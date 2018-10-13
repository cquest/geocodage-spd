t=7
millesime=$1

echo "1/$t téléchargement des fichiers"
wget -nc https://media.interieur.gouv.fr/rna/rna_waldec_$millesime.zip
wget -nc https://media.interieur.gouv.fr/rna/rna_import_$millesime.zip

echo "2/$t décompression"
unzip rna_waldec_$millesime.zip
unzip rna_import_$millesime.zip

echo "3/$t ISO8859 > UTF8"
iconv -f 'ISO8859-1' -t 'utf8' rna_waldec_$millesime.csv > rna_waldec.csv
iconv -f 'ISO8859-1' -t 'utf8' rna_import_$millesime.csv > rna_import.csv

echo "4/$t remplacement de \n et \r dans le champ 'objet' et ajout code département"
time python 1_rna_clean.py rna_waldec.csv
time python 1_rna_clean.py rna_import.csv

echo "5/$t découpage en fichiers départementaux"
for d in {00..19} 2A 2B {21..98} {971..978}; do
  head -n 1 rna_waldec.csv > temp/rna_waldec_d$d.csv
done
time awk -v FPAT='[^,]*|"([^"]|"")*"' '{ print >> "temp/rna_waldec_d"$39".csv"}' rna_waldec.csv

cat rna_waldec_d0.csv >> rna_waldec_d00.csv
cat rna_waldec_d.csv >> rna_waldec_d00.csv
rm rna_waldec_d0.csv rna_waldec_d.csv rna_waldec_ddep.csv rna_waldec_dep.csv rna_waldec_d96.csv rna_waldec_d97.csv

echo "6/$t géocodage en //"
time wc -c rna_waldec_d*.csv | sort -n -r | grep 'rna_waldec_.*.csv' -o | \
  parallel -j 36 -t  python 2_rna_geo.py {} \> {}.log

echo "7/$t compression"
time wc -c geo-rna_waldec_d*.csv | sort -n -r | grep 'geo-rna_waldec_.*.csv' -o | \
  parallel -j 12 gzip -9 {}
