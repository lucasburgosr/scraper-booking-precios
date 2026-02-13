from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.settings import DATABASE_URL

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=1800
)

# Create Session factory
SessionLocal = sessionmaker(
    bind=engine, autoflush=False, expire_on_commit=False)

# Declarative Base
Base = declarative_base()


def get_db():
    """
    Generator to get a database session.
    Useful for dependency injection or context management.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
