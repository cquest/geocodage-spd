#! /bin/bash

# décompression du fichier ZIP d'origine
unzip sirc*.zip

# remise en forme du CSV au standard (UTF8, virgules, quote uniquement si nécessaire)
csvclean sirc*.csv -e 'ISO8859-1' -d ';'

# suppression des libellés et dénormalisations du COG
csvcut sirc*_out.csv -v -C RPET,LIBREG,LIBCOM,EPCI,LIBNATETAB,LIBAPET,LIBTEFET,LIBNJ,LIBAPEN,LIBTEFEN,ARRONET,CTONET,DU,UU,TU,ZEMET > sirene_mini.csv

# préparation base sqlite avec COG
wget -nc http://www.insee.fr/fr/methodes/nomenclatures/cog/telechargement/2016/txt/comsimp2016.zip
unzip comsimp2016.zip
