@echo off
setlocal enabledelayedexpansion

set "GEOJSON_DIR=.\Pune_City_Geojson"
set "PG_CONN=PG:host=localhost port=5433 dbname=pune_city user=postgres password=admin"

for %%f in (%GEOJSON_DIR%\*.geojson) do (
    set "filename=%%~nf"
    set "table_name=!filename: =_!"
    set "table_name=!table_name:-=_!"
    set "table_name=!table_name:A=a!"
    echo 📥 Importing %%f as !table_name!...
    ogr2ogr -f "PostgreSQL" "!PG_CONN!" "%%f" -nln "!table_name!" -nlt PROMOTE_TO_MULTI -overwrite
)

echo ✅ All GeoJSON files have been imported successfully.
