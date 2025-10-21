import os
import sys
proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_dir)

import traceback
import subprocess
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from datetime import date, timedelta
import time
import locale
from config.dbconfig import Base, engine, session
from models.alojamiento import Alojamiento
from models.metricas_alojamiento import MetricasAlojamiento
from models.precios_reserva import PrecioReserva

os.system("rm -f /tmp/.X99-lock")

xvfb_process = subprocess.Popen(
    ["Xvfb", ":99", "-screen", "0", "1366x768x24", "-ac"])
os.environ["DISPLAY"] = ":99"

options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1366,768")
options.add_argument("--process-per-site")
options.add_argument("--disable-gpu")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-backgrounding-occluded-windows")
options.add_argument("--disable-renderer-backgrounding")
options.add_argument("--disable-extensions")
options.add_argument("--disable-infobars")
options.add_argument("--no-first-run")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-background-networking")
options.add_argument("--disable-default-apps")
options.add_argument("--disable-sync")
options.add_argument("--metrics-recording-only")
options.add_argument("--mute-audio")
options.add_argument("--no-zygote")
options.add_argument("--disable-software-rasterizer")

prefs = {
    "profile.managed_default_content_settings.images": 2,
    "profile.default_content_setting_values.notifications": 2,
    "profile.default_content_setting_values.geolocation": 2,
    "profile.default_content_setting_values.sound": 2,
}
options.add_experimental_option("prefs", prefs)

locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')

driver = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=options)

driver.set_page_load_timeout(90)
driver.set_script_timeout(60)

wait = WebDriverWait(driver, 15)

driver.execute_cdp_cmd("Network.enable", {})
driver.execute_cdp_cmd("Network.setBlockedURLs", {
    "urls": [
        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp",
        "*.svg", "*.mp4", "*.webm", "*.avi", "*.mov",
        "*.woff", "*.woff2", "*.ttf", "*.otf"
    ]
})

# fecha = date.today()
fecha_reserva = date(2025, 11, 15)
fecha_checkin = fecha_reserva.strftime("%Y-%m-%d")
fecha_checkout = (fecha_reserva + timedelta(days=1)).strftime("%Y-%m-%d")

