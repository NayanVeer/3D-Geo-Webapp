# ai_search.py
import os
import logging
import re
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from db import get_db
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class AiQuery(BaseModel):
    query: str

async def geocode_landmark(query: str):
    """Use Pelias to get lat/lon for a landmark"""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"http://localhost:4000/v1/search?text={query}&size=1")
            data = r.json()
        if data.get("features"):
            coords = data["features"][0]["geometry"]["coordinates"]
            return coords[1], coords[0]  # lat, lon
        else:
            return None, None
    except Exception as e:
        logger.error(f"Geocoding failed: {e}")
        return None, None

@router.post("/ai-search")
async def ai_search(request: AiQuery, db: Session = Depends(get_db)):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not set in environment")

    query_text = request.query.strip()

    # --- Extract distance from query ---
    match = re.search(r'within (\d+) ?m', query_text, re.IGNORECASE)
    distance = int(match.group(1)) if match else 1000
    query_text_clean = re.sub(r'within (\d+) ?m', '', query_text, flags=re.IGNORECASE).strip()

    # --- AI Prompt ---
    prompt = f"""
You are an expert PostGIS assistant.
Convert the user query into a valid SQL query for one of these tables:

1. worship_places
   - fclass ∈ {{hindu, muslim, christian, sikh}}
   - Example: temples, mosques, churches, gurudwaras.

2. place_points
   - fclass includes {{hospital, clinic, pharmacy, restaurant, cafe, atm, bar, bank, library, hotel, park, police, school, university, etc.}}

3. transport_stops
   - fclass ∈ {{bus_stop, bus_station, railway_station, taxi}}

4. traffic_point
   - fclass ∈ {{fuel, traffic_signals, parking, parking_bicycle, parking_underground, crossing, speed_camera, turning_circle, mini_roundabout, motorway_junction}}

5. places
   - fclass ∈ {{city, town, suburb, village, locality, region}}

Rules:
- Identify which table best matches the query.
- Always include: ogc_fid, name, fclass, wkb_geometry
- If query mentions 'near [landmark]', generate SQL using:
    ST_DWithin(wkb_geometry, __LANDMARK_PLACEHOLDER__, __DISTANCE__)
- Only query ONE table per request.
- Do not add explanations, markdown or comments, return only SQL.
"""

    logger.info(f"AI Prompt:\n{prompt}\nUser Query: {query_text_clean}")

    # --- Call OpenRouter / Scout model ---
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": query_text_clean},
                    ],
                },
                timeout=60.0,
            )
        response.raise_for_status()
        ai_sql = response.json()["choices"][0]["message"]["content"].strip()
        if ai_sql.endswith(";"):
            ai_sql = ai_sql[:-1]

        debug_sql = ai_sql
    except Exception as e:
        logger.error(f"AI request failed: {e}")
        raise HTTPException(status_code=500, detail="AI request failed")

    # --- Handle landmark proximity ---
    if "__LANDMARK_PLACEHOLDER__" in ai_sql:
        lat, lon = await geocode_landmark(query_text_clean)
        if lat is None or lon is None:
            raise HTTPException(status_code=404, detail=f"Could not resolve landmark: {query_text_clean}")
        ai_sql = ai_sql.replace(
            "__LANDMARK_PLACEHOLDER__",
            f"ST_SetSRID(ST_MakePoint({lon}, {lat}), 4326), {distance}"
        )

    # --- Wrap in GeoJSON query ---
    final_sql = f"""
        SELECT ogc_fid, name, fclass,
               ST_AsGeoJSON(wkb_geometry)::json AS geometry
        FROM ({ai_sql}) AS subquery
    """
    logger.info(f"Executing SQL:\n{final_sql}")

    try:
        rows = db.execute(text(final_sql)).mappings().all()
        features = [{
            "type": "Feature",
            "geometry": row["geometry"],
            "properties": {
                "ogc_fid": row["ogc_fid"],
                "name": row["name"],
                "fclass": row["fclass"]
            }
        } for row in rows]

        return {
            "user_query": query_text,
            "ai_sql_raw": debug_sql,
            "ai_sql_final": final_sql,
            "type": "FeatureCollection",
            "features": features,
            "warning": "No features returned by the query." if not features else None
        }

    except Exception as e:
        logger.error(f"Database query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute query. AI SQL may be invalid. Error: {e}"
        )
