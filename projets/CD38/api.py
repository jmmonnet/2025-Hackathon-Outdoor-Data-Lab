from typing import Union

from lib.type import BoundingBox

from lib.scoring import Scoring
from fastapi import FastAPI
from lib.utils import get_geojson_with_score_and_bbox

app = FastAPI()
score_instance = Scoring("ressources/OSM_hiking_routes38.geojson")
@app.get("/")
def read_root():
    return "Welcome to the CD38 API"


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
    box = BoundingBox(x1,y1,x2,y2)
    return get_geojson_with_score_and_bbox(box,score_instance.compute_score(box))