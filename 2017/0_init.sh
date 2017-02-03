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

# découpage Paris
echo {101..120} | sed 's/ /\n/g' | \
    parallel -j 24 -t csvgrep sirene_75.csv -c COMET -m {} \> sirene_75{}.csv

# découpage DOM
echo {1..6} | sed 's/ /\n/g' | \
    parallel -j 24 -t csvgrep sirene_97.csv -c COMET -r "{}.*" \> sirene_97{}.csv

rm sirene_97.csv
rm sirene_75.csv

# géocodage par taille décroissante...
wc -l sirene_*.csv | sort -n -r | grep 'sirene_.*.csv' -o | \
  parallel -j 24 -t  ./1b_sirene_geo.py {} \> {}.log
