#! /bin/bash

echo "1/5 : Remise en forme du CSV (UTF8, quotes, etc)"
csvclean $1 -e 'ISO8859-1' -d ';'
rm -f sirene.csv; mv $(echo $1 | sed 's/.csv/_out.csv/') sirene.csv

#echo "2/5 : Suppression des libellés et dénormalisations du COG"
#csvcut sirene.csv -v -C RPET,LIBREG,LIBCOM,EPCI,LIBNATETAB,LIBAPET,LIBTEFET,LIBNJ,LIBAPEN,LIBTEFEN,ARRONET,CTONET,DU,UU,TU,ZEMET > sirene-mini.csv

mkdir -p sirene
mkdir -p sirene_geo
mkdir -p cache_geo

echo "2/5 : découpage en fichiers départementaux"
for d in `seq -w 1 19` 2A 2B `seq 21 99`; do
  head -n 1 sirene.csv > sirene_$d.csv
done
# split du fichier national sur DEPET (25ème colonne)
awk -v FPAT='[^,]*|"([^"]|"")*"' '{ print >> "sirene_"$25".csv"}' sirene.csv
cat sirene_.csv >> sirene_99.csv
rm sirene_DEPET.csv

# découpage Paris
seq 101 120 | sed 's/ /\n/g' | \
    parallel -t csvgrep sirene_75.csv -c COMET -m {} \> sirene_75{}.csv

# découpage DOM
seq 1 6 | sed 's/ /\n/g' | \
    parallel -t csvgrep sirene_97.csv -c COMET -r "^{}.*" \> sirene_97{}.csv

rm sirene_97.csv
rm sirene_75.csv
rm sirene_.csv
rm sirene_96.csv

echo "3/5 : géocodage par taille décroissante"
time wc -l sirene_*.csv | sort -n -r | grep 'sirene_.*.csv' -o | \
  parallel -j 36 -t  ./1b_sirene_geo.py {} \> {}.log

echo "4/5 : split par commune"
ls -1 geo-sirene_*.csv | parallel ./2_split_rsync.sh {}

echo "5/5 : fusion fichier national"
head -n 1 geo-sirene_01.csv > geo_sirene.csv
for f in geo-sirene_*.csv; do tail -n +2 $f >> geo_sirene.csv; done
gzip -9 geo_sirene.csv

mkdir -p "AAAA-MM"
mv communes "AAAA-MM"
cp Licence*.pdf "AAAA-MM" # licence
ls -1 geo-sirene_*.csv | parallel 7z a {}.7z {}
mv geo*.7z "AAAA-MM"
mv geo_sirene.csv.gz "AAAA-MM"
grep final -h *.log > AAAA-MM/stats.json

7z a AAAA-MM/logs.7z *.log

rsync "AAAA-MM" root@data.cquest.org:/var/www/html/data/geo_sirene/ -avz --progress

# extraction liste des CEDEX, libelles et code INSEE (DEP/COM)
echo 'cedex,libelle,insee' > cedex.csv; grep CEDEX sirene-mini.csv | csvcut -c 8,23,24 | grep CEDEX | sort -u | grep '^[0-9][0-9][0-9][0-9][0-9]' | sed 's/^\(.....\) /"\1,/;s/,\(...\)$/\1"/;s/,/","/g' >> cedex.csv
