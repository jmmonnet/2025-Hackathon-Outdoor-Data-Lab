

from lib.habitat import load_habitat
from lib.user_frequency import load_user_frequency
from lib.grid import make_grid
from .hiking import load_hiking_trails
from .geonature import load_geonature
import geopandas as gpd
from .type import Ponderation
from tqdm import tqdm
import os

tqdm.pandas()


class Scoring:
    def __init__(self,resolution=500):
        
        fn = f"ressources/grid_{resolution}.gpkg"
        if not os.path.exists(fn):
            print("load hiking trails")
            self.hiking_trails = load_hiking_trails("ressources/fusion_sentiers_OSM-PDIPR.geojson")
            self.hiking_trails = self.hiking_trails.to_crs(epsg=4326)
            print("load observations")
            self.observations = load_geonature()
            print("load user frequency")
            self.user_frequency = load_user_frequency()#.sample(n=2000)
            print("load habitat")
            self.habitat = load_habitat()
            self.habitat = self.habitat.to_crs(epsg=4326)

            print("make grid")
            self.grid = make_grid(self.observations,resolution)
            print("compute scores")
            self.compute_each_score_per_cell()
            print("save grid")
            self.grid.to_file(fn)
        else:
            print("load existing grid")
            self.grid = gpd.read_file(fn)
    
    def compute_each_score_per_cell(self):
        def species_score(x):
            inters_obs = self.observations[self.observations.geometry.intersects(x)]
            inters_obs = inters_obs.drop_duplicates(subset=["nom_valide"])
            return inters_obs["Note totale"].apply(int).sum()
        self.grid["species_presence_sc"] = self.grid.geometry.progress_apply(lambda x: species_score(x))
        self.grid["hiking_trails_sc"] = self.grid.geometry.progress_apply(lambda x: self.hiking_trails.geometry.intersects(x).sum())
        self.grid["user_frequency_sc"] = self.grid.geometry.progress_apply(lambda x: self.user_frequency.geometry.intersects(x).sum())
        self.grid["habitat_presence_sc"] = self.grid.geometry.progress_apply(lambda x: self.habitat.geometry.intersects(x).sum())
    
    def get_grid_of_interest(self,geometry):
        return self.grid[self.grid.intersects(geometry)]

    def compute_score_for_grid(self,grid_of_interest:gpd.GeoDataFrame, ponderation:Ponderation):
        goi = grid_of_interest.copy()
        goi["species_presence_sc_ponderated"] = ponderation.species_presence*(goi.species_presence_sc/goi.species_presence_sc.max())
        goi["hiking_trails_sc_ponderated"] = ponderation.hiking_trail_presence*(goi.hiking_trails_sc/goi.hiking_trails_sc.max())
        goi["user_frequency_sc_ponderated"] = ponderation.user_presence*(goi.user_frequency_sc/goi.user_frequency_sc.max())
        goi["habitat_presence_sc_ponderated"] = ponderation.habitat_presence*(goi.habitat_presence_sc/goi.habitat_presence_sc.max())
        goi["score"] = goi["species_presence_sc_ponderated"] + goi["hiking_trails_sc_ponderated"] + goi["user_frequency_sc_ponderated"] + goi["habitat_presence_sc_ponderated"]
        return goi

    