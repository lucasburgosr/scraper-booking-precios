from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine(
    'mysql+pymysql://root:Lucas15Roman16_@localhost:3306/booking',
    pool_pre_ping=True,
    pool_recycle=1800)
Session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
session = Session()
Base = declarative_base()

# engine = create_engine('mysql+pymysql://observer:8Vko*OH0Xv@localhost:3307/booking', pool_pre_ping=True)