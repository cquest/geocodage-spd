# Scripts de géocodage de la base SIRENE

## Prérequis

Pour fonctionner, ces scripts ont besoin de deux instances du géocodeur addok:
- l'une avec la BAN
- la seconde avec la BANO

Ceci représente 36Go de RAM.
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


Contact: adresse at data point gouv point fr
