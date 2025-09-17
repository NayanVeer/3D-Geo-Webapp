from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
from routes import nearby, history
from dotenv import load_dotenv
import os

load_dotenv()


# ----------------------------
# ✅ Initialize FastAPI app
# ----------------------------
app = FastAPI(title="3D Geo WebApp Backend")
app.include_router(nearby.router, prefix="/api")
# ----------------------------
# ✅ Enable CORS for frontend
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# ✅ Root & Ping Test Routes
# ----------------------------
@app.get("/")
async def root():
    return {"message": "Backend running 🚀"}

@app.get("/ping")
def ping():
    return {"message": "pong"}

@app.get("/api/hello")
async def hello():
    return {"result": "Hello from FastAPI!"}

# ----------------------------
# ✅ Geocode Proxy to Pelias
# ----------------------------
@app.get("/api/geocode")
async def geocode(query: str):
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"http://localhost:4000/v1/search?text={query}")
            data = r.json()
        if data['features']:
            coords = data['features'][0]['geometry']['coordinates']
            label = data['features'][0]['properties']['label']
            return {"lat": coords[1], "lon": coords[0], "label": label}
        else:
            return {"error": "No results found"}
    except Exception as e:
        return {"error": str(e)}

# ----------------------------
# ✅ Register all routers
# ----------------------------
from routes import (
    buildings, landuse, place_points, place_polygon, places, railway, roads,
    traffic_point, traffic_polygon, transport_stops, water_type, waterway,
    worship_places, spatial_query, nearby, ai_search
)

app.include_router(buildings.router)
app.include_router(landuse.router)
app.include_router(place_points.router)
app.include_router(place_polygon.router)
app.include_router(places.router)
app.include_router(railway.router)
app.include_router(roads.router)
app.include_router(traffic_point.router)
app.include_router(traffic_polygon.router)
app.include_router(transport_stops.router)
app.include_router(water_type.router)
app.include_router(waterway.router)
app.include_router(worship_places.router)
app.include_router(spatial_query.router)
app.include_router(nearby.router)
app.include_router(history.router)
app.include_router(ai_search.router)