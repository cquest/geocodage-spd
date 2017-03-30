#! /bin/bash

echo "1/5 : Remise en forme du CSV (UTF8, quotes, etc)"
csvclean $1 -e 'ISO8859-1' -d ';'
mv *_out.csv sirene.csv

echo "2/5 : Suppression des libellés et dénormalisations du COG"
csvcut sirene.csv -v -C RPET,LIBREG,LIBCOM,EPCI,LIBNATETAB,LIBAPET,LIBTEFET,LIBNJ,LIBAPEN,LIBTEFEN,ARRONET,CTONET,DU,UU,TU,ZEMET > sirene-mini.csv

mkdir -p sirene
mkdir -p sirene_geo
mkdir -p cache_geo

echo "3/5 : découpage en fichiers départementaux"
for d in {01..19} 2A 2B {21..98}; do
  head -n 1 sirene-mini.csv > sirene_$d.csv
done
# split du fichier national sur DEPET (23ème colonne)
awk -v FPAT='[^,]*|"([^"]|"")*"' '{ print >> "sirene_"$23".csv"}' sirene-mini.csv

# découpage du fichier national en fichiers par département (DOM groupés)
#echo {01..19} 2A 2B {21..98} | sed 's/ /\n/g' | \
#  parallel -j 24 -t csvgrep sirene-mini.csv -c DEPET -m {} \> sirene_{}.csv

# découpage Paris
echo {101..120} | sed 's/ /\n/g' | \
    parallel -t csvgrep sirene_75.csv -c COMET -m {} \> sirene_75{}.csv

# découpage DOM
echo {1..6} | sed 's/ /\n/g' | \
    parallel -t csvgrep sirene_97.csv -c COMET -r "{}.*" \> sirene_97{}.csv

rm sirene_97.csv
rm sirene_75.csv

echo "4/5 : géocodage par taille décroissante"
time wc -c sirene_*.csv | sort -n -r | grep 'sirene_.*.csv' -o | \
  parallel -j 36 -t  ./1b_sirene_geo.py {} \> {}.log

echo "5/5 : split par commune"
ls -1 geo-sirene_*.csv | parallel ./2_split_rsync.sh {}

# extraction liste des CEDEX, libelles et code INSEE (DEP/COM)
echo 'cp,libelle,insee' > cedex.csv; grep CEDEX sirene-mini.csv | csvcut -c 8,23,24 | grep CEDEX | sort -u | grep '^[0-9]' | sed 's/^\(.....\) /"\1,/;s/,\(...\)$/\1"/;s/,/","/g' >> cedex.csv
