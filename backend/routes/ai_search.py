# import os
# import httpx
# from fastapi import APIRouter, Depends, HTTPException, Body
# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from geoalchemy2.shape import to_shape
# from db import get_db
# import logging
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# router = APIRouter()

# # --- AI Prompt Configuration ---
# DB_SCHEMA = """
# You are an expert PostGIS assistant. Your task is to convert natural language questions into valid PostGIS SQL queries.
# Your must only return a single, executable SQL query. Do not include any other text, explanations, or markdown.

# The user is querying a database with the following tables in the 'public' schema:

# 1.  `buildings` (ogc_fid, name, wkb_geometry: MULTIPOLYGON)
# 2.  `landuse` (ogc_fid, landuse, wkb_geometry: MULTIPOLYGON)
# 3.  `place_points` (ogc_fid, name, type, wkb_geometry: POINT)
# 4.  `place_polygon` (ogc_fid, name, type, wkb_geometry: MULTIPOLYGON)
# 5.  `places` (ogc_fid, name, type, wkb_geometry: GEOMETRY)
# 6.  `railway` (ogc_fid, railway, wkb_geometry: LINESTRING)
# 7.  `roads` (ogc_fid, name, highway, wkb_geometry: LINESTRING)
# 8.  `traffic_point` (ogc_fid, fclass, name, wkb_geometry: POINT)
# 9.  `traffic_polygon` (ogc_fid, fclass, name, wkb_geometry: MULTIPOLYGON)
# 10. `transport_stops` (ogc_fid, name, fclass, wkb_geometry: POINT)
# 11. `water_type` (ogc_fid, fclass, name, wkb_geometry: MULTIPOLYGON)
# 12. `waterway` (ogc_fid, fclass, name, width, wkb_geometry: LINESTRING)
# 13. `worship_places` (ogc_fid, fclass, name, wkb_geometry: POINT) - fclass can be 'place_of_worship'

# Key Functions to Use:
# - ST_Distance, ST_DWithin, ST_Intersects, ST_SetSRID, ST_Transform

# Examples:
# User Query: "Find all temples"
# SQL Query:
# SELECT name, wkb_geometry FROM worship_places WHERE fclass = 'place_of_worship';

# User Query: "Show me hospitals near me at lon 73.85 and lat 18.52, within 1km"
# SQL Query:
# SELECT name, wkb_geometry FROM place_points 
# WHERE type = 'hospital' 
# AND ST_DWithin(wkb_geometry, ST_Transform(ST_SetSRID(ST_MakePoint(73.85, 18.52), 4326), ST_SRID(wkb_geometry)), 1000);

# Now, answer the following user query.
# """

# async def get_sql_from_ai(user_query: str):
#     """
#     Calls the OpenRouter API to convert a natural language query into SQL.
#     """
#     api_key = os.getenv("OPENROUTER_API_KEY")
#     if not api_key:
#         raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not set.")

#     prompt = f"""{DB_SCHEMA}
# User Query: "{user_query}" """
#     logger.info(f"AI Prompt: {prompt}")

#     async with httpx.AsyncClient() as client:
#         try:
#             response = await client.post(
#                 "https://openrouter.ai/api/v1/chat/completions",
#                 headers={
#                     "Authorization": f"Bearer {api_key}",
#                     "Content-Type": "application/json"
#                 },
#                 json={
#                     "model": "meta-llama/llama-4-scout:free",
#                     "messages": [
#                         {"role": "system", "content": "You are an expert PostGIS assistant that converts natural language to SQL."},
#                         {"role": "user", "content": prompt}
#                     ]
#                 },
#                 timeout=60.0
#             )
#             response.raise_for_status()
#             data = response.json()
#             sql_query = data['choices'][0]['message']['content'].strip()

#             # Clean the response to get only the SQL
#             if sql_query.startswith("```sql"):
#                 sql_query = sql_query[6:]
#             if sql_query.endswith("```"):
#                 sql_query = sql_query[:-3]
#             sql_query = sql_query.replace("\\\n", " ").replace("\n", " ").strip()

#             logger.info(f"Generated SQL: {sql_query}")
#             return sql_query

#         except httpx.HTTPStatusError as e:
#             logger.error(f"AI API request failed: {e.response.text}")
#             raise HTTPException(status_code=500, detail=f"AI service request failed: {e.response.text}")
#         except Exception as e:
#             logger.error(f"Unexpected error in AI request: {e}")
#             raise HTTPException(status_code=500, detail="Failed to communicate with AI service.")

# @router.post("/ai-search")
# async def ai_search(payload: dict = Body(...), db: Session = Depends(get_db)):
#     """
#     Accepts a natural language query, converts it to SQL using an AI model,
#     executes the SQL on the PostGIS database, and returns the result as GeoJSON.
#     """
#     user_query = payload.get("query")
#     if not user_query:
#         raise HTTPException(status_code=400, detail="Query not provided.")

