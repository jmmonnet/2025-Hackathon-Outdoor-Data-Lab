import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np


def make_grid(gdf, cell_size_m):
    """
    Create a grid over the extent of a GeoDataFrame.
    cell_size_m is in meters. The input GeoDataFrame must have a geographic CRS (EPSG:4326).
    """

    # 1. Reproject to a CRS in meters (UTM is usually best)
    utm_crs = gdf.estimate_utm_crs()
    gdf_utm = gdf.to_crs(utm_crs)

    # 2. Get bounding box
    minx, miny, maxx, maxy = gdf_utm.total_bounds

    # 3. Create grid cells
    x_coords = np.arange(minx, maxx, cell_size_m)
    y_coords = np.arange(miny, maxy, cell_size_m)

    polys = []
    for x in x_coords:
        for y in y_coords:
            polys.append(
                Polygon(
                    [
                        (x, y),
                        (x + cell_size_m, y),
                        (x + cell_size_m, y + cell_size_m),
                        (x, y + cell_size_m),
                    ]
                )
            )

    # 4. Convert to GeoDataFrame
    grid = gpd.GeoDataFrame({"geometry": polys}, crs=utm_crs).to_crs(4326)

    return grid
