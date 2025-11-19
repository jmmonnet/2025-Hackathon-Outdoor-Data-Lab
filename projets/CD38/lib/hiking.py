import geopandas as gpd
from .type import BoundingBox
from shapely.geometry import box
from shapely import to_geojson,box
import json

def load_hiking_trails(fn="ressources/OSM_hiking_routes38.geojson"):
    return gpd.read_file(fn)

def get_intersecting_hiking_trails(trail_gdf,bbox: BoundingBox):
    return trail_gdf[trail_gdf.intersects(box(bbox.x1, bbox.y1, bbox.x2, bbox.y2))]