#     try:
#         sql_query = await get_sql_from_ai(user_query)

#         # --- Basic SQL safety check ---
#         if any(keyword in sql_query.upper() for keyword in ["DROP", "DELETE", "UPDATE", "INSERT", "TRUNCATE"]):
#             raise HTTPException(status_code=400, detail="Invalid query generated. Write operations are not allowed.")

#         # --- Transform geometry to 4326 and return WKB ---
#         if "wkb_geometry" in sql_query.lower() or "geom" in sql_query.lower():
#             if sql_query.endswith(";"):
#                 sql_query = sql_query[:-1].strip()
#             sql_query = f"""
#             SELECT *, ST_AsBinary(ST_Transform(wkb_geometry, 4326)) AS wkb_geometry
#             FROM ({sql_query}) AS subquery
#             """

#         logger.info(f"Executing SQL: {sql_query}")
#         result = db.execute(text(sql_query)).fetchall()

#         features = []
#         for row in result:
#             row_dict = dict(row._mapping)
#             geom_col = next((key for key in row_dict if 'geom' in key.lower()), None)
#             if not geom_col or row_dict[geom_col] is None:
#                 continue
#             shape = to_shape(row_dict[geom_col])
#             properties = {k: v for k, v in row_dict.items() if k != geom_col}
#             features.append({
#                 "type": "Feature",
#                 "geometry": shape.__geo_interface__,
#                 "properties": properties
#             })

#         return {
#             "ai_sql": sql_query,
#             "type": "FeatureCollection",
#             "features": features,
#             "warning": "No features returned by the query. Check table data or AI SQL." if not features else None
#         }

#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         logger.error(f"Database query failed: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to execute query. AI SQL may be invalid. Error: {str(e)}")


# For worship places Only
import os
import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session
from db import get_db  # ✅ use your existing db session
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class AiQuery(BaseModel):
    query: str

@router.post("/ai-search")
async def ai_search(request: AiQuery, db: Session = Depends(get_db)):
    """
    AI-assisted search ONLY for worship_places table.
    """

    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OPENROUTER_API_KEY not set in environment")

    # --- AI Prompt ---
    prompt = f"""
    You are an expert PostGIS assistant. 
    Convert the user query into a valid SQL query for the table worship_places.

    worship_places table:
      - ogc_fid (integer)
      - osm_id (varchar)
      - code (integer)
      - fclass (varchar)  -> 'hindu', 'muslim', 'christian', etc.
      - name (varchar)    -> temple/mandir/masjid/church name
      - wkb_geometry (MultiPoint, 4326)

    Examples:
    User Query: "Find all temples"
    SQL: SELECT ogc_fid, name, fclass, wkb_geometry FROM worship_places WHERE name ILIKE '%temple%' OR name ILIKE '%mandir%';

    User Query: "Find all Hindu temples"
    SQL: SELECT ogc_fid, name, fclass, wkb_geometry FROM worship_places WHERE fclass = 'hindu';

    User Query: "Find all mosques"
    SQL: SELECT ogc_fid, name, fclass, wkb_geometry FROM worship_places WHERE fclass = 'muslim';

    IMPORTANT:
    - Only query worship_places.
    - Always include ogc_fid, name, fclass, and wkb_geometry in SELECT.
    - Do not add explanations or markdown, only SQL.
    """

    logger.info(f"AI Prompt:\n{prompt}\nUser Query: {request.query}")

    # --- Call OpenRouter ---
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
                        {"role": "user", "content": request.query},
                    ],
                },
                timeout=60.0,
            )
        response.raise_for_status()
        ai_sql = response.json()["choices"][0]["message"]["content"].strip()

# 🚨 Remove trailing semicolons (common issue with AI output)
        if ai_sql.endswith(";"):
            ai_sql = ai_sql[:-1]

        logger.info(f"Generated SQL (cleaned): {ai_sql}")

    except Exception as e:
        logger.error(f"AI request failed: {e}")
        raise HTTPException(status_code=500, detail="AI request failed")

    # --- Wrap in GeoJSON query ---
    final_sql = f"""
        SELECT ogc_fid, name, fclass,
               ST_AsGeoJSON(wkb_geometry)::json AS geometry
        FROM ({ai_sql}) AS subquery
    """
    logger.info(f"Executing SQL:\n{final_sql}")

    try:
        rows = db.execute(text(final_sql)).mappings().all()

        features = []
        for row in rows:
            features.append({
                "type": "Feature",
                "geometry": row["geometry"],
                "properties": {
                    "ogc_fid": row["ogc_fid"],
                    "name": row["name"],
                    "fclass": row["fclass"]
                }
            })

        return {
            "ai_sql": final_sql,
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
