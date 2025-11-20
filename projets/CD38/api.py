import json
from typing import Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from lib.scoring import Scoring
from lib.type import Ponderation
from shapely.geometry import GeometryCollection, MultiPolygon, box, shape
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()
score_instance = Scoring(resolution=500)
pond=Ponderation(0.35,0.4,0.1,0.15)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return HTMLResponse(open("index.html").read(), status_code=200)


@app.get("/risk/")
def read_risk(x1:float=None,y1:float=None,x2:float=None,y2:float=None,bbox:str=None):
    """
    Compute the risk on a bounding box defined by its top left coordinates (x1,y1) and its bottom right coordinates (x2,y2) 

    Parameters
    ----------
    x1 : float
        min x
    y1 : float
        min y
    x2 : float
        max x
    y2 : float
        max y
    bbox : str
        a string format of the bbox "x1,y1,x2,y2" (eg. 5.530345,45.180724,5.655314,45.254969)

    Returns
    -------
    float
        a risk value between 0 and 1
    """
    if bbox:
        x1 = float(bbox.split(",")[0])
        y1 = float(bbox.split(",")[1])
        x2 = float(bbox.split(",")[2])
        y2 = float(bbox.split(",")[3])
    elif x1 is None or y1 is None or x2 is None or y2 is None:
        return "Missing parameters"
    roi = score_instance.get_grid_of_interest(box(x1, y1, x2, y2))
    return json.loads(score_instance.compute_score_for_grid(roi,pond).to_json())


@app.post("/risk/geojson/")
def read_risk_geojson(geojson: dict[str, Any]):
    
    # --- Handle FeatureCollection ---
    if geojson.get("type") == "FeatureCollection":
        features = geojson.get("features", [])
        if not features:
            return {"error": "FeatureCollection is empty"}

        shapely_geoms = [shape(feat["geometry"]) for feat in features]

        # Extract only Polygons / MultiPolygons
        polygons = []
        for g in shapely_geoms:
            if g.geom_type == "Polygon":
                polygons.append(g)
            elif g.geom_type == "MultiPolygon":
                polygons.extend(list(g.geoms))

        if polygons:
            geometry = MultiPolygon(polygons)
        else:
            # fallback: everything else
            geometry = GeometryCollection(shapely_geoms)

    elif geojson.get("type") == "Feature":
        geometry = shape(geojson["geometry"])

    else:
        geometry = shape(geojson)

    # Compute risk
    roi = score_instance.get_grid_of_interest(geometry)
    return json.loads(score_instance.compute_score_for_grid(roi, pond).to_json())

    