destinos = {
    # "Mendoza": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Mendoza&ssne=Provincia+de+Mendoza&ssne_untouched=Provincia+de+Mendoza&label=gen173nr-1BCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQGIAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIF4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=597&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Buenos Aires": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Buenos+Aires&ssne=Provincia+de+Buenos+Aires&ssne_untouched=Provincia+de+Buenos+Aires&label=gen173nr-1BCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQzYAQHoAQGIAgGoAgO4As24scEGwAIB0gIkMjI2YjA4N2MtM2MyOS00YmM5LTlkYjItOWYzN2Y0OWJkZjY32AIF4AIB&sid=d58cadffffeced965e517d550bbaef7a&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3619&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "CABA": f"https://www.booking.com/searchresults.es.html?ss=Buenos+Aires%2C+Argentina&label=gen173nr-1BCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQGIAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIF4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=-979186&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=6d714bad82ea0156&ac_meta=GhA2ZDcxNGJhZDgyZWEwMTU2IAAoATICZXM6CUNpdWRhZCBhdUAASgBQAA%3D%3D&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Córdoba": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+C%C3%B3rdoba%2C+Argentina&ssne=C%C3%B3rdoba&ssne_untouched=C%C3%B3rdoba&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=d58cadffffeced965e517d550bbaef7a&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=1342&dest_type=region&ac_position=2&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=33464bddd7f40901&ac_meta=GhAzMzQ2NGJkZGQ3ZjQwOTAxIAIoATICZXM6FVByb3ZpbmNpYSBkZSBDw7NyZG9iYUAASgBQAA%3D%3D&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Santa Fe": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Santa+Fe&ssne=Provincia+de+Santa+Fe&ssne_untouched=Provincia+de+Santa+Fe&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3628&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Neuquén": f"https://www.booking.com/searchresults.es.html?ss=Neuqu%C3%A9n+Province%2C+Argentina&ssne=Provincia+de+Santa+Fe&ssne_untouched=Provincia+de+Santa+Fe&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=searchresults&dest_id=3627&dest_type=region&ac_position=2&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=6f6c4c269cd101aa&ac_meta=GhA2ZjZjNGMyNjljZDEwMWFhIAIoATICZXM6CE5ldXF1w6luQABKAFAA&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Salta": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Salta%2C+Argentina&ssne=Salta&ssne_untouched=Salta&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=599&dest_type=region&ac_position=1&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=9a3a4c9baf610170&ac_meta=GhA5YTNhNGM5YmFmNjEwMTcwIAEoATICZXM6ElByb3ZpbmNpYSBkZSBTYWx0YUAASgBQAA%3D%3D&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Jujuy": f"https://www.booking.com/searchresults.es.html?ss=Jujuy&ssne=Jujuy&ssne_untouched=Jujuy&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=596&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Tucumán": f"https://www.booking.com/searchresults.es.html?ss=Tucum%C3%A1n&ssne=Tucum%C3%A1n&ssne_untouched=Tucum%C3%A1n&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3629&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Formosa": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Formosa&ssne=Provincia+de+Formosa&ssne_untouched=Provincia+de+Formosa&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3624&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Santiago del Estero": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Santiago+del+Estero&ssne=Provincia+de+Santiago+del+Estero&ssne_untouched=Provincia+de+Santiago+del+Estero&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=602&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "La Rioja": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+La+Rioja%2C+Argentina&ssne=Provincia+de+Santiago+del+Estero&ssne_untouched=Provincia+de+Santiago+del+Estero&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3626&dest_type=region&ac_position=1&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=290b4ddeba5d0463&ac_meta=GhAyOTBiNGRkZWJhNWQwNDYzIAEoATICZXM6FVByb3ZpbmNpYSBkZSBMYSBSaW9qYUAASgBQAA%3D%3D&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "San Juan": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+San+Juan&ssne=Provincia+de+San+Juan&ssne_untouched=Provincia+de+San+Juan&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=600&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "San Luis": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+San+Luis&ssne=Provincia+de+San+Luis&ssne_untouched=Provincia+de+San+Luis&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=601&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "La Pampa": f"https://www.booking.com/searchresults.es.html?ss=La+Pampa&ssne=La+Pampa&ssne_untouched=La+Pampa&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3625&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Río Negro": f"https://www.booking.com/searchresults.es.html?ss=R%C3%ADo+Negro&ssne=R%C3%ADo+Negro&ssne_untouched=R%C3%ADo+Negro&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=598&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Santa Cruz": f"https://www.booking.com/searchresults.es.html?ss=Santa+Cruz&ssne=Santa+Cruz&ssne_untouched=Santa+Cruz&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=d58cadffffeced965e517d550bbaef7a&aid=304142&lang=es&sb=1&src_elem=sb&src=searchresults&dest_id=3618&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Catamarca": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Catamarca&ssne=Provincia+de+Catamarca&ssne_untouched=Provincia+de+Catamarca&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3620&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Misiones": f"https://www.booking.com/searchresults.es.html?ss=Misiones&ssne=Misiones&ssne_untouched=Misiones&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=1343&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Tierra del Fuego": f"https://www.booking.com/searchresults.es.html?ss=Tierra+del+Fuego&ssne=Tierra+del+Fuego&ssne_untouched=Tierra+del+Fuego&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=603&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Corrientes": f"https://www.booking.com/searchresults.es.html?ss=Provincia+de+Corrientes&ssne=Provincia+de+Corrientes&ssne_untouched=Provincia+de+Corrientes&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3623&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Entre Ríos": f"https://www.booking.com/searchresults.es.html?ss=Entre+R%C3%ADos&ssne=Entre+R%C3%ADos&ssne_untouched=Entre+R%C3%ADos&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=595&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Chaco": f"https://www.booking.com/searchresults.es.html?ss=Chaco&ssne=Chaco&ssne_untouched=Chaco&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3621&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    "Chubut": f"https://www.booking.com/searchresults.es.html?ss=Chubut&ssne=Chubut&ssne_untouched=Chubut&label=gen173nr-1FCAEoggI46AdIM1gEaAyIAQGYAQq4ARnIAQ_YAQHoAQH4AQ2IAgGoAgO4AvrbqMAGwAIB0gIkZTU5ZDk2ZmMtZjE2MC00YTY3LThmOTAtZjM5MzRkZDEzYzhi2AIG4AIB&sid=25354a0abd4c8b948d7d2e477a15e759&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=3622&dest_type=region&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD"
    # "Río de Janeiro": f"https://www.booking.com/searchresults.es.html?ss=R%C3%ADo+de+Janeiro%2C+R%C3%ADo+de+Janeiro%2C+Brasil&ssne=R%C3%ADo+de+Janeiro&ssne_untouched=R%C3%ADo+de+Janeiro&efdco=1&label=gen173nr-10CAEoggI46AdIM1gEaAyIAQGYATO4ARfIAQzYAQPoAQH4AQGIAgGoAgG4AuzZwsQGwAIB0gIkNTg3Yzk4NDktNTE1MS00ZTZiLWE0YzEtOWFhMzQ5ZWRlM2I52AIB4AIB&sid=07e0f29184142cdd408cfbc94b0bd0ae&aid=304142&lang=es&sb=1&src_elem=sb&src=searchresults&dest_id=-666610&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=2bf15a907e0f088c&ac_meta=GhAyYmYxNWE5MDdlMGYwODhjIAAoATICZXM6CFLDrW8gZGUgQABKAFAA&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD",
    # "Viña del Mar": f"https://www.booking.com/searchresults.es.html?ss=Vi%C3%B1a+del+Mar%2C+Valpara%C3%ADso+Region%2C+Chile&ssne=R%C3%ADo+de+Janeiro&ssne_untouched=R%C3%ADo+de+Janeiro&label=gen173nr-10CAEoggI46AdIM1gEaAyIAQGYATO4ARfIAQzYAQPoAQH4AQGIAgGoAgG4AuzZwsQGwAIB0gIkNTg3Yzk4NDktNTE1MS00ZTZiLWE0YzEtOWFhMzQ5ZWRlM2I52AIB4AIB&sid=dc1029d913a82d38c79bdb261886d12c&aid=304142&lang=es&sb=1&src_elem=sb&src=index&dest_id=-904540&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=es&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=6e7b5af4a3cc0d61&ac_meta=GhA2ZTdiNWFmNGEzY2MwZDYxIAAoATICZXM6BXZpw7FhQABKAFAA&checkin={fecha_checkin}&checkout={fecha_checkout}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD"
}


