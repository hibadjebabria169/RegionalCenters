from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import json
import math

app = FastAPI(
    title="Sports Health Centers API",
    description="API for querying sports and health centers in Centre-Val de Loire region",
    version="1.0.0"
)

# Enable CORS for web agents
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data
def load_centers():
    with open("sportsantecvl.json", "r", encoding="utf-8") as f:
        return json.load(f)

centers = load_centers()


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers."""
    R = 6371  # Earth's radius in km
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c


@app.get("/")
def root():
    """API root - returns basic info."""
    return {
        "message": "Sports Health Centers API",
        "total_centers": len(centers),
        "endpoints": {
            "all_centers": "/centers",
            "center_by_id": "/centers/{id}",
            "search": "/search?q=keyword",
            "by_discipline": "/discipline?name=Tennis",
            "by_pathology": "/pathology?name=Cancer",
            "nearby": "/nearby?lat=47.0&lng=2.0&radius_km=50"
        }
    }


@app.get("/centers")
def get_all_centers(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0)
):
    """Get all centers with pagination."""
    return {
        "total": len(centers),
        "limit": limit,
        "offset": offset,
        "data": centers[offset:offset + limit]
    }


@app.get("/centers/{center_id}")
def get_center_by_id(center_id: str):
    """Get a specific center by its ID."""
    for center in centers:
        if center["id"] == center_id:
            return center
    raise HTTPException(status_code=404, detail=f"Center with id {center_id} not found")


@app.get("/search")
def search_centers(q: str = Query(..., min_length=2, description="Search keyword")):
    """Search centers by keyword (searches name, description, discipline)."""
    q_lower = q.lower()
    results = []
    for center in centers:
        if (q_lower in center["Name"].lower() or
            q_lower in center["Description"].lower() or
            q_lower in center["Discipline"].lower()):
            results.append(center)
    return {"query": q, "count": len(results), "data": results}


@app.get("/discipline")
def get_by_discipline(name: str = Query(..., description="Discipline name (e.g., Tennis, Basket, Natation)")):
    """Get centers offering a specific discipline/sport."""
    name_lower = name.lower()
    results = [c for c in centers if name_lower in c["Discipline"].lower()]
    return {"discipline": name, "count": len(results), "data": results}


@app.get("/disciplines")
def list_disciplines():
    """List all unique disciplines available."""
    all_disciplines = set()
    for center in centers:
        for d in center["Discipline"].split("\r\n"):
            d = d.strip()
            if d:
                all_disciplines.add(d)
    return {"count": len(all_disciplines), "disciplines": sorted(all_disciplines)}


@app.get("/pathology")
def get_by_pathology(name: str = Query(..., description="Pathology name (e.g., Cancer, diabète)")):
    """Get centers handling a specific pathology/condition."""
    name_lower = name.lower()
    results = [c for c in centers if name_lower in c["Pathologies / Prévention"].lower()]
    return {"pathology": name, "count": len(results), "data": results}


@app.get("/pathologies")
def list_pathologies():
    """List all unique pathologies/conditions handled."""
    all_pathologies = set()
    for center in centers:
        for p in center["Pathologies / Prévention"].split("\r\n"):
            p = p.strip()
            if p:
                all_pathologies.add(p)
    return {"count": len(all_pathologies), "pathologies": sorted(all_pathologies)}


@app.get("/nearby")
def get_nearby_centers(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius_km: float = Query(default=50, ge=1, le=500, description="Search radius in kilometers")
):
    """Find centers within a given radius of a location."""
    results = []
    for center in centers:
        center_lat = float(center["lat"])
        center_lng = float(center["lng"])
        distance = haversine_distance(lat, lng, center_lat, center_lng)
        if distance <= radius_km:
            results.append({**center, "distance_km": round(distance, 2)})

    results.sort(key=lambda x: x["distance_km"])
    return {
        "location": {"lat": lat, "lng": lng},
        "radius_km": radius_km,
        "count": len(results),
        "data": results
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
