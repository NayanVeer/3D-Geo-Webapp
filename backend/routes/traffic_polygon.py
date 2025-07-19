from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import TrafficPolygon
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/traffic-polygon")
def get_traffic_polygon(db: Session = Depends(get_db)):
    traffic_polygon_items = db.query(TrafficPolygon).all()
    features = []
    for item in traffic_polygon_items:
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
