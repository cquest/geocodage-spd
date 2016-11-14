# Scripts postgresql pour importer les données SIRENE

## sirene2pgsql.sql

Crée la table **sirene** et importe le fichier CSV sans modification.

Les champs sont tous laissés en "TEXT".


## sirene_normalise.sql

Normalise la table sirene en supprimant les libellés stockés dans les tables.
Ce script crée les tables sirene_ape, sirene_natetab, sirene_tef contenant les codes APE, nature d'établissement et type d'effectif avec leurs libellés correspondants.
Les colonnes sont ensuite supprimées de la table **sirene** et la table est compactée (VACUUM FULL) pour récupérer l'espace gagné.
