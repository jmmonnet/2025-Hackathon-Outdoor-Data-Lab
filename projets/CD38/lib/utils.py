from shapely import box, to_geojson
import json
from .type import BoundingBox


def get_geojson_with_score_and_bbox(bbox: BoundingBox, score):
    shape = box(bbox.x1, bbox.y1, bbox.x2, bbox.y2)
    geojson = json.loads(to_geojson(shape))
    geojson["properties"] = {"score": score}
    return geojson


def gdf_to_geojson(gdf):
    return json.loads(gdf.to_json())
