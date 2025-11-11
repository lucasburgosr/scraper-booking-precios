import traceback, os, sys, subprocess, locale
proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_dir)
from utils.dependencias import inicializar_driver, parsear_a_float
from config.dbconfig import session
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from models.metricas_alojamiento import MetricasAlojamiento
from models.precios_reserva import PrecioReserva
from models.alojamiento import Alojamiento

os.system("rm -f /tmp/.X99-lock")

xvfb_process = subprocess.Popen(
    ["Xvfb", ":99", "-screen", "0", "1366x768x24", "-ac"])
os.environ["DISPLAY"] = ":99"

locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')


def traer_ids_pendientes(session):
    q = (
        session.query(Alojamiento.id, Alojamiento.link)
        .outerjoin(MetricasAlojamiento, Alojamiento.id == MetricasAlojamiento.id_alojamiento)
        .filter(MetricasAlojamiento.id_alojamiento.is_(None))
        .order_by(Alojamiento.id.asc())
        .execution_options(stream_results=True)
        .yield_per(2000)
    )
    for (aloj_id, link) in q:
        yield aloj_id, link

def scrapear_y_procesar_datos(wait, id_alojamiento):
    try:
        puntuacion_string = wait.until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[1]/div[1]/div[4]/div/div[1]/div[1]/div/div[1]/a/div/div/div/div[1]"))).text
        puntuacion_con_punto = puntuacion_string.split()[1]
        print(f"Puntuacíon: {puntuacion_con_punto}")
        puntuacion = parsear_a_float(puntuacion_con_punto)
    except:
        puntuacion = 0

    try:
        personal = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[1]/div/div/div[1]/div[2]/div"))).text
        print(f"Personal: {personal}")
    except:
        personal = None

    try:
        instalaciones_y_servicios = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[2]/div/div/div[1]/div[2]/div"))).text
        print(f"Instalaciones: {instalaciones_y_servicios}")
    except:
        instalaciones_y_servicios = None

    try:
        limpieza = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[3]/div/div/div[1]/div[2]/div"))).text
        print(f"Limpieza: {limpieza}")
    except:
        limpieza = None

    try:
        confort = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[4]/div/div/div[1]/div[2]/div"))).text
        print(f"Confort: {confort}")
    except:
        confort = None

    try:
        relacion_calidad_precio = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[5]/div/div/div[1]/div[2]/div"))).text
        print(f"Relación calidad - precio: {relacion_calidad_precio}")
    except:
        relacion_calidad_precio = None

    try:
        ubicacion = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[3]/div/div[3]/div/div[2]/div[6]/div/div/div[1]/div[2]/div"))).text
        print(f"Ubicacion: {ubicacion}")
    except:
        ubicacion = None
    try:
        coordenadas = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "a[id='map_trigger_header']"))).get_attribute("data-atlas-latlng")
        print(f"Coordenadas: {coordenadas}")
    except:
        coordenadas = None

    try:
        string_comentarios = wait.until(EC.presence_of_element_located(
            (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[7]/div/div/div[2]/div/div[2]/div/button/div/div/div[4]/span[2]"))).text
        cantidad_comentarios = string_comentarios.split()[1]
        print(f"Cantidad de comentarios: {cantidad_comentarios}")
    except:
        cantidad_comentarios = None
    try:
        button_calificacion = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'button[data-testid="quality-rating"]')))
        contenedor_calificacion = button_calificacion.find_element(
            By.TAG_NAME, "span")
        calificacion = contenedor_calificacion.find_elements(
            By.CSS_SELECTOR, "div")
        estrellas = len(calificacion)
        print(f"Estrellas: {len(calificacion)}")
    except Exception as e:
        estrellas = None

    nuevo_data_alojamiento = MetricasAlojamiento(
        id_alojamiento=id_alojamiento,
        puntuacion=float(puntuacion) if puntuacion else 0,
        personal=personal if personal else None,
        instalaciones_y_servicios=instalaciones_y_servicios if instalaciones_y_servicios else None,
        limpieza=limpieza if limpieza else None,
        confort=confort if confort else None,
        relacion_calidad_precio=relacion_calidad_precio if relacion_calidad_precio else None,
        ubicacion=ubicacion if ubicacion else None,
        estrellas=estrellas if estrellas else None,
        coordenadas=coordenadas if coordenadas else None,
        cantidad_comentarios=cantidad_comentarios if cantidad_comentarios else 0
    )

    return nuevo_data_alojamiento

def guardar_metricas(data_list):
    try:
        session.add_all(data_list)
        session.commit()
        session.expunge_all()
        print(f"Guardado exitosamente {len(data_list)} registros")
    except:
        session.rollback()
        traceback.print_exc()
    

def obtener_metricas_alojamiento():
    buffer_pares = []
    objs_para_guardar = []

    for aloj_id, link in traer_ids_pendientes(session):
        buffer_pares.append((aloj_id, link))

        if len(buffer_pares) >= 50:
            driver = inicializar_driver()
            wait = WebDriverWait(driver, 15)
            try:
                objs_para_guardar.clear()

                for id_, url in buffer_pares:
                    try:
                        if not url:
                            print(f"[WARN] Alojamiento {id_} sin link; salto.")
                            continue
                        driver.get("about:blank")
                        driver.get(url)

                        obj = scrapear_y_procesar_datos(wait=wait, id_alojamiento=id_)
                        objs_para_guardar.append(obj)

                    except Exception:
                        print(f"[ERROR] Alojamiento {id_} no almacenado")
                        traceback.print_exc()
                        continue

                if objs_para_guardar:
                    guardar_metricas(objs_para_guardar)

            finally:
                try: driver.quit()
                except: pass

            buffer_pares.clear()

    # Procesa el último lote si quedaron pendientes
    if buffer_pares:
        driver = inicializar_driver()
        wait = WebDriverWait(driver, 15)
        try:
            objs_para_guardar.clear()

            for id_, url in buffer_pares:
                try:
                    if not url:
                        print(f"[WARN] Alojamiento {id_} sin link; salto.")
                        continue
                    driver.get("about:blank")
                    driver.get(url)

                    obj = scrapear_y_procesar_datos(wait=wait, id_alojamiento=id_)
                    objs_para_guardar.append(obj)

                except Exception:
                    print(f"[ERROR] Alojamiento {id_} no almacenado")
                    traceback.print_exc()
                    continue

            if objs_para_guardar:
                guardar_metricas(objs_para_guardar)

        finally:
            try: driver.quit()
            except: pass

try:
    obtener_metricas_alojamiento()
finally:
    pass
