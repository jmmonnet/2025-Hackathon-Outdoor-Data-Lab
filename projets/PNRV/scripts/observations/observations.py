import geopandas
import pandas as pd

input_maille_path = "/home/theo/Documents/SCIENTIFIQUE/odl_2025/mailles_ens.gpkg"
input_obs_path = "/home/theo/Documents/SCIENTIFIQUE/odl_2025/obs_ens.gpkg"


df_maille = geopandas.read_file(input_maille_path)
df_observation = geopandas.read_file(input_obs_path)
# f = lambda x:numpy.sum(df_observation.intersects(x))
# df_maille['nb_obs'].apply(f)

point_in_poly = geopandas.sjoin(df_observation, df_maille, how="left", predicate="within")

counts = point_in_poly.groupby("id_area").size().reset_index(name="nb_points")

maille_with_counts = df_maille.merge(counts, on="id_area", how="left")
maille_with_counts["nb_points"] = maille_with_counts["nb_points"].fillna(0)

min = maille_with_counts["nb_points"].min()
max = maille_with_counts["nb_points"].max()


# bornes avec interval égal
# bornes = numpy.linspace(min, max, 11) 
# print(bornes)

# borne avec quantile

maille_with_counts["score"] = 0
bornes = maille_with_counts["nb_points"].quantile([0, 1/3, 2/3, 1]).tolist()

print(bornes)
maille_with_counts.loc[maille_with_counts["nb_points"] > 0, "score"] = pd.cut(
    maille_with_counts.loc[maille_with_counts["nb_points"] > 0, "nb_points"],
    bins=bornes,
    labels=[1, 2, 3],     # faible, moyen, fort
    include_lowest=True,
    duplicates="drop"
).astype(int)




maille_with_counts.to_file("/home/theo/Documents/SCIENTIFIQUE/odl_2025/mailles_with_count_obs.gpkg", driver="gpkg")
