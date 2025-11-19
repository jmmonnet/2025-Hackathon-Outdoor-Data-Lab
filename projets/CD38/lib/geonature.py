import geopandas as gpd
from .type import BoundingBox
from shapely.geometry import box
from shapely import to_geojson,box
import json

def load_geonature(fn="ressources/geonature_data_ens.geojson"):
    return gpd.read_file(fn)

def get_intersecting_observations(observations_gdf,bbox: BoundingBox):
    return observations_gdf[observations_gdf.intersects(box(bbox.x1, bbox.y1, bbox.x2, bbox.y2))]