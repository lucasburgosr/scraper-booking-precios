import os
from datetime import date, timedelta
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Database
DB_USER = os.getenv("DB_USER", "observer")
DB_PASSWORD = os.getenv("DB_PASSWORD", "8Vko*OH0Xv")
DB_HOST = os.getenv("DB_HOST", "149.50.141.218")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "booking")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Scraping
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Fechas
_default_date = date.today() + timedelta(days=23)
_env_date = os.getenv("RESERVATION_DATE")

if _env_date:
    try:
        RESERVATION_DATE = date.fromisoformat(_env_date)
    except ValueError:
        RESERVATION_DATE = _default_date
else:
    RESERVATION_DATE = _default_date

CHECK_IN = RESERVATION_DATE.strftime("%Y-%m-%d")
CHECK_OUT = (RESERVATION_DATE + timedelta(days=1)).strftime("%Y-%m-%d")