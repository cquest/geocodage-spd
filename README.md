# Scripts de géocodage de la base SIRENE

## Prérequis

Pour fonctionner, ces scripts ont besoin de deux instances du géocodeur addok:
- l'une avec la BAN
- la seconde avec la BANO

Ceci représente au moins 36Go de RAM.
A titre d'information, le traitement intégral prends environ 8 heures sur une machine avec 24 coeurs et 96Go de RAM.


## Principe

Le fichier ZIP est décompressé et remis en forme (CSV, UTF8, virgules en séparateur, quotes uniquement si nécessaire).
Cette remise en forme lui fait perdre 2Go.

Il est ensuite dénormalisé et simplifié:
- élimination des libellés
- dénormalisation des données géographiques

2Go de plus sont ainsi économisés.

Il est ensuite découpé par départements (colonne DEPET), pour un traitement en parallèle (avec GNU parallel).

Un script python effectue de multiples géocodages pour sélectionner le résultat le plus proche de l'information d'origine.
Il utilise par défaut la BAN et BANO en second choix si l'adresse n'est pas trouvée ou si le score minimal n'est pas atteint.
C'est l'adresse "géographique" qui est utilisée en premier et à défaut l'adresse déclarée (ligne4) ou l'adresse normalisée.

Si l'adresse n'est pas trouvée, les coordonnées du chef lieu de la commune sont utilisées comme longitude/latitude.
Pour les adresses indiquées "MAIRIE" ou "HOTEL DE VILLE", les coordonnées sont reprises de l'annuaire des services publics diffusé en opendata par la DILA.


## Colonnes ajoutées par le géocodage

Les champs ajoutés sont:
- longitude (en degrés décimaux, WGS84)
- latitude (en dégrés décimaux, WGS84)
- geo_score : indice de similarité fournit par le moteur de géocodage
- geo_type : "housenumber" = n° trouvé, "interpolation" = n° interpolé, "street" = voie trouvée, "locality" = lieu-dit (ou position de la mairie) pour les adresses indiquées "MAIRIE" ou "HOTEL DE VILLE",
"municipality" = position de la commune car l'adresse n'a pas été trouvée.
- geo_adresse : libellé de l'adresse trouvée
- geo_id : id dans le référentiel BAN, ou BANO (si commence par "BANO_")


**Les données contenues dans les colonnes ajoutées par le géocodage sont sous licence ODbL 1.0.**

Contact: adresse at data point gouv point fr
