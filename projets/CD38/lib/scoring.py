import os
import logging
import geopandas as gpd
from tqdm import tqdm
from .type import Ponderation
from .grid import make_grid

# For pandas, to use progress_apply method
tqdm.pandas()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
)
logger.addHandler(handler)


class Scoring:
    def __init__(
        self,
        resolution: int = 500,
        hiking_trails_fn: str = "ressources/fusion_sentiers_OSM-PDIPR.geojson",
        observations_fn: str = "ressources/geonature_data_ens.geojson",
        user_frequency_fn: str = "ressources/user_frequency.gpkg",
        habitat_fn: str = "ressources/habitats_ENS_patrimoniaux.gpkg",
    ):
        grid_filename = f"ressources/grid_{resolution}.gpkg"

        if not os.path.exists(grid_filename):
            logger.info("Loading hiking trails...")
            self.hiking_trails = gpd.read_file(hiking_trails_fn).to_crs(epsg=4326)
            logger.info("Hiking trails loaded.")

            logger.info("Loading observations...")
            self.observations = gpd.read_file(observations_fn)
            logger.info("Observations loaded.")

            logger.info("Loading user frequency data...")
            self.user_frequency = gpd.read_file(user_frequency_fn)
            logger.info("User frequency data loaded.")

            logger.info("Loading habitat data...")
            self.habitat = gpd.read_file(habitat_fn).to_crs(epsg=4326)
            logger.info("Habitat data loaded.")

            logger.info("Generating grid (resolution=%s)...", resolution)
            self.grid = make_grid(self.observations, resolution)
            logger.info("Grid generated.")

            logger.info("Computing scores...")
            self.compute_each_score_per_cell()
            logger.info("Scores computed.")

            logger.info("Saving grid to %s", grid_filename)
            self.grid.to_file(grid_filename)
            logger.info("Grid saved.")
        else:
            logger.info("Loading existing grid from %s...", grid_filename)
            self.grid = gpd.read_file(grid_filename)
            logger.info("Grid loaded.")

    def compute_each_score_per_cell(self):
        """
        Compute scores for each cell in the grid.

        Scores are computed as follows:
        - species_presence_sc: sum of Note totale for each observation in the cell
        - hiking_trails_sc: sum of hiking trails in the cell
        - user_frequency_sc: sum of user frequency in the cell
        - habitat_presence_sc: sum of habitat presence in the cell

        Scores are stored in the grid GeoDataFrame.
        """

        def species_score(x):
            inters_obs = self.observations[self.observations.geometry.intersects(x)]
            inters_obs = inters_obs.drop_duplicates(subset=["nom_valide"])
            return inters_obs["Note totale"].apply(int).sum()

        self.grid["species_presence_sc"] = self.grid.geometry.progress_apply(
            lambda x: species_score(x)
        )
        self.grid["hiking_trails_sc"] = self.grid.geometry.progress_apply(
            lambda x: self.hiking_trails.geometry.intersects(x).sum()
        )
        self.grid["user_frequency_sc"] = self.grid.geometry.progress_apply(
            lambda x: self.user_frequency.geometry.intersects(x).sum()
        )
        self.grid["habitat_presence_sc"] = self.grid.geometry.progress_apply(
            lambda x: self.habitat.geometry.intersects(x).sum()
        )

    def get_grid_of_interest(self, geometry):
        """
        Return a GeoDataFrame of the grid cells (maille in french) that intersects
        with the given geometry.

        Parameters
        ----------
        geometry : shapely.geometry.Geometry
            The geometry to intersect with the grid

        Returns
        -------
        gpd.GeoDataFrame
            A GeoDataFrame of the grid cells that intersect with the given geometry
        """
        return self.grid[self.grid.intersects(geometry)]

    def compute_score_for_grid(
        self, grid_of_interest: gpd.GeoDataFrame, ponderation: Ponderation
    ):
        """
        Compute the score for each cell in the grid of interest.

        The score is computed by multiplying each score
        (species presence, hiking trails, user frequency, habitat presence)
        by its corresponding ponderation value, and then summing all the scores.

        Parameters
        ----------
        grid_of_interest : gpd.GeoDataFrame
            A GeoDataFrame of the grid cells that intersect with the given geometry
        ponderation : Ponderation
            The ponderation values for each score

        Returns
        -------
        gpd.GeoDataFrame
            A GeoDataFrame of the grid cells with their corresponding scores
        """
        goi = grid_of_interest.copy()
        goi["species_presence_sc_ponderated"] = ponderation.species_presence * (
            goi.species_presence_sc / goi.species_presence_sc.max()
        )
        goi["hiking_trails_sc_ponderated"] = ponderation.hiking_trail_presence * (
            goi.hiking_trails_sc / goi.hiking_trails_sc.max()
        )
        goi["user_frequency_sc_ponderated"] = ponderation.user_presence * (
            goi.user_frequency_sc / goi.user_frequency_sc.max()
        )
        goi["habitat_presence_sc_ponderated"] = ponderation.habitat_presence * (
            goi.habitat_presence_sc / goi.habitat_presence_sc.max()
        )
        goi["habitat_presence_sc_ponderated"] = goi[
            "habitat_presence_sc_ponderated"
        ].fillna(0)
        goi["score"] = (
            goi["species_presence_sc_ponderated"]
            + goi["hiking_trails_sc_ponderated"]
            + goi["user_frequency_sc_ponderated"]
            + goi["habitat_presence_sc_ponderated"]
        )
        return goi
