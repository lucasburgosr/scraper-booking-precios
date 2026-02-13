import pandas as pd
import os, sys

proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_dir)

from config.dbconfig import session
from models.alojamiento import Alojamiento
from models.metricas_alojamiento import MetricasAlojamiento
from models.precios_reserva import PrecioReserva

def clean_alojamientos():

    df_temporada = pd.read_csv("./csvs/precios_chile_temporada2023.csv", sep=",")

    # 1. Definimos los nombres de las columnas basándonos en tu imagen
    columnas = [
        "destino", 
        "nombre", 
        "ubicacion", 
        "tipo_alojamiento", 
        "link", 
        "clasificacion_emetur"
    ]

    # 2. Creamos el DataFrame vacío con estas columnas
    df_alojamientos = pd.DataFrame(columns=columnas, index=None)

    for row in df_temporada.itertuples(index=True):
        destino = row.f4bd0794db
        nombre = row.fcab3ed991
        ubicacion = row.f4bd0794db
        tipo_alojamiento = row.df597226dd
        link = row.c90a25d457
        clasificacion_emetur = row.Categoria

        a = {
            "destino": destino,
            "nombre": nombre,
            "ubicacion": ubicacion,
            "tipo_alojamiento": tipo_alojamiento,
            "link": link,
            "clasificacion_emetur": clasificacion_emetur
        }

        df_alojamientos = pd.concat([df_alojamientos, pd.DataFrame([a])], ignore_index=True)

    df_alojamientos.to_csv("./csvs/alojamientos_chile.csv", sep=";", encoding="utf-8")

def wipe_ids():
    df_brasil = pd.read_csv("./csvs/alojamientos_brasil.csv", sep=";", encoding="utf-8")
    df_bsas = pd.read_csv("./csvs/alojamientos_bsas.csv", sep=";", encoding="utf-8")
    df_chile = pd.read_csv("./csvs/alojamientos_chile.csv", sep=";", encoding="utf-8")
    df_mendoza = pd.read_csv("./csvs/alojamientos_mendoza.csv", sep=";", encoding="utf-8")
    df_pais = pd.read_csv("./csvs/alojamientos_pais.csv", sep=";", encoding="utf-8")
    df_pais1 = pd.read_csv("./csvs/alojamientos_pais1.csv", sep=";", encoding="utf-8")

    df_final = pd.concat([df_brasil, df_bsas, df_chile, df_mendoza, df_pais, df_pais1], ignore_index=True)
    df_final = df_final.drop(columns=["Unnamed: 0"])

    df_final.to_csv("./csvs/alojamientos_2023.csv", sep=";", encoding="utf-8", index=False)

def comparar_db():

    df_alojamientos = pd.read_csv("./csvs/alojamientos_2023.csv", sep=";", encoding="utf-8")

    for row in df_alojamientos.itertuples(index=False):
        existe = session.query(Alojamiento).filter(Alojamiento.nombre == row.nombre).first()

        if not existe:
            a = Alojamiento(
                destino = row.destino,
                nombre = row.nombre,
                ubicacion = row.ubicacion,
                tipo_alojamiento = row.tipo_alojamiento,
                link = row.link,
                clasificacion_emetur = row.clasificacion_emetur
            )

            try:
                session.add(a)
                session.commit()
                print("Nuevo alojamiento registrado")
            except Exception as e:
                session.rollback()
                print(f"Error al guardar el alojamiento en la DB: {e}")
        else:
            print(f"El alojamiento {row.nombre} ya se encuentra registrado en la DB")

comparar_db()