def parsear_a_float(num_string: str):
    if ("US$" in num_string):
        num_sin_signo = num_string.replace("US$", "").strip()
        num_corregido = num_sin_signo.replace(".", "").replace(",", ".")
    elif (num_string == ''):
        num_corregido = "0"
    else:
        num_corregido = num_string.replace(".", "").replace(",", ".")
    return float(num_corregido)


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

def cargar_todos_los_alojamientos(link):
    driver.get(link)
    height_previo = 0
    while True:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except TimeoutException:
            print("Se agotó el tiempo al hacer scroll")
            break

        time.sleep(2)

        try:
            boton_cargar_mas = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[span[contains(text(), 'Cargar más resultados')]]")
            ))
            if boton_cargar_mas.is_displayed():
                driver.execute_script("arguments[0].scrollIntoView();", boton_cargar_mas)
                boton_cargar_mas.click()
                print("Se hizo click en el botón 'Cargar más resultados'")
                time.sleep(2)
        except:
            pass

        try:
            nuevo_height = driver.execute_script("return document.body.scrollHeight")
        except TimeoutException:
            print("Timeout al obtener scrollHeight, finalizando scroll")
            break

        if nuevo_height == height_previo:
            break
        height_previo = nuevo_height


def obtener_alojamientos(destino, driver, fecha_reserva):

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
            except NoSuchElementException:
                puntuacion = 0

            link = alojamiento.find_element(
                By.CSS_SELECTOR, "a[data-testid='title-link']").get_attribute("href")

            alojamiento_guardado = session.query(Alojamiento).filter(
                Alojamiento.nombre == nombre).first()

            if alojamiento_guardado is None:
                alojamiento_obj = Alojamiento(
                    destino=destino,
                    nombre=nombre,
                    ubicacion=ubicacion,
                    tipo_alojamiento=tipo_alojamiento,
                    link=link
                )
                session.add(alojamiento_obj)
                session.flush()  # Fuerza que se genere el ID para usarlo enseguida
            else:
                alojamiento_guardado.fecha_registro = date.today()
                alojamiento_guardado.fecha_reserva = alojamiento_guardado.fecha_registro + \
                    timedelta(15)
                alojamiento_guardado.puntuacion = puntuacion
                alojamiento_guardado.link = link
                alojamiento_obj = alojamiento_guardado  # Unificamos referencia

            # Ahora que tenemos el alojamiento_obj, agregamos PrecioReserva
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


# Entramos al link de cada alojamiento y obtenemos algunas métricas (estrellas, puntajes por categoría)
# def obtener_metricas_alojamiento(driver):

#     alojamientos = session.query(Alojamiento).filter(Alojamiento.id > 7816).all()

#     for alojamiento in alojamientos:
#         try:

#             id = alojamiento.id

#             url = alojamiento.link
#             driver.get("about:blank")
#             driver.get(url)

#             try:
#                 puntuacion_string = wait.until(
#                     EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[1]/div[1]/div[4]/div/div[1]/div[1]/div/div[1]/a/div/div/div/div[2]"))).text
#                 puntuacion_con_punto = puntuacion_string.split()[1]
#                 puntuacion = float(puntuacion_con_punto)
#             except:
#                 puntuacion = 0

#             try:
#                 personal = wait.until(EC.presence_of_element_located(
#                     (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[8]/div/div/div[2]/div/div[4]/div/div[2]/div[1]/div/div/div[1]/div[2]/div"))).text
#             except:
#                 personal = None

