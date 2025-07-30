from config.dbconfig import Base
from sqlalchemy import Column, Integer, String, Float, Date, Text, ForeignKey
from sqlalchemy.orm import relationship

class PrecioReserva(Base):
    __tablename__ = "precios_reserva"

    id = Column(Integer, primary_key=True, autoincrement=True)
    id_alojamiento = Column(Integer, ForeignKey("alojamientos.id"), nullable=False)
    fecha_registro = Column(Date, nullable=False)
    fecha_reserva = Column(Date, nullable=False)
    precio_en_dolares = Column(Float, nullable=False)
    impuestos_en_dolares = Column(Float, nullable=True)

    alojamiento = relationship("Alojamiento", back_populates="precios_reserva")