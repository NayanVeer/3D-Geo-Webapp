from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from .utils.spatial import get_nearest_features

router = APIRouter()

@router.get("/nearest_features/")
def nearest_features(lon: float, lat: float, radius: int = 500, db: Session = Depends(get_db)):
    results = get_nearest_features(lon, lat, radius, db)
    return [
        {
            "type": row["type"],
            "name": row["name"],
            "geometry": row["geometry"]
        }
        for row in results
    ]
