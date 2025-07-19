from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.model import Buildings
from db import SessionLocal
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
from fastapi.responses import JSONResponse

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/buildings/geojson")
def get_buildings_geojson(db: Session = Depends(get_db)):
    features = []
    rows = db.query(Buildings).limit(1000).all()
    for row in rows:
        geom = to_shape(row.geom)
        features.append({
            "type": "Feature",
            "geometry": mapping(geom),
            "properties": {
                "id": row.id,
                "name": row.name
            }
        })
    return JSONResponse(content={"type": "FeatureCollection", "features": features})
