#! /bin/bash

# remise en forme du CSV au standard (UTF8, virgules, quote uniquement si nécessaire)
csvclean $1 -e 'ISO8859-1' -d ';'

mv *_out.csv sirene.csv

# suppression des libellés et dénormalisations du COG
csvcut sirene.csv -v -C RPET,LIBREG,LIBCOM,EPCI,LIBNATETAB,LIBAPET,LIBTEFET,LIBNJ,LIBAPEN,LIBTEFEN,ARRONET,CTONET,DU,UU,TU,ZEMET > sirene-mini.csv

mkdir -p sirene
mkdir -p sirene_geo

# découpage du fichier national en fichiers par département (DOM groupés)
echo {01..19} 2A 2B {21..98} | sed 's/ /\n/g' | \
  parallel -j 24 -t csvgrep sirene-mini.csv -c DEPET -m {} \> sirene_{}.csv
# géocodage par taille décroissante...
wc -l sirene_*.csv | sort -n -r | grep ...csv -o | sed 's/.csv//' | \
  parallel -j 24 -t  ./1b_sirene_geo.py sirene_{}.csv \> sirene_{}.csv.log
