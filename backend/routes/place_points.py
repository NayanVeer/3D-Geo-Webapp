from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import PlacePoints
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/place-points")
def get_place_points(db: Session = Depends(get_db)):
    place_points_items = db.query(PlacePoints).all()
    features = []
    for item in place_points_items:
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
