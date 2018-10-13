# Scripts de géocodage des fichiers stock SIRENE version 2019

En octobre 2018, l'INSEE a modifié le format des fichiers de diffusion de la base SIRENE au format CSV.

Ces scripts sont destinés à géocoder ces nouveaux fichiers et ont été adaptés à partir des scripts servant à géocoder la base SIRENE depuis fin 2016.

Seul le fichier StockEtablissement est traité, vu que c'est le seul fichier parmis les 4 diffusés par l'INSEE qui contient des adresses.

Les changements:
- les fichiers sont désormais tous compressés en gzip (plus de 7z)
- un traitement supplémentaire prends en compte les anciennes communes qui n'existent plus (fusions) et leur fait correspondre le code INSEE actuel afin de permettre le géocodage
- le stock national est disponible pour les établissements Actifs et pour l'ensemble des établissements (Actifs ou Fermés)

# Fichiers générés

- StockEtablissement_geo.csv.gz : fichier national complet (29 millions)
- StockEtablissementActif_geo.csv.gz : fichier national des établissements Actifs (11 millions)
- geo_siret_DDD.csv.gz : stock complet pour un département (et arrondissements de Paris)
- communes/{codeINSEEcommune}.csv : stock complet pour une commune
- logs.7z : logs complet de géocodage (un fichier par département)
- stats.json : statistiques finales du géocodage par département

Exemple:
```
{
  "action": "final",
  "count": 518841,
  "efficacite": 99.69,
  "fichier": "historique/data/dep_94.csv",
  "geocode_cache": 512560,
  "geocode_count": 36399,
  "geocode_score_avg": 0.8621282880021781,
  "geocode_score_variance": 0.006177756765848515,
  "housenumber": 476942,
  "interpolation": 3513,
  "locality": 461,
  "municipality": 1,
  "poi": 2385,
  "street": 33956,
  "townhall": 0,
  "vide": 0
}
```
geocode_score_avg et geocode_score_variance indiquent le score moyen et la variance du score, ce qui donne un indicateur de pertinence du géocodage sur le département.

housenumber, interpolation, street, locality, poi, municipality indiquent le nombre d'adresses géocodées au numéro, interpolées, à la rue, au lieu-dit, sur un point d'intérêt ou à la commune.
