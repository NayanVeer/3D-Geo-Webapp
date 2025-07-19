from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# FastAPI app
app = FastAPI(title="3D Geo WebApp Backend")

# Enable CORS for frontend access (e.g., WebGL viewer, JS maps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root test route
@app.get("/")
async def root():
    return {"message": "Backend running 🚀"}

@app.get("/api/hello")
async def hello():
    return {"result": "Hello from FastAPI!"}

# ---------------------
# ✅ Include all routers
# ---------------------
from routes import (
    buildings, landuse, place_points, place_polygon, places, railway, roads,
    traffic_point, traffic_polygon, transport_stops, water_type, waterway, worship_places
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
