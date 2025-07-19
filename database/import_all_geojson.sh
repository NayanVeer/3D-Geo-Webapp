#!/bin/bash

DB_CONN="PG:host=localhost port=5432 dbname=pune_city user=postgres password=admin"
GEOJSON_DIR="./Pune_City_Geojson"

for file in "$GEOJSON_DIR"/*.geojson; do
  table_name=$(basename "$file" .geojson | tr '[:upper:]' '[:lower:]' | tr '-' '_' | tr ' ' '_')
  echo "📥 Importing $file as '$table_name'..."
  ogr2ogr -f "PostgreSQL" "$DB_CONN" "$file" \
    -nln "$table_name" -nlt PROMOTE_TO_MULTI -overwrite
done
echo "✅ All GeoJSON files have been imported successfully."