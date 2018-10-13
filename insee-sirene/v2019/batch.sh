mkdir -p data

echo "1/5 : téléchargement"
# récupération des URL des fichiers
curl 'https://www.data.gouv.fr/api/1/datasets/5b7ffc618b4c4169d30727e0/' -s \
  | jq .resources[].url -r \
  | grep stocketablissement-utf8.zip \
  | sort | tail -n 1> urls.txt
wget -nc -i urls.txt

echo "1b/5 : décompression"
unzip stocketablissement-utf8.zip

echo "2/5 : découpage en fichiers départementaux"
awk -v FPAT='[^,]*|"([^"]|"")*"' '{ print >> "data/dep_"substr($21,1,2)".csv"}' StockEtablissement_utf8.csv
awk -v FPAT='[^,]*|"([^"]|"")*"' '{ print >> "data/dep_"$21".csv"}' data/dep_75.csv
awk -v FPAT='[^,]*|"([^"]|"")*"' '{ print >> "data/dep_"substr($21,1,3)".csv"}' data/dep_97.csv
rm data/dep_75.csv data/dep_97.csv data/dep_co.csv
rm stocketablissement-utf8.csv

cd ..
echo "3/5 : géocodage par taille décroissante"

# extrait la liste des anciens codes INSEE et nouveau correspondant
csvgrep -c POLE -r '^.+$' -t France2018.tsv -e iso8859-1 | csvcut -c 6,7,11,14 | sed 's/,//' > histo_depcom.csv

time wc -l v2019/data/dep_*.csv | sort -n -r | grep dep | sed 's/^.*_\(.*\).csv/\1/' | \
  parallel -j 36 -t ./geocode.py v2019/data/dep_{}.csv v2019/data/geo_siret_{}.csv.gz cache_geo/cache_addok_sirene_{}.csv.db \> v2019/data/geo_siret_{}.log
cd -
rm data/*.csv

echo "4/5 : split par commune"
cd data
ls -1 geo_siret_*.csv.gz | parallel sh ../communes_split.sh {}
rm communes/.csv
cd -

echo "5/5 : fusion fichier national"
head -n 1 data/geo_dep_01.csv | gzip -9 > StockEtablissement_utf8_geo.csv.gz
for f in data/geo_dep*.csv.gz; do zcat "$f" | tail -n +2 | gzip -9 >> StockEtablissement_utf8_geo.csv.gz ; done

# fichier séparé pour établissements actifs seuls
zcat StockEtablissement_utf8_geo.csv.gz | csvgrep -c etatadministratifetablissement -m "A" | gzip -9 > StockEtablissementActif_utf8_geo.csv.gz

rsync *.gz root@data.cquest.org:/var/www/html/data/geo_sirene/v2019/AAAA-MM -av --progress
rsync data/geo_*.gz root@data.cquest.org:/var/www/html/data/geo_sirene/v2019/AAAA-MM -av --progress

grep final -h data/*.log | jq -s '.' > data/stats.json # récap stats
tar czf data/logs.tgz data/*.log

rsync data/stats.json root@data.cquest.org:/var/www/html/data/geo_sirene/v2019/AAAA-MM -av --progress
rsync data/logs.tgz root@data.cquest.org:/var/www/html/data/geo_sirene/v2019/AAAA-MM -av --progress
rsync data/communes/ root@data.cquest.org:/var/www/html/data/geo_sirene/v2019/AAAA-MM/communes -avz --progress

mv data/geo_*.gz "AAAA-MM" # fichiers départementaux + logs
mv communes "AAAA-MM" # fichiers communaux
mv *.gz "AAAA-MM"

# extraction liste des CEDEX, libelles et code INSEE (DEP/COM)
echo 'cedex,libelle,insee' > cedex.csv; grep CEDEX sirene-mini.csv | csvcut -c 8,23,24 | grep CEDEX | sort -u | grep '^[0-9][0-9][0-9][0-9][0-9]' | sed 's/^\(.....\) /"\1,/;s/,\(...\)$/\1"/;s/,/","/g' >> cedex.csv
