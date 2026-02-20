#!/bin/bash

# ==============================================================================
# Pipeline Scraper Booking.com
# Este script ejecuta el contenedor Docker del scraper y guarda los logs.
# ==============================================================================

# Definir variables
CONTAINER_NAME="booking_scraper"
IMAGE_NAME="booking_scraper_img"
LOG_DIR="/var/log/booking"
LOG_FILE="${LOG_DIR}/scraper_$(date +%Y%m%d_%H%M%S).log"
PROJECT_DIR=$(pwd) # Asumimos que se ejecuta desde la raíz del proyecto

echo "=================================================="
echo "Iniciando Pipeline de Scraper de Booking.com"
echo "Fecha y hora: $(date)"
echo "Los logs detallados se guardarán en: $LOG_FILE"
echo "=================================================="

# 1. Crear directorio de logs si no existe (requiere permisos de superusuario por ser /var/log)
if [ ! -d "$LOG_DIR" ]; then
    echo "Creando directorio de logs en $LOG_DIR..."
    sudo mkdir -p "$LOG_DIR"
    sudo chown $USER:$USER "$LOG_DIR"
fi

# 2. Construir la imagen Docker (Opcional, comentalo si la imagen ya existe y no hay cambios)
echo "Construyendo la imagen Docker..." | tee -a "$LOG_FILE"
docker build -t "$IMAGE_NAME" "$PROJECT_DIR" 2>&1 | tee -a "$LOG_FILE"

# 3. Eliminar contenedor previo si existiera (limpieza)
if [ "$(docker ps -aq -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "Limpiando contenedor anterior..." | tee -a "$LOG_FILE"
    docker rm -f "$CONTAINER_NAME" 2>&1 | tee -a "$LOG_FILE"
fi

# 4. Ejecutar el contenedor
echo "Ejecutando el contenedor (Scraper)..." | tee -a "$LOG_FILE"
# Se asume que existe un archivo .env en la misma carpeta del script
docker run --name "$CONTAINER_NAME" \
    --env-file "$PROJECT_DIR/.env" \
    --network host \
    --shm-size="2g" \
    "$IMAGE_NAME" 2>&1 | tee -a "$LOG_FILE"

# 5. Comprobar resultado
EXIT_CODE=$(docker inspect "$CONTAINER_NAME" --format='{{.State.ExitCode}}')

if [ "$EXIT_CODE" -eq 0 ]; then
    echo "STATUS: ÉXITO. El scraper finalizó correctamente." | tee -a "$LOG_FILE"
else
    echo "STATUS: ERROR. El scraper falló con código $EXIT_CODE." | tee -a "$LOG_FILE"
fi

echo "=================================================="
echo "Pipeline finalizado a las $(date)"
echo "Logs completos guardados en: $LOG_FILE"
echo "=================================================="
