from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import Waterway
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/waterway")
def get_waterway(db: Session = Depends(get_db)):
    waterway_items = db.query(Waterway).all()
    features = []
    for item in waterway_items:
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
