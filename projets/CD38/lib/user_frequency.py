import geopandas as gpd
from .type import BoundingBox
from shapely.geometry import box
from shapely import to_geojson, box
import json


def load_user_frequency(fn="ressources/user_frequency.gpkg"):
    return gpd.read_file(fn)
