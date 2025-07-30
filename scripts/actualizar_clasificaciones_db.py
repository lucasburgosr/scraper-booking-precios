import os
import sys
proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_dir)

import pandas as pd
import numpy as np
from models.alojamiento import Alojamiento
from models.metricas_alojamiento import MetricasAlojamiento
from models.precios_reserva import PrecioReserva
from config.dbconfig import engine, Base, session


def actualizar_con_orm():
    """
    Función principal para leer el CSV y actualizar la BD usando SQLAlchemy ORM.
    """
    try:
        # --- Leer y limpiar los datos del CSV ---
        print(f"Leyendo el archivo CSV:")
        df_csv = pd.read_csv("./csvs/base_completa_sin_clasificar.csv")
        df_csv['clasificacion_emetur'].replace('', np.nan, inplace=True)
        df_csv.dropna(subset=['clasificacion_emetur'], inplace=True)
        print(
            f"Se encontraron {len(df_csv)} registros con una clasificación válida en el CSV.")
        if len(df_csv) == 0:
            return

        # --- MODO SIMULACIÓN (DRY RUN) ---
        # print("\n--- INICIANDO MODO SIMULACIÓN (DRY RUN) ---")
        # print("El script planifica realizar las siguientes actualizaciones:")
        # for index, row in df_csv.iterrows():
        #     # Buscar el alojamiento en la BD que coincida por nombre y destino
        #     alojamiento_a_actualizar = session.query(Alojamiento).filter_by(
        #         nombre=row['nombre'],
        #         destino=row['destino']
        #     ).first()

        #     if alojamiento_a_actualizar:
        #         print(
        #             f"  -> Plan: Actualizar '{alojamiento_a_actualizar.nombre}' en '{alojamiento_a_actualizar.destino}' con la clasificación: '{row['clasificacion_emetur']}'")
                
        # --- MODO EJECUCIÓN REAL ---
        # ¡PELIGRO! Descomenta el siguiente bloque solo después de verificar
        # que la simulación muestra los resultados correctos.

        print("\n--- INICIANDO MODO EJECUCIÓN REAL ---")
        updated_count = 0
        for index, row in df_csv.iterrows():
            # Buscar el alojamiento en la BD
            alojamiento_a_actualizar = session.query(Alojamiento).filter_by(
                nombre=row['nombre'],
                destino=row['destino'],
            ).first()

            # Si se encuentra y la clasificación actual es nula (o si quieres sobreescribir siempre)
            if alojamiento_a_actualizar:
                if alojamiento_a_actualizar.clasificacion_emetur is None:
                    print(f"Actualizando alojamiento {alojamiento_a_actualizar.nombre}")
                    alojamiento_a_actualizar.clasificacion_emetur = row['clasificacion_emetur']
                    updated_count += 1
        
        if updated_count > 0:
            print(f"Confirmando {updated_count} actualizaciones en la base de datos...")
            session.commit() # Guardar todos los cambios en una sola transacción
            print("¡ÉXITO! Cambios guardados.")
        else:
            print("No se encontraron registros coincidentes para actualizar.")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo csv")
    except Exception as e:
        print(f"Ha ocurrido un error: {e}")
        if 'session' in locals():
            print("Revirtiendo cambios (rollback)...")
            session.rollback()
    finally:
        if 'session' in locals():
            session.close()
            print("\nSesión de SQLAlchemy cerrada.")

actualizar_con_orm()