# routes/valhalla.py
from typing import List, Optional
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import httpx

router = APIRouter(prefix="/api/valhalla", tags=["valhalla"])

# ----------------------------
# Config
# ----------------------------
VALHALLA_URL = os.getenv("VALHALLA_URL", "http://localhost:8002/route")
HTTP_TIMEOUT = float(os.getenv("VALHALLA_TIMEOUT", "15.0"))  # seconds


# ----------------------------
# Pydantic Models
# ----------------------------
class Point(BaseModel):
    lat: float = Field(..., description="Latitude")
    lon: float = Field(..., description="Longitude")


class RouteRequest(BaseModel):
    locations: List[Point] = Field(..., min_items=2, description="Start and end points")
    costing: Optional[str] = Field("auto", description="Costing model (auto/bicycle/pedestrian/etc.)")


# ----------------------------
# Low-level Valhalla Proxy
# ----------------------------
@router.post("/route", summary="Proxy request to Valhalla and return raw JSON")
async def route_proxy(req: RouteRequest):
    payload = {"locations": [{"lat": p.lat, "lon": p.lon} for p in req.locations], "costing": req.costing}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            resp = await client.post(VALHALLA_URL, json=payload)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Valhalla request failed: {exc}") from exc

    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    return resp.json()


# ----------------------------
# Polyline Decoder
# ----------------------------
def _decode_polyline(encoded: str, precision: int = 6):
    coords, index, lat, lng = [], 0, 0, 0
    factor = 10 ** precision

    while index < len(encoded):
        for coord in (lat, lng):
            shift, result = 0, 0
            while True:
                b = ord(encoded[index]) - 63
                index += 1
                result |= (b & 0x1f) << shift
                shift += 5
                if b < 0x20:
                    break
            dcoord = ~(result >> 1) if (result & 1) else (result >> 1)
            if coord is lat:
                lat += dcoord
            else:
                lng += dcoord
        coords.append((lat / factor, lng / factor))
    return coords


# ----------------------------
# Valhalla → GeoJSON converter
# ----------------------------
def valhalla_to_geojson(valhalla_json: dict):
    trip = valhalla_json.get("trip", {})
    features = []

    # Decode line geometry
    all_coords = []
    for leg in trip.get("legs", []):
        shape = leg.get("shape")
        if not shape:
            continue
        decoded = _decode_polyline(shape, 6)
        if all_coords and decoded and all_coords[-1] == decoded[0]:
            decoded = decoded[1:]
        all_coords.extend(decoded)

    if all_coords:
        features.append({
            "type": "Feature",
            "properties": {"summary": trip.get("summary", {})},
            "geometry": {"type": "LineString", "coordinates": [[lon, lat] for lat, lon in all_coords]}
        })

    # Add maneuver points
    if trip.get("legs"):
        maneuvers = trip["legs"][0].get("maneuvers", [])
        for m in maneuvers:
            idx = int(m.get("begin_shape_index", 0))
            if 0 <= idx < len(all_coords):
                lat, lon = all_coords[idx]
                features.append({
                    "type": "Feature",
                    "properties": {
                        "instruction": m.get("instruction"),
                        "time": m.get("time"),
                        "length": m.get("length"),
                        "street_names": m.get("street_names", [])
                    },
                    "geometry": {"type": "Point", "coordinates": [lon, lat]}
                })

    return {"type": "FeatureCollection", "features": features}


# ----------------------------
# High-level endpoint (for routing.js)
# ----------------------------
@router.post("/route/geojson", summary="Get Valhalla route as decoded GeoJSON")
async def route_geojson(req: RouteRequest):
    payload = {"locations": [{"lat": p.lat, "lon": p.lon} for p in req.locations], "costing": req.costing}

    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
        try:
            resp = await client.post(VALHALLA_URL, json=payload)
        except httpx.RequestError as exc:
            raise HTTPException(status_code=502, detail=f"Valhalla request error: {exc}") from exc

    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Valhalla returned {resp.status_code}: {resp.text}")

    valhalla_json = resp.json()
    geojson = valhalla_to_geojson(valhalla_json)

    return {"valhalla": valhalla_json, "geojson": geojson}
