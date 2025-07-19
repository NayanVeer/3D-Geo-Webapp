from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import WorshipPlaces
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/worship-places")
def get_worship_places(db: Session = Depends(get_db)):
    worship_places_items = db.query(WorshipPlaces).all()
    features = []
    for item in worship_places_items:
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
