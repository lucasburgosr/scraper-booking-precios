import os
import sys
proyecto_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(proyecto_dir)

from models.precios_reserva import PrecioReserva
from models.metricas_alojamiento import MetricasAlojamiento
from models.alojamiento import Alojamiento
from config.dbconfig import session, engine, Base
from dotenv import load_dotenv
from groq import Groq
from bs4 import BeautifulSoup
import requests
import time

from sqlalchemy import or_


# --- 1. CONFIGURACIÓN DE LA BASE DE DATOS Y API ---

# Cargar variables de entorno (GROQ_API_KEY)
load_dotenv()

# Configurar API Key de Groq
try:
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError(
            "La variable de entorno GROQ_API_KEY no está configurada.")
    client = Groq(api_key=api_key)
except ValueError as e:
    print(f"Error de configuración: {e}")
    exit()

# --- 2. FUNCIONES DE CLASIFICACIÓN (SIN CAMBIOS EN SU LÓGICA) ---


def extraer_texto_web(url):
    """Scraping básico del sitio para obtener una descripción."""
    if not url or not url.startswith('http'):
        print(f"URL inválida o ausente: {url}")
        return ""
    try:
        response = requests.get(url, timeout=15, headers={
                                'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extraer solo el texto visible, limitar a 2000 caracteres
            textos = soup.get_text(separator=' ', strip=True)
            return textos[:2000]
        else:
            print(f"Error {response.status_code} al acceder a {url}")
            return ""
    except Exception as e:
        print(f"Error de scraping en {url}: {e}")
        return ""


def clasificar_por_nombre(nombre):
    """Clasificación rápida basada en palabras clave en el nombre."""
    nombre_lower = nombre.lower()
    if "hostel" in nombre_lower:
        return "Hostel"
    if "hotel" in nombre_lower:
        return "Hotel"
    if "pat" in nombre_lower or "departamento" in nombre_lower or "apartment" in nombre_lower or "dpto" in nombre_lower or "depto" in nombre_lower or "apartamento" in nombre_lower:
        return "PAT"
    if "apart" in nombre_lower:
        return "Apart-Hotel"
    if "cabaña" in nombre_lower or "cabana" in nombre_lower:
        return "Cabañas"
    if "bed" in nombre_lower or "b&b" in nombre_lower:
        return "Bed & breakfast"
    if "lodge" in nombre_lower:
        return "Lodge"
    if "hospedaje" in nombre_lower:
        return "Hospedaje"
    if "habitación" in nombre_lower or "room" in nombre_lower:
        return "Habitación"
    return "Indeterminado"


def clasificar_llm(nombre, descripcion):
    """Clasificación avanzada usando el LLM de Groq."""
    prompt = f"""
Eres un experto en clasificación de alojamientos turísticos. Debes clasificar el siguiente establecimiento en UNA SOLA de las siguientes categorías:
Apart-Hotel, Bed & Breakfast, Cabañas, Habitación, Hospedaje, Hostel, Hotel, Lodge, Otros, Para-hotelero, PAT.

PAT es abreviación de Propiedad de Alquiler Temporario.

Nombre del establecimiento: {nombre}
Descripción extraída de la web: {descripcion}

Responde solo con la categoría exacta y nada más.
"""
    try:
        completion = client.chat.completions.create(
            model="gemma2-9b-it",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=20,
        )
        respuesta = completion.choices[0].message.content.strip()
        # Lista de categorías válidas para asegurar la respuesta del LLM
        categorias_validas = ["Apart-Hotel", "Bed & breakfast", "Cabañas", "Habitación", "Hospedaje", "Hostel",
                              "Hotel", "Lodge", "Otros", "Para-hotelero", "PAT"]
        return respuesta if respuesta in categorias_validas else "Otros"
    except Exception as e:
        print(f"Error llamando al LLM: {e}")
        return "Error LLM"

# --- 3. PROCESAMIENTO PRINCIPAL CON BASE DE DATOS ---


def procesar_alojamientos():

    try:
        # Buscar todos los alojamientos que necesitan clasificación
        alojamientos_a_procesar = session.query(Alojamiento).filter(Alojamiento.clasificacion_emetur == "Error LLM"
                                                                    ).all()

        total = len(alojamientos_a_procesar)
        if total == 0:
            print("¡Excelente! No hay alojamientos pendientes de clasificación.")
            return

        print(f"Se encontraron {total} alojamientos para clasificar.")

        for i, alojamiento in enumerate(alojamientos_a_procesar):
            print(
                f"\n--- Procesando {i+1}/{total}: ID {alojamiento.id} - {alojamiento.nombre} ---")

            # 1. Intentar clasificación por nombre
            categoria = clasificar_por_nombre(alojamiento.nombre)
            print(f"Clasificación por nombre: {categoria}")

            # 2. Si no es concluyente, usar scraping y el LLM
            if categoria == "Indeterminado":
                descripcion_web = extraer_texto_web(alojamiento.link)
                if descripcion_web:
                    print("Texto extraído, consultando al LLM...")
                    categoria = clasificar_llm(
                        alojamiento.nombre, descripcion_web)
                    print(f"Clasificación por LLM: {categoria}")
                else:
                    print("No se pudo extraer texto. Se asigna 'Otros'.")
                    categoria = "Otros"

            # 3. Actualizar el objeto en la sesión de SQLAlchemy
            print(f"Categoría final asignada: '{categoria}'")
            alojamiento.clasificacion_emetur = categoria

            # 4. Guardar progreso en la base de datos cada 5 registros
            if (i + 1) % 5 == 0:
                print(f"--- Guardando lote de 5 registros en la base de datos... ---")
                session.commit()

            time.sleep(1)  # Pausa para no saturar servidores

        # 5. Guardado final para los registros restantes
        print("\n--- Guardando registros restantes en la base de datos... ---")
        session.commit()
        print("Clasificación completada.")

    except Exception as e:
        print(f"Ha ocurrido un error inesperado: {e}")
        print("Revirtiendo últimos cambios no guardados (rollback)...")
        session.rollback()
    finally:
        session.close()
        print("Conexión a la base de datos cerrada.")


# --- Ejecutar el script ---
if __name__ == '__main__':
    procesar_alojamientos()
