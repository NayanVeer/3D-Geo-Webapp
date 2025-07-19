from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.model import Railway
from geoalchemy2.shape import to_shape

router = APIRouter()

@router.get("/railway")
def get_railway(db: Session = Depends(get_db)):
    railway_items = db.query(Railway).all()
    features = []
    for item in railway_items:
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
