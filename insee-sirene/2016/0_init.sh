#! /bin/bash

# décompression du fichier ZIP d'origine
unzip sirc*.zip

# remise en forme du CSV au standard (UTF8, virgules, quote uniquement si nécessaire)
csvclean sirc*.csv -e 'ISO8859-1' -d ';'

# suppression des libellés et dénormalisations du COG
csvcut sirc*_out.csv -v -C RPET,LIBREG,LIBCOM,EPCI,LIBNATETAB,LIBAPET,LIBTEFET,LIBNJ,LIBAPEN,LIBTEFEN,ARRONET,CTONET,DU,UU,TU,ZEMET > sirene_mini.csv

# préparation CSV position des communes
wget -nc https://www.data.gouv.fr/_uploads/resources/communes-plus-20140630-csv.zip
unzip communes-plus-20140630-csv.zip

# position des mairies
wget -nc http://www.ideeslibres.org/opendata/spbdlv2/organismes.csv.zip
unzip organismes.csv.zip
csvcut organismes.csv -c codeinsee,lat,lng -d ';' > communes_mairies.csv

