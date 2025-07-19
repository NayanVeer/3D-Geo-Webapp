import os
import subprocess

# Path to the folder containing your GeoJSONs
geojson_folder = os.path.join(os.getcwd(), 'Pune_City_Geojson')

# Connection string for PostGIS database
pg_connection = "PG:host=localhost port=5432 dbname=postgres user=postgres password=admin"

# Loop through all GeoJSON files in the folder
for filename in os.listdir(geojson_folder):
    if filename.endswith(".geojson"):
        filepath = os.path.join(geojson_folder, filename)
        tablename = os.path.splitext(filename)[0].lower().replace('-', '_').replace(' ', '_')

        print(f"\n📥 Importing {filename} as table '{tablename}'...")

        command = [
            'ogr2ogr',
            '-f', 'PostgreSQL',
            pg_connection,
            filepath,
            '-nln', tablename,
            '-nlt', 'PROMOTE_TO_MULTI',
            '-overwrite'
        ]

        try:
            subprocess.run(command, check=True)
            print(f"✅ Done: {tablename}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to import {filename}: {e}")
