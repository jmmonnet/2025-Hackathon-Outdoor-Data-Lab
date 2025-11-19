from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return "Welcome to the CD38 API"


@app.get("/risk/")
def read_risk(x1:float,y1:float,x2:float,y2:float):
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
    return 1