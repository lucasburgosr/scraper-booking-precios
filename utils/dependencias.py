from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config.settings import CHECK_IN, CHECK_OUT, HEADLESS

# Parsing Functions


def parsear_a_float(num_string: str) -> float:
    """Parses a currency string (e.g. 'US$ 1.200,50') to float."""
    if not num_string:
        return 0.0

    # Remove currency symbol and whitespace
    num_clean = num_string.replace("US$", "").strip()

    if not num_clean:
        return 0.0

    # Handle European format (1.200,00 -> 1200.00) if applicable,
    # or US format. logic from original code:
    # numeric string -> replace . with nothing, replace , with .
    # This implies 1.000,00 format
    return float(num_clean.replace(".", "").replace(",", "."))


def parsear_impuestos(num_string: str) -> float:
    """Parses tax string."""
    if not num_string:
        return 0.0

    if "Incluye impuestos y cargos" in num_string:
        return 0.0

    if "+ US$" in num_string and "de impuestos y cargos" in num_string:
        num_sin_signos = num_string.replace(
            "+ US$", "").replace("de impuestos y cargos", "").strip()
        return float(num_sin_signos.replace(".", "").replace(",", "."))

    return 0.0

# Driver Initialization


def inicializar_driver():
    """Initializes Chrome WebDriver with configured options."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    # Overcome limited resource problems
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    if HEADLESS:
        options.add_argument("--headless=new")

    # Anti-detection / preferences
    prefs = {
        "profile.managed_default_content_settings.images": 2,  # Block images for speed
        "profile.default_content_setting_values.notifications": 2,
    }
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=options)

    driver.set_page_load_timeout(30)
    driver.set_script_timeout(30)

    return driver


# Destinations Configuration
# Solo parámetros funcionales: ss, dest_id, dest_type, fechas, huéspedes, moneda.
# Los parámetros de tracking (label, sid, ac_meta, etc.) causan que Booking
# descarte la búsqueda cuando no coinciden con una sesión válida.

_BASE = "https://www.booking.com/searchresults.es.html"
_PARAMS = f"&lang=es&checkin={CHECK_IN}&checkout={CHECK_OUT}&group_adults=2&no_rooms=1&group_children=0&selected_currency=USD"

destinos = {
    "Mendoza": f"{_BASE}?ss=Provincia+de+Mendoza%2C+Argentina&dest_id=597&dest_type=region{_PARAMS}",
    "Buenos Aires": f"{_BASE}?ss=Provincia+de+Buenos+Aires%2C+Argentina&dest_id=3619&dest_type=region{_PARAMS}",
    "CABA": f"{_BASE}?ss=Buenos+Aires%2C+Ciudad+Aut%C3%B3noma+de+Buenos+Aires%2C+Argentina&dest_id=-979186&dest_type=city{_PARAMS}",
    "Córdoba": f"{_BASE}?ss=Provincia+de+C%C3%B3rdoba%2C+Argentina&dest_id=1342&dest_type=region{_PARAMS}",
    "Santa Fe": f"{_BASE}?ss=Provincia+de+Santa+Fe%2C+Argentina&dest_id=3628&dest_type=region{_PARAMS}",
    "Neuquén": f"{_BASE}?ss=Neuqu%C3%A9n+Province%2C+Argentina&dest_id=3627&dest_type=region{_PARAMS}",
    "Salta": f"{_BASE}?ss=Provincia+de+Salta%2C+Argentina&dest_id=599&dest_type=region{_PARAMS}",
    "Jujuy": f"{_BASE}?ss=Jujuy%2C+Argentina&dest_id=596&dest_type=region{_PARAMS}",
    "Tucumán": f"{_BASE}?ss=Tucum%C3%A1n%2C+Argentina&dest_id=3629&dest_type=region{_PARAMS}",
    "Formosa": f"{_BASE}?ss=Provincia+de+Formosa%2C+Argentina&dest_id=3624&dest_type=region{_PARAMS}",
    "Santiago del Estero": f"{_BASE}?ss=Provincia+de+Santiago+del+Estero%2C+Argentina&dest_id=602&dest_type=region{_PARAMS}",
    "La Rioja": f"{_BASE}?ss=Provincia+de+La+Rioja%2C+Argentina&dest_id=3626&dest_type=region{_PARAMS}",
    "San Juan": f"{_BASE}?ss=Provincia+de+San+Juan%2C+Argentina&dest_id=600&dest_type=region{_PARAMS}",
    "San Luis": f"{_BASE}?ss=Provincia+de+San+Luis%2C+Argentina&dest_id=601&dest_type=region{_PARAMS}",
    "La Pampa": f"{_BASE}?ss=La+Pampa%2C+Argentina&dest_id=3625&dest_type=region{_PARAMS}",
    "Río Negro": f"{_BASE}?ss=R%C3%ADo+Negro%2C+Argentina&dest_id=598&dest_type=region{_PARAMS}",
    "Santa Cruz": f"{_BASE}?ss=Santa+Cruz%2C+Argentina&dest_id=3618&dest_type=region{_PARAMS}",
    "Catamarca": f"{_BASE}?ss=Provincia+de+Catamarca%2C+Argentina&dest_id=3620&dest_type=region{_PARAMS}",
    "Misiones": f"{_BASE}?ss=Misiones%2C+Argentina&dest_id=1343&dest_type=region{_PARAMS}",
    "Tierra del Fuego": f"{_BASE}?ss=Tierra+del+Fuego%2C+Argentina&dest_id=603&dest_type=region{_PARAMS}",
    "Corrientes": f"{_BASE}?ss=Provincia+de+Corrientes%2C+Argentina&dest_id=3623&dest_type=region{_PARAMS}",
    "Entre Ríos": f"{_BASE}?ss=Entre+R%C3%ADos%2C+Argentina&dest_id=595&dest_type=region{_PARAMS}",
    "Chaco": f"{_BASE}?ss=Chaco%2C+Argentina&dest_id=3621&dest_type=region{_PARAMS}",
    "Chubut": f"{_BASE}?ss=Chubut%2C+Argentina&dest_id=3622&dest_type=region{_PARAMS}",
    "Río de Janeiro": f"{_BASE}?ss=R%C3%ADo+de+Janeiro%2C+Brasil&dest_id=652&dest_type=region{_PARAMS}",
    "Viña del Mar": f"{_BASE}?ss=Vi%C3%B1a+del+Mar%2C+Chile&dest_id=-904540&dest_type=city{_PARAMS}",
}