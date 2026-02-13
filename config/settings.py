import os
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

# Database
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Scraping
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Dates
_default_date = date.today() + timedelta(days=30)
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
