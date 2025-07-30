from config.dbconfig import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from models.alojamiento import Alojamiento

class MetricasAlojamiento(Base):
    __tablename__ = "metricas_alojamiento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_alojamiento = Column(Integer, ForeignKey("alojamientos.id"), nullable=False)
    puntuacion = Column(Float, nullable=True)
    estrellas = Column(Integer, nullable=True)
    personal = Column(String(25), nullable=True)
    instalaciones_y_servicios = Column(String(25), nullable=True)
    limpieza = Column(String(25), nullable=True)
    confort = Column(String(25), nullable=True)
    relacion_calidad_precio = Column(String(25), nullable=True)
    ubicacion = Column(String(25), nullable=True)
    coordenadas = Column(String(100), nullable=True)
    cantidad_comentarios = Column(String(10), nullable=True)

    alojamiento = relationship("Alojamiento", back_populates="data")
