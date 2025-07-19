from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import TransportStops
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/transport-stops")
def get_transport_stops(db: Session = Depends(get_db)):
    transport_stops_items = db.query(TransportStops).all()
    features = []
    for item in transport_stops_items:
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
