from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import Landuse
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/landuse")
def get_landuse(db: Session = Depends(get_db)):
    landuse_items = db.query(Landuse).all()
    features = []
    for item in landuse_items:
        geom = to_shape(item.geom)
        features.append({
            "type": "Feature",
            "geometry": geom.__geo_interface__,
            "properties": {
                "id": item.id,
                "landuse": item.landuse
            }
        })
    return {
        "type": "FeatureCollection",
        "features": features
    }
