import pandas as pd
import numpy as np

# --- Nombres de los archivos ---
archivo_maestro = './csvs/alojamientos_202506121038.csv'
archivo_fuente = './csvs/precios 2025 mayo - base.csv'
archivo_final = 'clasificaciones_actualizado.csv'

try:
    # Cargar ambos archivos
    df_maestro = pd.read_csv(archivo_maestro)
    df_fuente = pd.read_csv(archivo_fuente)
    print(f"Archivo maestro '{archivo_maestro}' cargado con {len(df_maestro)} registros.")
    print(f"Archivo fuente '{archivo_fuente}' cargado con {len(df_fuente)} registros.\n")

except FileNotFoundError as e:
    print(f"Error: No se pudo encontrar el archivo {e.filename}. Verifica los nombres y la ubicación.")
    exit()

# --- FASE 1: ACTUALIZAR CLASIFICACIONES EXISTENTES ---

print("--- INICIANDO FASE 1: Actualizar registros existentes ---")

# 1. Preparar los datos de la fuente: Renombrar columna y quedarnos con lo esencial.
#    Esto evita conflictos y hace el proceso más eficiente.
df_fuente_limpio = df_fuente.rename(columns={'Clasificación': 'clasificacion_emetur'})
df_fuente_limpio = df_fuente_limpio.drop_duplicates(subset=['nombre'], keep='last') # Por si hay nombres duplicados en la fuente

# 2. Crear un "diccionario de búsqueda" (nombre -> clasificacion_emetur) desde la fuente.
#    Es la forma más eficiente de buscar los datos.
mapa_clasificaciones = df_fuente_limpio.set_index('nombre')['clasificacion_emetur'].to_dict()
print(f"Se ha creado un mapa con {len(mapa_clasificaciones)} clasificaciones únicas desde la fuente.")

# 3. Usar el mapa para "proponer" clasificaciones al DataFrame maestro.
clasificaciones_propuestas = df_maestro['nombre'].map(mapa_clasificaciones)

# 4. Rellenar SOLAMENTE las clasificaciones que están vacías (NaN) en el maestro.
#    Si ya había un valor, .fillna() no lo sobreescribe.
df_maestro['clasificacion_emetur'].fillna(clasificaciones_propuestas, inplace=True)
print("Se han actualizado las clasificaciones vacías en el archivo maestro.\n")


# --- FASE 2: AGREGAR ALOJAMIENTOS NUEVOS ---

print("--- INICIANDO FASE 2: Agregar nuevos alojamientos ---")

# 5. Identificar qué alojamientos de la fuente NO existen en el maestro.
nombres_maestro = set(df_maestro['nombre'])
nuevos_registros = df_fuente_limpio[~df_fuente_limpio['nombre'].isin(nombres_maestro)]

if nuevos_registros.empty:
    print("No se encontraron alojamientos nuevos para agregar.")
    df_final = df_maestro.copy() # El resultado final es solo el maestro actualizado
else:
    print(f"Se encontraron {len(nuevos_registros)} alojamientos nuevos para agregar.")
    
    # 6. Seleccionar solo las columnas necesarias de los nuevos registros para que coincidan con el maestro.
    columnas_a_mantener = ['nombre', 'ubicacion', 'tipo_alojamiento', 'link', 'clasificacion_emetur']
    nuevos_registros_formateados = nuevos_registros[columnas_a_mantener]
    
    # 7. Combinar el maestro (ya actualizado) con los nuevos registros.
    #    Pandas alineará las columnas y dejará en blanco (NaN) las que no correspondan (id, destino).
    df_final = pd.concat([df_maestro, nuevos_registros_formateados], ignore_index=True)
    print("Se han agregado los nuevos alojamientos al final del archivo.")


# --- FASE 3: GUARDAR RESULTADO ---

# 8. Guardar el DataFrame final y unificado.
df_final.to_csv(archivo_final, index=False)
print(f"\n✅ ¡Proceso completado!")
print(f"El archivo final '{archivo_final}' ha sido creado con {len(df_final)} registros totales.")
print("Este archivo contiene los registros originales actualizados y los nuevos alojamientos agregados.")