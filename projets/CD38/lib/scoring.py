

from lib.grid import make_grid
from .hiking import load_hiking_trails
from .geonature import load_geonature
import geopandas as gpd


class Scoring:
    def __init__(self):
        self.hiking_trails = load_hiking_trails()
        self.observations = load_geonature()
        self.grid = make_grid(self.observations,500)
    
    def get_grid_of_interest(self,geometry):
        return self.grid[self.grid.intersects(geometry)]
    
    def compute_score_for_grid(self,grid_of_interest:gpd.GeoDataFrame):
        goi = grid_of_interest.copy()
        goi["nb_observations"] = goi.geometry.apply(lambda x: self.observations.geometry.intersects(x).sum())
        goi["nb_hiking_trails"] = goi.geometry.apply(lambda x: self.hiking_trails.geometry.intersects(x).sum())
        goi["score"] = 1-(1/(1+goi["nb_hiking_trails"])) + (1-(1/(1+goi["nb_observations"])))/2
        return goi

    