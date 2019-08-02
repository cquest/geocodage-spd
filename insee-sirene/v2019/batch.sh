#! /bin/bash

mkdir -p data

echo "1/5 : téléchargement" # ------------------------------------------------------
wget -N https://files.data.gouv.fr/insee-sirene/StockEtablissement_utf8.zip

echo "2/5 : découpage en fichiers départementaux" # -------------------------------
rm -f data/dep_*.csv
unzip -p StockEtablissement_utf8.zip | awk -v FPAT='[^,]*|"([^"]|"")*"' '{ print >> "data/dep_"substr($21,1,2)".csv"}'
awk -v FPAT='[^,]*|"([^"]|"")*"' '{ print >> "data/dep_"$21".csv"}' data/dep_75.csv
awk -v FPAT='[^,]*|"([^"]|"")*"' '{ print >> "data/dep_"substr($21,1,3)".csv"}' data/dep_97.csv
rm -f data/dep_75.csv data/dep_97.csv data/dep_co.csv

cd ..
echo "3/5 : géocodage par taille décroissante" # ----------------------------------
# extrait la liste des anciens codes INSEE et nouveau correspondant
csvgrep -c POLE -r '^.+$' -t France2018.tsv -e iso8859-1 | csvcut -c 6,7,11,14 | sed 's/,//' > histo_depcom.csv

time wc -l v2019/data/dep_*.csv | sort -n -r | grep dep | sed 's/^.*_\(.*\).csv/\1/' | \
  parallel -j 36 -t ./geocode.py v2019/data/dep_{}.csv v2019/data/geo_siret_{}.csv.gz cache_geo/cache_addok_sirene_{}.csv.db \> v2019/data/geo_siret_{}.log
cd -
rm data/*.csv

echo "4/5 : split par commune" # ------------------------------------------------------
cd data
ls -1 geo_siret_*.csv.gz | parallel sh ../communes_split.sh {}
rm communes/.csv
cd -

echo "5/5 : fusion fichier national" # ------------------------------------------------
zcat data/geo_siret_01.csv.gz | head -n 1 | gzip -9 --rsyncable > StockEtablissement_utf8_geo.csv.gz
for f in data/geo_siret*.csv.gz; do zcat "$f" | tail -n +2 | gzip -9 --rsyncable >> StockEtablissement_utf8_geo.csv.gz ; done

# fichier séparé pour établissements actifs/fermés seuls
zcat StockEtablissement_utf8_geo.csv.gz \
| tee >(csvgrep -c etatAdministratifEtablissement -m "A" | gzip -9 --rsyncable > StockEtablissementActif_utf8_geo.csv.gz) >(csvgrep -c etatAdministratifEtablissement -m "F" | gzip -9 --rsyncable > StockEtablissementFerme_utf8_geo.csv.gz) > /dev/null

# ------------------------------------------------------
# récap stats
grep final -h data/*.log | jq -s '.' > data/stats.json
tar czf data/logs.tgz data/*.log

# rangement local
mkdir -p "AAAA-MM/dep"
mv data/geo_*.gz "AAAA-MM/dep"    # fichiers départementaux + logs
mv data/communes "AAAA-MM"    # fichiers communaux
mv data/stats.json "AAAA-MM"  # recap stats
mv data/logs.tgz "AAAA-MM"    # logs
mv *.gz "AAAA-MM"

# publication sur serveur
DIR=$(date -r StockEtablissement_utf8.zip +%Y-%m)
mv AAAA-MM $DIR
rsync $DIR root@data.cquest.org:/var/www/html/data/geo_sirene/v2019/$DIR -avz --progress
ssh root@data.cquest.org "cd /var/www/html/data/geo_sirene; rm last; ln -s $DIR last"
