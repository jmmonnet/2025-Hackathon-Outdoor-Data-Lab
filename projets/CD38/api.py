from typing import Any, Union

from lib.type import BoundingBox
import json
from lib.scoring import Scoring
from fastapi import FastAPI
from lib.utils import to_geojson
from shapely.geometry import box
from shapely.geometry import shape
from fastapi.responses import HTMLResponse

app = FastAPI()
score_instance = Scoring()

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
    y1 : float
    x2 : float
    y2 : float

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
    return json.loads(score_instance.compute_score_for_grid(roi).to_json())

@app.post("/risk/geojson/")
def read_risk_geojson(geojson: dict[str, Any]):
    """
    Compute the risk on a geojson object

    Parameters
    ----------
    geojson : dict
        a geojson object (Feature, FeatureCollection, or Geometry)

    Returns
    -------
    dict
        a geojson with risk values
    """
    try:
        # Gérer différents types de GeoJSON
        if geojson.get("type") == "FeatureCollection":
            if not geojson.get("features"):
                return {"error": "FeatureCollection is empty"}
            geometry = shape(geojson["features"][0]["geometry"])
        elif geojson.get("type") == "Feature":
            geometry = shape(geojson["geometry"])
        else:
            geometry = shape(geojson)
        
        roi = score_instance.get_grid_of_interest(geometry)
        return json.loads(score_instance.compute_score_for_grid(roi).to_json())
    
    except Exception as e:
        return {"error": f"Failed to process GeoJSON: {str(e)}"}
    
