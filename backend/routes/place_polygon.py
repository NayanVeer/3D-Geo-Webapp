from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import PlacePolygon
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/place-polygon")
def get_place_polygon(db: Session = Depends(get_db)):
    place_polygon_items = db.query(PlacePolygon).all()
    features = []
    for item in place_polygon_items:
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
