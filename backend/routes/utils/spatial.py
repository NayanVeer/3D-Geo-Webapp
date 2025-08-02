from sqlalchemy import text
from fastapi import Depends
from sqlalchemy.orm import Session
from db import get_db

def get_nearest_features(lon: float, lat: float, radius_m: int, db: Session):
    query = text(f"""
        SELECT 'hospital' AS type, name, ST_AsGeoJSON(geom) AS geometry
        FROM hospitals
        WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :radius)

        UNION

        SELECT 'bus_stop' AS type, name, ST_AsGeoJSON(geom) AS geometry
        FROM transport_stops
        WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :radius)

        UNION

        SELECT 'temple' AS type, name, ST_AsGeoJSON(geom) AS geometry
        FROM worship_places
        WHERE lower(type) = 'temple'
        AND ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography, :radius)
    """)

    return db.execute(query, {"lon": lon, "lat": lat, "radius": radius_m}).fetchall()
