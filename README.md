# Scripts de géocodage des données du Service Public de la Donnée

Ces scripts s'appuient sur le moteur de géocodage addok développé par Etalab.

Pour obtenir une couverture maximale, deux instances d'addok sont utilisés, l'une s'appuyant sur la BAN (Base Adresse Nationale) elle même faisant partie du Service Public de la Donnée, la seconde sur la BANO (produite par OpenStreetMap France) afin de compléter la BAN en particulier sur les localisations des lieux-dits.

Pour accélérer le géocodage et tirer parti des multiples coeurs disponibles dans nos machines, le fichier national est découpé par département et chaque fichier départemental est géocodé en paralèlle.

Un script python assure le double géocodage et détermine la meilleure réponse. Il tente aussi de géocoder les différentes adresses et variantes des adresses présentes dans les fichiers d'origine.

Ce script est exécuté en paralèlle à l'aide de la commande GNU parallel.

## SIRENE

## RNA
