# Script de traitement des données de Strava Metro
# Date : 20/11/2025
# Auteur : Delphine Jaymond (IMBE-INRAE)
# Hackathon "Sports de nature et biodiversité"

# Chargement des packages
library(dplyr)
library(sf)

# Chargement des données
# Données issues du compte Strava Metro de Christelle Bakhache (ASTERS)
don_hike <- read.csv("~/Documents/Projets/Hackathon/Strava/strava_hike.csv")
maps_hike <- st_read("~/Documents/Projets/Hackathon/Strava/strava_hike.shp", crs = 4326)
don_bike <- read.csv("~/Documents/Projets/Hackathon/Strava/strava_ride.csv")
maps_bike <- st_read("~/Documents/Projets/Hackathon/Strava/strava_ride.shp", crs = 4326)

# Modification du type de certaines colonnes
don_hike$date <- as.Date(don_hike$date)
don_bike$date <- as.Date(don_bike$date)

# Création de la table avec toutes les données
data_strava <- data.frame(id = don$edge_uid,
                          origine = "strava",
                          activite = don$activity_type,
                          nb_personnes = don$total_trip_count,
                          type = "sortie",
                          description = "aggrégation des sorties journalières sur un segment",
                          date = don$date)
data_strava <- rbind(data_strava,
                     data.frame(id = don_bike$edge_uid,
                                origine = "strava",
                                activite = don_bike$activity_type,
                                nb_personnes = don_bike$total_trip_count,
                                type = "sortie",
                                description = "aggrégation des sorties journalières sur un segment",
                                date = don_bike$date))

# On fusionne les 2 tables
data_strava$the_geom <- maps$geometry[match(data_strava$id, maps_hike$edgeUID)]
data_strava$the_geom <- maps$geometry[match(data_strava$id, maps_bike$edgeUID)]

# On indique la colonne de géométrie
st_geometry(data_strava) <- "the_geom"
# Identification du système de coordonnées
st_crs(data_strava)
# EPSG: 4326 (WGS84)

# On exporte la table en GEOJSON
st_write(data_strava, "./ASTERS/data_strava.geojson")
# Problème avec le CRS des données

# On aggrège les données pour les avoir sur la saison
# POur fairtre la jointure dans QGis directement
data_agg <- data_strava %>% 
  group_by(id, activite) %>% 
  summarise(nb_personnes = sum(nb_personnes))
# On exporte la table en shp
st_write(data_agg, "./ASTERS/data_strava_agg.shp")
