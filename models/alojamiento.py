from config.dbconfig import Base
from sqlalchemy import Column, Integer, String, Float, Date, Text
from sqlalchemy.orm import relationship

class Alojamiento(Base):
    __tablename__ = "alojamientos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    destino = Column(String(255), nullable=False)
    nombre = Column(String(255), nullable=False)
    ubicacion = Column(String(255), nullable=False)
    tipo_alojamiento = Column(String(255), nullable=False)
    link = Column(Text, nullable=False)
    clasificacion_emetur = Column(String(255), nullable=True)

    data = relationship("MetricasAlojamiento", back_populates="alojamiento", cascade="all, delete-orphan")
    precios_reserva = relationship("PrecioReserva", back_populates="alojamiento")