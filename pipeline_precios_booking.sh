#!/bin/bash

# --- Configuración de rutas y usuarios ---
WORKSPACE="/home/observer/scripts/scraper-booking"
PUBLIC_DATA_DIR="/home/observer/public_html/data"
MYSQL_OUTFILE="/var/lib/mysql-files/booking.csv"
USER_WEB="observer:observer"
DB_NAME="booking"

# Crear carpeta temporal si no existe
mkdir -p "$WORKSPACE"

echo ">>> Iniciando Pipeline: $(date)"

# 1. Ejecución del ETL (Docker)
echo "1/5 Ejecutando ETL..."
docker run --rm --name scraper_booking scraper_booking || { echo "Falló el ETL"; exit 1; }

# 2. Exportación MySQL (Host)
echo "2/5 Exportando desde MySQL..."
rm -f "$MYSQL_OUTFILE" # Limpieza necesaria para INTO OUTFILE
mysql -u root "$DB_NAME" -e "
    (SELECT 'localidad', 'fecha_registro', 'fecha_proyeccion', 'dias_proyeccion', 'establecimientos_ofrecidos', 'establecimientos_disponibles', 'porcentaje_ocupacion')
    UNION ALL
    (SELECT localidad, fecha_registro, fecha_proyeccion, dias_proyeccion, establecimientos_ofrecidos, establecimientos_disponibles, porcentaje_ocupacion FROM proyeccion_export)
    INTO OUTFILE '$MYSQL_OUTFILE'
    FIELDS TERMINATED BY ';'
    LINES TERMINATED BY '\n';
" || { echo "Falló la exportación MySQL"; exit 1; }

# Mover al workspace y dar permisos iniciales para que el siguiente Docker lo lea
mv "$MYSQL_OUTFILE" "$WORKSPACE/booking.csv"
chown $USER_WEB "$WORKSPACE/booking.csv"
chmod 644 "$WORKSPACE/booking.csv"

# 3. Ejecución de Cálculos (Docker)
echo "3/5 Ejecutando contenedor de cálculos..."
docker run --rm -v "$WORKSPACE":/data procesamiento-ocupacion || { echo "Falló el contenedor de cálculos"; exit 1; }

# 4. Copia a Carpeta Pública
echo "4/5 Publicando archivos en public_html..."
cp "$WORKSPACE/booking.csv" "$PUBLIC_DATA_DIR/"
cp "$WORKSPACE/consultas_proyeccion.csv" "$PUBLIC_DATA_DIR/"
cp "$WORKSPACE/parametros_regresion.csv" "$PUBLIC_DATA_DIR/"
cp "$WORKSPACE/comparacion_r2.csv" "$PUBLIC_DATA_DIR/"

# 5. Aplicación de Permisos y Propietario (Sustituye a tus 8 crons)
echo "5/5 Ajustando permisos finales..."
chown $USER_WEB "$PUBLIC_DATA_DIR"/*.csv
chmod o+r "$PUBLIC_DATA_DIR"/*.csv

echo ">>> Pipeline completado con éxito: $(date)"