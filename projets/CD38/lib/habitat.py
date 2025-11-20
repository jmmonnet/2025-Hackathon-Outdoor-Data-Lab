import geopandas as gpd
from .type import BoundingBox
from shapely.geometry import box
from shapely import to_geojson,box
import json

def load_habitat(fn="ressources/habitats_ENS_patrimoniaux.gpkg"):
    return gpd.read_file(fn)

