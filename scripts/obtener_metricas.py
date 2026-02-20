import os
import sys
proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_dir)
import re
import time
import logging
from models.alojamiento import Alojamiento
# requerido por SQLAlchemy para resolver relaciones
from models.precios_reserva import PrecioReserva
from models.metricas_alojamiento import MetricasAlojamiento
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from config.dbconfig import get_db, Base, engine
from utils.dependencias import inicializar_driver, parsear_a_float
import traceback

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def traer_ids_pendientes(session):
    """Buscar ID's de alojamientos que no tienen métricas."""
    q = (
        session.query(Alojamiento.id, Alojamiento.link)
        .outerjoin(MetricasAlojamiento, Alojamiento.id == MetricasAlojamiento.id_alojamiento)
        .filter(MetricasAlojamiento.id_alojamiento.is_(None))
        .order_by(Alojamiento.id.desc())
        .execution_options(stream_results=True)
        .yield_per(2000)
    )
    for (aloj_id, link) in q:
        yield aloj_id, link


def scrapear_y_procesar_datos(driver, id_alojamiento):
    """Scrapear métricas de una sola página de propiedad de forma optimizada y rápida."""
    # Espera rápida para asegurar que cargó lo básico (ej. el título)
    wait_corto = WebDriverWait(driver, 3)
    try:
        wait_corto.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "h2.pp-header__title")))
    except Exception:
        pass  # Si falla, intentamos los selectores igual porque driver tiene implicit wait

    try:
        # 1. PUNTUACIÓN GENERAL
        try:
            puntuacion_string = driver.find_element(
                By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[1]/div[1]/div[4]/div/div[1]/div[1]/div/div[1]/a/div/div/div/div[1]"
            ).text
            puntuacion_val = puntuacion_string.split()[1]
            puntuacion = parsear_a_float(puntuacion_val)
        except Exception:
            # Fallback con selectores CSS comunes de Booking
            try:
                score_str = driver.find_element(
                    By.CSS_SELECTOR, "div[data-testid='review-score-right-component']").text
                puntuacion = parsear_a_float(
                    score_str.split()[0].replace(',', '.'))
            except:
                puntuacion = 0.0

        # 2. SUB-MÉTRICAS (Personal, Instalaciones, Limpieza, etc.)
        metricas = {}
        mapeo = {
            "personal": "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[1]/div/div/div[1]/div[2]/div",
            "instalaciones": "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[2]/div/div/div[1]/div[2]/div",
            "limpieza": "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[3]/div/div/div[1]/div[2]/div",
            "confort": "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[4]/div/div/div[1]/div[2]/div",
            "calidad_precio": "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[5]/div/div/div[1]/div[2]/div",
            "ubicacion_score": "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[6]/div/div/div[1]/div[2]/div"
        }

        # Intento rápido sin esperar 15 segundos
        for clave, xpath in mapeo.items():
            try:
                metricas[clave] = driver.find_element(By.XPATH, xpath).text
            except Exception:
                metricas[clave] = None

        # Si todas fallaron (porque la página cambió su estructura HTML), usamos búsqueda agnóstica de estructura
        if not any(metricas.values()):
            try:
                subscores = driver.find_elements(
                    By.CSS_SELECTOR, "div[data-testid='review-subscore']")
                for sub in subscores:
                    text_str = sub.text.lower()
                    if not text_str:
                        continue
                    val = sub.find_element(By.CSS_SELECTOR, "div.bui-review-score__badge").text if "bui-" in sub.get_attribute(
                        "innerHTML") else sub.text.split('\n')[-1]

                    match = re.search(r'(\d+[,.]\d+)', val)
                    val_str = match.group(1) if match else None
                    if not val_str:
                        continue

                    if "personal" in text_str:
                        metricas["personal"] = val_str
                    elif "instalacion" in text_str:
                        metricas["instalaciones"] = val_str
                    elif "limpieza" in text_str:
                        metricas["limpieza"] = val_str
                    elif "confort" in text_str:
                        metricas["confort"] = val_str
                    elif "calidad" in text_str or "precio" in text_str:
                        metricas["calidad_precio"] = val_str
                    elif "ubicaci" in text_str:
                        metricas["ubicacion_score"] = val_str
            except Exception:
                pass

        # 3. COORDENADAS
        try:
            coordenadas = driver.find_element(
                By.CSS_SELECTOR, "a[id='map_trigger_header']").get_attribute("data-atlas-latlng")
        except Exception:
            coordenadas = None

        # 4. CANTIDAD DE COMENTARIOS
        try:
            string_comentarios = driver.find_element(
                By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[2]/div/div[2]/div/button/div/div/div[4]/span[2]").text
            cantidad_comentarios = int(
                string_comentarios.split()[1].replace(".", ""))
        except Exception:
            try:
                coms_elems = driver.find_elements(
                    By.XPATH, "//*[contains(text(), 'comentarios') or contains(text(), 'opiniones')]")
                match_val = None
                for el in coms_elems:
                    m = re.search(
                        r'([\d.,]+)\s+(comentarios|opiniones)', el.text, re.IGNORECASE)
                    if m:
                        match_val = m.group(1).replace(
                            ".", "").replace(",", "")
                        break
                cantidad_comentarios = int(match_val) if match_val else 0
            except:
                cantidad_comentarios = 0

        # 5. ESTRELLAS (Categoría del Alojamiento)
        try:
            button_calificacion = driver.find_element(
                By.CSS_SELECTOR, 'button[data-testid="quality-rating"]')
            calificacion = button_calificacion.find_element(
                By.TAG_NAME, "span").find_elements(By.CSS_SELECTOR, "div")
            estrellas = len(calificacion)
        except Exception:
            estrellas = None

        return MetricasAlojamiento(
            id_alojamiento=id_alojamiento,
            puntuacion=puntuacion,
            personal=metricas.get("personal"),
            instalaciones_y_servicios=metricas.get("instalaciones"),
            limpieza=metricas.get("limpieza"),
            confort=metricas.get("confort"),
            relacion_calidad_precio=metricas.get("calidad_precio"),
            ubicacion=metricas.get("ubicacion_score"),
            estrellas=estrellas,
            coordenadas=coordenadas,
            cantidad_comentarios=cantidad_comentarios
        )
    except Exception as e:
        logger.warning(
            f"Error general extrayendo métricas_alojamiento={id_alojamiento}: {e}")
        return None


def guardar_metricas(session, data_list):
    """Guardar métricas en la base de datos."""
    session.add_all(data_list)
    session.commit()
    session.expunge_all()
    logger.info(f"Guardado exitosamente {len(data_list)} registros")


def procesar_lote(lote, session):
    """Procesar lote de propiedades."""
    driver = inicializar_driver()
    # Implicit wait bajo. Hacemos que si un elemento no está, falle en máximo 0.5s.
    driver.implicitly_wait(0.5)
    objs_para_guardar = []

    try:
        for id_, url in lote:
            try:
                if not url:
                    logger.warning(f"Alojamiento {id_} sin link; omitiendo.")
                    continue

                # Omitir parámetros URL que puedan generar redirecciones por caducidad
                url_limpia = url.split("?")[0]

                driver.get("about:blank")
                driver.get(url_limpia)

                # Checkear si fuimos redirigidos fuera de la página individual del hotel
                time.sleep(1.5)
                if "searchresults" in driver.current_url:
                    logger.warning(
                        f"Alojamiento {id_} redirigido al listado (hotel inactivo/cerrado). Omitiendo métricas.")
                    obj = MetricasAlojamiento(
                        id_alojamiento=id_,
                        puntuacion=0.0,
                        cantidad_comentarios=0
                    )
                    objs_para_guardar.append(obj)
                    continue

                obj = scrapear_y_procesar_datos(driver, id_)
                if obj:
                    objs_para_guardar.append(obj)
            except Exception as e:
                logger.error(f"Error al procesar alojamiento {id_}: {e}")
                continue

        # Maximum number of retries for Database commits
        MAX_RETRIES = 3
        RETRY_DELAY = 5

        if objs_para_guardar:
            for attempt in range(MAX_RETRIES):
                try:
                    guardar_metricas(session, objs_para_guardar)
                    break  # Success!
                except Exception as db_err:
                    logger.warning(
                        f"Error guardando lote (Intento {attempt + 1}/{MAX_RETRIES}): {db_err}")
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(RETRY_DELAY)
                        # Intenta hacer rollback por si la transacción quedó sucia
                        try:
                            session.rollback()
                        except:
                            pass
                    else:
                        logger.error(
                            f"Fallo definitivo al guardar lote tras {MAX_RETRIES} intentos.")

    finally:
        driver.quit()


def main():
    logger.info("Iniciando obtención de métricas de alojamiento agilizada")

    Base.metadata.create_all(engine)

    db_gen = get_db()
    session = next(db_gen)

    try:
        lote_actual = []
        lote_size = 20

        for id_aloj, link in traer_ids_pendientes(session):
            lote_actual.append((id_aloj, link))

            if len(lote_actual) >= lote_size:
                logger.info(f"Procesando lote de {lote_size} alojamientos...")
                procesar_lote(lote_actual, session)
                lote_actual.clear()

        # Procesar remanente
        if lote_actual:
            logger.info(
                f"Procesando último lote de {len(lote_actual)} alojamientos...")
            procesar_lote(lote_actual, session)

    except Exception as e:
        logger.critical(f"Error crítico en la ejecución: {e}")
        traceback.print_exc()
    finally:
        next(db_gen, None)
        logger.info("Proceso de métricas finalizado.")


if __name__ == "__main__":
    main()
