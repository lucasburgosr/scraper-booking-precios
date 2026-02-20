
import os
import sys

proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_dir)

from utils.dependencias import destinos, inicializar_driver, parsear_a_float, parsear_impuestos
from models.precios_reserva import PrecioReserva
from models.alojamiento import Alojamiento
from models.metricas_alojamiento import MetricasAlojamiento  # requerido por SQLAlchemy para resolver relaciones
from config.settings import RESERVATION_DATE
from config.dbconfig import get_db, Base, engine
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import logging
import time
import traceback
from datetime import date

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def scroll_de_carga(driver):
    wait = WebDriverWait(driver, 10)

    try:
        popup_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label='Ignorar información sobre el inicio de sesión.']"))
        )
        popup_btn.click()
        logger.info("Login popup closed.")
    except TimeoutException:
        pass
    except Exception as e:
        logger.debug(f"Popup check exception: {e}")

    prev_height = 0
    iteration = 0

    while True:
        iteration += 1
        try:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            try:
                load_more_btn = driver.find_element(
                    By.XPATH, "//button[span[contains(text(), 'Cargar más resultados')]]")
                if load_more_btn.is_displayed():
                    driver.execute_script(
                        "arguments[0].scrollIntoView();", load_more_btn)
                    load_more_btn.click()
                    logger.info("Clicked 'Load more results' button.")
                    time.sleep(3)
            except NoSuchElementException:
                pass

            new_height = driver.execute_script(
                "return document.body.scrollHeight")

            if new_height == prev_height:
                break
            prev_height = new_height

        except Exception as e:
            logger.error(f"Error durante el scroll: {e}")
            break


def extraer_datos_alojamiento(element):
    data = {
        "nombre": "Desconocido",
        "ubicacion": "Desconocido",
        "precio": 0.0,
        "impuestos": 0.0,
        "tipo": "Sin clasificar",
        "puntuacion": 0.0,
        "link": ""
    }

    try:
        data["nombre"] = element.find_element(
            By.CSS_SELECTOR, "div[data-testid='title']").text
        data["link"] = element.find_element(
            By.CSS_SELECTOR, "a[data-testid='title-link']").get_attribute("href")

        try:
            data["ubicacion"] = element.find_element(
                By.CSS_SELECTOR, "span[data-testid='address']").text
        except NoSuchElementException:
            pass

        try:
            price_str = element.find_element(
                By.CSS_SELECTOR, "span[data-testid='price-and-discounted-price']").text
            data["precio"] = parsear_a_float(price_str)
        except NoSuchElementException:
            pass

        try:
            taxes_str = element.find_element(
                By.CSS_SELECTOR, "div[data-testid='taxes-and-charges']").text
            data["impuestos"] = parsear_impuestos(taxes_str)
        except NoSuchElementException:
            pass

        try:
            data["tipo"] = element.find_element(By.TAG_NAME, "h4").text
        except NoSuchElementException:
            pass
        try:
            score_str = element.find_element(
                By.CSS_SELECTOR, "div[data-testid='review-score']").text
            lines = score_str.split("\n")
            if len(lines) > 1:
                score_val = lines[1].replace(",", ".")
                data["puntuacion"] = float(score_val)
        except (NoSuchElementException, IndexError, ValueError):
            pass

    except Exception as e:
        logger.warning(f"Error al extraer datos de un alojamiento: {e}")
        return None

    return data


def guardar_alojamiento(session, data, destino):
    try:
        alojamiento = session.query(Alojamiento).filter(
            Alojamiento.nombre == data["nombre"],
            Alojamiento.destino == destino
        ).first()

        if not alojamiento:
            alojamiento = Alojamiento(
                destino=destino,
                nombre=data["nombre"],
                ubicacion=data["ubicacion"],
                tipo_alojamiento=data["tipo"],
                link=data["link"]
            )
            session.add(alojamiento)
            session.flush()  # flush para obtener el ID
        else:
            if alojamiento.link != data["link"]:
                alojamiento.link = data["link"]

        nuevo_precio = PrecioReserva(
            id_alojamiento=alojamiento.id,
            fecha_registro=date.today(),
            fecha_reserva=RESERVATION_DATE,
            precio_en_dolares=data["precio"],
            impuestos_en_dolares=data["impuestos"] or 0.0
        )
        session.add(nuevo_precio)
        session.commit()
        # logger.info(f"Guardado: {data['nombre']}")
        return True

    except Exception as e:
        session.rollback()
        logger.error(f"Error al guardar {data['nombre']}: {e}")
        return False


def procesar_destino(driver, session, destino, url):
    logger.info(f"Procesando destino: {destino}")
    try:
        driver.get(url)
        scroll_de_carga(driver)

        driver.execute_script("window.scrollTo(0, 0)")

        cards = driver.find_elements(
            By.CSS_SELECTOR, "div[data-testid='property-card-container']")
        count = len(cards)
        logger.info(f"Encontrados {count} alojamientos para {destino}")

        saved_count = 0
        for card in cards:
            data = extraer_datos_alojamiento(card)
            if data and guardar_alojamiento(session, data, destino):
                saved_count += 1

        logger.info(
            f"Guardados {saved_count}/{count} alojamientos para {destino}")

    except Exception as e:
        logger.error(f"Error al procesar {destino}: {e}")
        traceback.print_exc()


def main():
    logger.info("Iniciando Scraper de Booking")

    Base.metadata.create_all(engine)

    driver = None
    try:
        driver = inicializar_driver()

        db_gen = get_db()
        session = next(db_gen)

        try:
            for destino, url in destinos.items():
                procesar_destino(driver, session, destino, url)
                time.sleep(2)

        finally:
            
            next(db_gen, None)

    except Exception as e:
        logger.critical(f"Error crítico en la ejecución: {e}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
        logger.info("Scraper finalizado.")


if __name__ == "__main__":
    main()
