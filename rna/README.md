# Scripts de géocodage du RNA

## Prérequis

Pour fonctionner, ces scripts ont besoin de deux instances du géocodeur addok:
- l'une avec la BAN
- la seconde avec la BANO

Ceci représente au moins 36Go de RAM.
A titre d'information, le traitement intégral prends environ ~8 heures~ 4 heures sur une machine avec 24 coeurs et 96Go de RAM.


## Principe

Le fichier ZIP est décompressé et remis en forme (CSV, UTF8, virgules en séparateur, quotes uniquement si nécessaire).

Les retours à la ligne sont transformés en " \\n " et " \\r " pour éviter des problèmes de traitement des fichiers CSV.

Il est ensuite découpé par départements, pour un traitement en parallèle (avec GNU parallel).

Un script python effectue de multiples géocodages pour sélectionner le résultat le plus proche de l'information d'origine.
Il utilise par défaut la BAN et BANO en second choix si l'adresse n'est pas trouvée ou si le score minimal n'est pas atteint.

Si l'adresse n'est pas trouvée, les coordonnées du chef lieu de la commune sont utilisées comme longitude/latitude.
Pour les adresses indiquées "CHEF LIEU", "BOURG", "LE BOURG" ou "AU BOURG", les coordonnées du chef-lieu de la commune sont utilisées.


## Colonnes ajoutées par le géocodage

Les champs ajoutés sont:
- longitude (en degrés décimaux, WGS84)
- latitude (en dégrés décimaux, WGS84)
- geo_score : indice de similarité fournit par le moteur de géocodage
- geo_type : "housenumber" = n° trouvé, "interpolation" = n° interpolé, "street" = voie trouvée, "locality" = lieu-dit (ou position de la mairie), "municipality" = position de la commune car l'adresse n'a pas été trouvée.
- geo_adresse : libellé de l'adresse trouvée
- geo_id : id dans le référentiel BAN, ou BANO (si commence par "BANO_")
- geo_ligne : ligne d'adresse géocodée (G = géographique, N = normalisée, D = déclarée)
- geo_insee : code INSEE où l'adresse a été géocodée


**Les données contenues dans les colonnes ajoutées par le géocodage sont sous licence ODbL 1.0.**

Contact: adresse at data point gouv point fr
