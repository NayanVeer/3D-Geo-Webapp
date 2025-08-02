# routes/nearby.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from shapely.geometry import shape
from geopy.distance import geodesic
from fastapi.responses import JSONResponse
from db import get_db
from routes.utils.keyword_mapping import get_layer_filters

router = APIRouter()

@router.get("/api/nearby")
def get_nearby_features(lat: float, lon: float, type: str, distance: int = 1000, db: Session = Depends(get_db)):
    point_wkt = f"SRID=4326;POINT({lon} {lat})"
    filters = get_layer_filters(type)

    query_parts = []

    for filt in filters:
        table = filt['table']
        field = filt['field']
        value = filt.get('value')  # Optional value filter (e.g., 'hindu')

        where_clause = f"{field} ILIKE :type"
        if value:
            where_clause = f"{field} = :value"

        query = f"""
            SELECT '{table}' AS source, name, fclass, ST_AsGeoJSON(wkb_geometry) AS geom
            FROM public.{table}
            WHERE {where_clause}
            AND ST_DWithin(wkb_geometry::geography, ST_GeogFromText(:point), :distance)
        """
        query_parts.append(query)

    final_query = " UNION ".join(query_parts)
    stmt = text(final_query)

    # Bind parameters
    bind_params = {
        "type": f"%{type}%",
        "value": filters[0].get("value", None),  # Use the first value (if exists)
        "point": point_wkt,
        "distance": distance
    }

    results = db.execute(stmt, bind_params).fetchall()

    features = []
    min_dist = float('inf')
    nearest_name = None

    for row in results:
        try:
            geom = shape(eval(row.geom))
            centroid = geom.centroid
            coords = (centroid.y, centroid.x)
        except Exception:
            continue

        dist = geodesic((lat, lon), coords).meters
        if dist < min_dist:
            min_dist = dist
            nearest_name = row.name

        features.append({
            "source": row.source,
            "name": row.name,
            "fclass": row.fclass,
            "geometry": row.geom
        })

    ai_message = f"Found {len(features)} {type}(s) within {distance} meters."
    if nearest_name:
        ai_message += f" Nearest is '{nearest_name}' at approx {int(min_dist)} meters."

    return JSONResponse(content={
        "message": ai_message,
        "features": features
    })