#             try:
#                 instalaciones_y_servicios = wait.until(EC.presence_of_element_located(
#                     (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[8]/div/div/div[2]/div/div[4]/div/div[2]/div[2]/div/div/div[1]/div[2]/div"))).text
#             except:
#                 instalaciones_y_servicios = None

#             try:
#                 limpieza = wait.until(EC.presence_of_element_located(
#                     (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[8]/div/div/div[2]/div/div[4]/div/div[2]/div[3]/div/div/div[1]/div[2]/div"))).text
#             except:
#                 limpieza = None

#             try:
#                 confort = wait.until(EC.presence_of_element_located(
#                     (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[8]/div/div/div[2]/div/div[4]/div/div[2]/div[4]/div/div/div[1]/div[2]/div"))).text
#             except:
#                 confort = None

#             try:
#                 relacion_calidad_precio = wait.until(EC.presence_of_element_located(
#                     (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[8]/div/div/div[2]/div/div[4]/div/div[2]/div[5]/div/div/div[1]/div[2]/div"))).text
#             except:
#                 relacion_calidad_precio = None

#             try:
#                 ubicacion = wait.until(EC.presence_of_element_located(
#                     (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[8]/div/div/div[2]/div/div[4]/div/div[2]/div[6]/div/div/div[1]/div[2]/div"))).text
#             except:
#                 ubicacion = None

#             try:
#                 coordenadas = wait.until(EC.presence_of_element_located(
#                     (By.CSS_SELECTOR, "a[id='map_trigger_header']"))).get_attribute("data-atlas-latlng")
#             except:
#                 coordenadas = None

#             try:
#                 string_comentarios = wait.until(EC.presence_of_element_located(
#                     (By.XPATH, "/html/body/div[4]/div/div[4]/main/div[1]/div[1]/div[1]/div[4]/div/div[1]/div[1]/div/div[1]/a/div/div/div/div[4]/div[2]"))).text
#                 cantidad_comentarios = string_comentarios.split()[0]
#             except:
#                 cantidad_comentarios = 0

#             try:
#                 button_calificacion = wait.until(EC.element_to_be_clickable(
#                     (By.CSS_SELECTOR, 'button[data-testid="quality-rating"]')))
#                 contenedor_calificacion = button_calificacion.find_element(
#                     By.TAG_NAME, "span")
#                 calificacion = contenedor_calificacion.find_elements(
#                     By.CSS_SELECTOR, ":scope > span")
#                 estrellas = len(calificacion)
#             except Exception as e:
#                 estrellas = 0

#             metricas_guardadas = session.query(MetricasAlojamiento).filter(
#                 MetricasAlojamiento.id_alojamiento == id).first()

#             if metricas_guardadas is None:

#                 nuevo_data_alojamiento = MetricasAlojamiento(
#                     id_alojamiento=id,
#                     puntuacion=puntuacion,
#                     personal=personal,
#                     instalaciones_y_servicios=instalaciones_y_servicios,
#                     limpieza=limpieza,
#                     confort=confort,
#                     relacion_calidad_precio=relacion_calidad_precio,
#                     ubicacion=ubicacion,
#                     estrellas=estrellas,
#                     coordenadas=coordenadas,
#                     cantidad_comentarios=cantidad_comentarios
#                 )

#                 session.add(nuevo_data_alojamiento)

#             else:
#                 metricas_guardadas.puntuacion = puntuacion
#                 metricas_guardadas.estrellas = estrellas

#             try:
#                 session.commit()
#                 print("Guardado exitosamente")
#             except:
#                 session.rollback()
#                 traceback.print_exc()

#         except Exception as e:
#             print(f"Alojamiento con ID {id} no almacenado")
#             traceback.print_exc()
#             continue


Base.metadata.create_all(engine)

for destino, link in destinos.items():
    try:
        driver.get("about:blank")
        print(f"== Procesando destino {destino} ==")
        cargar_todos_los_alojamientos(link=link)
        obtener_alojamientos(destino=destino, driver=driver,
                         fecha_reserva=fecha_reserva)
    except Exception as e:
        print(f"Error al procesar el destino {destino}")
        traceback.print_exc()
    finally:
        try:
            driver.delete_all_cookies()
        except Exception:
            pass
        try:
            driver.execute_cdp_cmd("Storage.clearDataForOrigin", {
                "origin": "https://www.booking.com",
                "storageTypes": "all"
            })
        except Exception:
            pass
        try:
            driver.execute_cdp_cmd("Network.clearBrowserCache", {})
        except Exception:
            pass
        try:
            driver.get("about:blank")
        except Exception:
            pass
        time.sleep(0.2)
# obtener_metricas_alojamiento(driver=driver)

try:
    driver.quit()
finally:
    xvfb_process.terminate()
