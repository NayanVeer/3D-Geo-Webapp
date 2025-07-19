from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import TrafficPoint
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/traffic-point")
def get_traffic_point(db: Session = Depends(get_db)):
    traffic_point_items = db.query(TrafficPoint).all()
    features = []
    for item in traffic_point_items:
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
