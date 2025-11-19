import geopandas as gpd
from .type import BoundingBox
from shapely.geometry import box

def load_hiking_trails():
    return gpd.read_file("ressources/OSM_hiking_routes38.geojson")

def get_intersecting_hiking_trails(trail_gdf,bbox: BoundingBox):
    return trail_gdf[trail_gdf.intersects(box(bbox.x1, bbox.y1, bbox.x2, bbox.y2))]