
import os
import sys

# Add project root to path
proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_dir)

from utils.dependencias import destinos, inicializar_driver, parsear_a_float, parsear_impuestos
from models.precios_reserva import PrecioReserva
from models.alojamiento import Alojamiento
from models.metricas_alojamiento import MetricasAlojamiento  # noqa: F401 - requerido por SQLAlchemy para resolver relaciones
from config.settings import RESERVATION_DATE
from config.dbconfig import get_db, Base, engine
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import logging
import time
import traceback
from datetime import date
from contextlib import contextmanager

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def scroll_to_load_all(driver):
    wait = WebDriverWait(driver, 10)

    # Try to close popup if it appears
    try:
        popup_btn = wait.until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[aria-label='Ignorar información sobre el inicio de sesión.']"))
        )
        popup_btn.click()
        logger.info("Login popup closed.")
    except TimeoutException:
        pass  # Popup didn't appear, normal behavior
    except Exception as e:
        logger.debug(f"Popup check exception: {e}")

    prev_height = 0
    iteration = 0

    while True:
        iteration += 1
        try:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Give time for content to load

            # Click "Load more" if available
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
            # logger.debug(f"Scroll {iteration}: prev_height={prev_height}, new_height={new_height}")

            if new_height == prev_height:
                break
            prev_height = new_height

        except Exception as e:
            logger.error(f"Error during scrolling: {e}")
            break


def extract_alojamiento_data(element):
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

        # Ubicación (opcional, el selector puede cambiar)
        try:
            data["ubicacion"] = element.find_element(
                By.CSS_SELECTOR, "span[data-testid='address']").text
        except NoSuchElementException:
            pass

        # Price
        try:
            price_str = element.find_element(
                By.CSS_SELECTOR, "span[data-testid='price-and-discounted-price']").text
            data["precio"] = parsear_a_float(price_str)
        except NoSuchElementException:
            pass

        # Taxes
        try:
            taxes_str = element.find_element(
                By.CSS_SELECTOR, "div[data-testid='taxes-and-charges']").text
            data["impuestos"] = parsear_impuestos(taxes_str)
        except NoSuchElementException:
            pass

        # Type
        try:
            data["tipo"] = element.find_element(By.TAG_NAME, "h4").text
        except NoSuchElementException:
            pass

        # Score
        try:
            score_str = element.find_element(
                By.CSS_SELECTOR, "div[data-testid='review-score']").text
            # Format usually: "Puntuación\n8,5\n..."
            lines = score_str.split("\n")
            if len(lines) > 1:
                score_val = lines[1].replace(",", ".")
                data["puntuacion"] = float(score_val)
        except (NoSuchElementException, IndexError, ValueError):
            pass

    except Exception as e:
        logger.warning(f"Error extracting data for an element: {e}")
        return None

    return data


def save_alojamiento(session, data, destino):
    try:
        # Check if exists
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
            session.flush()  # flush to get ID
        else:
            # Update link if changed
            if alojamiento.link != data["link"]:
                alojamiento.link = data["link"]

        # Add price record
        nuevo_precio = PrecioReserva(
            id_alojamiento=alojamiento.id,
            fecha_registro=date.today(),
            fecha_reserva=RESERVATION_DATE,
            precio_en_dolares=data["precio"],
            impuestos_en_dolares=data["impuestos"] or 0.0  # Ensure not None
        )
        session.add(nuevo_precio)
        session.commit()
        # logger.info(f"Saved: {data['nombre']}")
        return True

    except Exception as e:
        session.rollback()
        logger.error(f"Database error saving {data['nombre']}: {e}")
        return False


def procesar_destino(driver, session, destino, url):
    logger.info(f"Processing destination: {destino}")
    try:
        driver.get(url)
        scroll_to_load_all(driver)

        driver.execute_script("window.scrollTo(0, 0)")  # Go back to top

        cards = driver.find_elements(
            By.CSS_SELECTOR, "div[data-testid='property-card-container']")
        count = len(cards)
        logger.info(f"Found {count} properties for {destino}")

        saved_count = 0
        for card in cards:
            data = extract_alojamiento_data(card)
            if data and save_alojamiento(session, data, destino):
                saved_count += 1

        logger.info(
            f"Successfully saved {saved_count}/{count} properties for {destino}")

    except Exception as e:
        logger.error(f"Error processing {destino}: {e}")
        traceback.print_exc()


def main():
    logger.info("Starting Booking Scraper")

    # Ensure tables exist
    Base.metadata.create_all(engine)

    driver = None
    try:
        driver = inicializar_driver()

        # Use a single session for the whole run or per destination?
        # Per destination is safer context-wise but single is fine for this script.
        # Let's use the generator from dbconfig
        db_gen = get_db()
        session = next(db_gen)

        try:
            for destino, url in destinos.items():
                procesar_destino(driver, session, destino, url)
                time.sleep(2)  # Brief pause between destinations

        finally:
            # Clean up session (it closes in finally block of generator)
            next(db_gen, None)

    except Exception as e:
        logger.critical(f"Critical error in main execution: {e}")
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
        logger.info("Scraper finished.")


if __name__ == "__main__":
    main()
