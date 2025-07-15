from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="3D Geo WebApp Backend")

# Allow cross-origin requests from frontend (important for JS maps)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production: replace * with your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Backend running 🚀"}

@app.get("/api/hello")
async def hello():
    return {"result": "Hello from FastAPI!"}

# Connect FastAPI to PostGIS
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# A new API route to query your buildings table and return GeoJSON
from sqlalchemy import text

@app.get("/api/buildings")
def get_buildings():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT name, ST_AsGeoJSON(geom) FROM buildings"))
        features = []
        for row in result:
            features.append({
                "type": "Feature",
                "properties": {"name": row[0]},
                "geometry": eval(row[1])  # converts string GeoJSON to Python dict
            })
    return {
        "type": "FeatureCollection",
        "features": features
    }
