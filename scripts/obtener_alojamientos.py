from datetime import date, timedelta
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from contextlib import suppress
import traceback, time, locale, os, sys, subprocess

proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_dir)

from utils.dependencias import inicializar_driver, parsear_a_float
from utils.dependencias import destinos, fecha_reserva
from models.precios_reserva import PrecioReserva
from models.alojamiento import Alojamiento
from models.metricas_alojamiento import MetricasAlojamiento
from config.dbconfig import Base, engine, session

os.system("rm -f /tmp/.X99-lock")

xvfb_process = subprocess.Popen(
    ["Xvfb", ":99", "-screen", "0", "1366x768x24", "-ac"])
os.environ["DISPLAY"] = ":99"

locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

def parsear_impuestos(num_string: str):
    num_corregido = None
    if ("+ US$" in num_string and "de impuestos y cargos" in num_string):
        num_sin_signos = num_string.replace(
            "+ US$", "").replace("de impuestos y cargos", "").strip()
        num_corregido = num_sin_signos.replace(".", "").replace(",", ".")
    elif "Incluye impuestos y cargos" in num_string:
        return None

    if num_corregido is None:
        return 0

    return float(num_corregido)


def cargar_todos_los_alojamientos(driver, link):
    driver.get(link)
    wait = WebDriverWait(driver, 15)
    height_previo = 0
    while True:
        try:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);")
        except TimeoutException:
            print("Se agotó el tiempo al hacer scroll")
            break

        time.sleep(2)

        try:
            boton_cargar_mas = wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 "//button[span[contains(text(), 'Cargar más resultados')]]")
            ))
            if boton_cargar_mas.is_displayed():
                driver.execute_script(
                    "arguments[0].scrollIntoView();", boton_cargar_mas)
                boton_cargar_mas.click()
                print("Se hizo click en el botón 'Cargar más resultados'")
                time.sleep(2)
        except:
            pass

        try:
            nuevo_height = driver.execute_script(
                "return document.body.scrollHeight")
        except TimeoutException:
            print("Timeout al obtener scrollHeight, finalizando scroll")
            break

        if nuevo_height == height_previo:
            break
        height_previo = nuevo_height


def obtener_alojamientos(driver, destino, fecha_reserva):
    wait = WebDriverWait(driver, 15)
    driver.execute_script("window.scrollTo(0, 0)")
    alojamientos = driver.find_elements(
        By.CSS_SELECTOR, "div[data-testid='property-card-container']")

    for alojamiento in alojamientos:
        try:
            nombre = alojamiento.find_element(
                By.CSS_SELECTOR, "div[data-testid='title']").text
            ubicacion = alojamiento.find_element(
                By.CSS_SELECTOR, "span[data-testid='address']").text

            try:
                precio_string = alojamiento.find_element(
                    By.CSS_SELECTOR, "span[data-testid='price-and-discounted-price']").text
                precio = parsear_a_float(precio_string)
                impuestos_string = alojamiento.find_element(
                    By.CSS_SELECTOR, "div[data-testid='taxes-and-charges']").text
                impuestos = parsear_impuestos(impuestos_string)
            except:
                precio = 0
                impuestos = 0

            try:
                tipo_alojamiento = alojamiento.find_element(
                    By.TAG_NAME, "h4").text
            except:
                tipo_alojamiento = "Sin clasificar"

            try:
                puntuacion_string = alojamiento.find_element(
                    By.CSS_SELECTOR, "div[data-testid='review-score']").text
                lineas = puntuacion_string.split("\n")
                linea = lineas[1]
                puntuacion_con_punto = linea.replace(",", ".")
                puntuacion = float(puntuacion_con_punto)
            except Exception:
                puntuacion = 0

            link = alojamiento.find_element(
                By.CSS_SELECTOR, "a[data-testid='title-link']").get_attribute("href")

            alojamiento_guardado = session.query(Alojamiento).filter(
                Alojamiento.nombre == nombre, Alojamiento.destino == destino).first()

            if alojamiento_guardado is None:
                alojamiento_obj = Alojamiento(
                    destino=destino,
                    nombre=nombre,
                    ubicacion=ubicacion,
                    tipo_alojamiento=tipo_alojamiento,
                    link=link
                )
            else:
                alojamiento_guardado.link = link
                alojamiento_obj = alojamiento_guardado

            session.add(alojamiento_obj)    
            session.flush()

            nuevo_precio = PrecioReserva(
                id_alojamiento=alojamiento_obj.id,
                fecha_registro=date.today(),
                fecha_reserva=fecha_reserva,
                precio_en_dolares=precio,
                impuestos_en_dolares=impuestos
            )
            session.add(nuevo_precio)

            try:
                session.commit()
                print("Guardado exitosamente")
            except Exception as e:
                session.rollback()
                print("Error al guardar: ", e)

        except NoSuchElementException as e:
            print("Error al obtener datos del alojamiento")
            continue


Base.metadata.create_all(engine)

for destino, link in destinos.items():
    print(f"== Procesando destino {destino} ==")
    driver = None
    try:
        driver = inicializar_driver()
        cargar_todos_los_alojamientos(driver=driver, link=link)
        obtener_alojamientos(
            driver=driver,
            destino=destino,
            fecha_reserva=fecha_reserva,
        )
        print(f"El ID de esta sesión es: {driver.session_id}")
    except Exception as e:
        print(f"Error al procesar el destino {destino}: {e!r}")
        traceback.print_exc()
    finally:
        if driver is not None:
            with suppress(Exception):
                driver.quit()
        time.sleep(2)


xvfb_process.terminate()

