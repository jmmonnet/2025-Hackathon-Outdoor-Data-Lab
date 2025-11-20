import geopandas
from pathlib import Path
from geopandas import GeoDataFrame
import numpy

ID_AREA_COLUMN = "id_area"

def save_result(mailles_with_coverage: GeoDataFrame, csv_output: Path, gpkg_output: Path) -> None:
    mailles_with_coverage[[ID_AREA_COLUMN, "pourcentage_de_sensibilite"]].to_csv(csv_output, index=False)
    print(f"Fichier CSV sauvegardé : {csv_output}")

    mailles_with_coverage.to_file(gpkg_output, layer="mailles_avec_pourcentage", driver="GPKG")
    print(f"Fichier GPKG sauvegardé : {gpkg_output}")


def load_gpkg(mailles_file: Path, zone_sensibles_file: Path) -> tuple[GeoDataFrame, GeoDataFrame]:
    mailles = geopandas.read_file(mailles_file)
    zones_sensibles = geopandas.read_file(zone_sensibles_file)
    return mailles, zones_sensibles

def coverage_percentage(mailles: GeoDataFrame, zones_sensibles: GeoDataFrame) -> GeoDataFrame:
    intersections = geopandas.overlay(mailles, zones_sensibles, how='intersection')
    intersections['intersection_area'] = intersections.geometry.area
    mailles['maille_area'] = mailles.geometry.area

    # Joindre avec les intersections pour obtenir les surfaces relatives
    intersections = intersections.merge(mailles[[ID_AREA_COLUMN, 'maille_area']], on=ID_AREA_COLUMN)

    # Calculer le pourcentage relatif (proportion par maille)
    intersections['pourcentage_de_sensibilite'] = intersections['intersection_area'] / intersections['maille_area']
    intersections.rename(columns={'code_ref': 'codes_refs_sensi'}, inplace=True)

    # Grouper par maille pour obtenir la somme des pourcentages et les codes intersectés
    couverture = intersections.groupby(ID_AREA_COLUMN).agg({
        'pourcentage_de_sensibilite': 'sum',
        'codes_refs_sensi': lambda codes: ', '.join(codes.astype(str))  # Concaténer les codes des zones intersectées
    }).reset_index()

    # Fusionner ces résultats avec les mailles originales
    mailles_with_coverage = mailles.merge(couverture, on=ID_AREA_COLUMN, how='left')

    # Remplacer les NaN par 0 (si une maille n'a pas de zone sensible qui la couvre)
    mailles_with_coverage['pourcentage_de_sensibilite'] = mailles_with_coverage['pourcentage_de_sensibilite'].fillna(0)

    # Ajouter une colonne "score" basée sur les conditions
    conditions = [
        (mailles_with_coverage['pourcentage_de_sensibilite'] == 0),
        (mailles_with_coverage['pourcentage_de_sensibilite'] > 0) & (
                    mailles_with_coverage['pourcentage_de_sensibilite'] < 0.3),
        (mailles_with_coverage['pourcentage_de_sensibilite'] >= 0.3) & (
                    mailles_with_coverage['pourcentage_de_sensibilite'] <= 0.7),
        (mailles_with_coverage['pourcentage_de_sensibilite'] > 0.7),
    ]
    scores = [0, 1, 2, 3]

    # Ajouter une colonne "score" basée sur les conditions
    mailles_with_coverage['score'] = numpy.select(conditions, scores, default=0)

    return mailles_with_coverage


if __name__ == '__main__':
    gpkg_folder = Path("../../data/")
    output_folder = Path("output/")
    output_folder.mkdir(parents=True, exist_ok=True)
    mailles, zones_sensibles = load_gpkg(gpkg_folder / "maille100_ens_moliere.gpkg", gpkg_folder/"zones_sensibles_pnrv.gpkg")
    mailles_avec_couverture = coverage_percentage(mailles, zones_sensibles)

    csv_output = output_folder / "mailles_pourcentage_sensibilite.csv"
    gpkg_output = output_folder / "mailles_pourcentage_sensibilite.gpkg"

    save_result(mailles_avec_couverture, csv_output, gpkg_output)
