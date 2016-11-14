# Scripts postgresql pour importer les données SIRENE

## sirene_importe.sql

Crée la table **sirene** et importe le fichier CSV sans modification.

Les champs sont tous laissés en "TEXT".


## sirene_normalise.sql

Normalise la table sirene en supprimant les libellés stockés dans les tables.

Ce script crée les tables sirene_ape, sirene_natetab, sirene_tef, sirene_nj contenant les codes APE (ape), nature d'établissement (natetab), type d'effectif (tef) et nature juridique (nj) avec leurs libellés correspondants.

Les colonnes sont ensuite supprimées de la table **sirene** et la table est compactée (VACUUM FULL) pour récupérer l'espace gagné. La table finale fait 5Go.
