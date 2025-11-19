

from .hiking import get_intersecting_hiking_trails, load_hiking_trails
from .type import BoundingBox
from shapely import box, to_geojson
import json


class Scoring:
    def __init__(self,hiking_trail_file):
        self.hiking_trails = load_hiking_trails(hiking_trail_file)
 
    def compute_score(self,bbox: BoundingBox):
        return 1-(1/len(get_intersecting_hiking_trails(self.hiking_trails,bbox)))
    
    