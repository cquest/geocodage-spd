# on supprime les fichiers vide (bug de traitement précédent)
find ./ -size 0c -delete
rm -f sirc*.csv

# récupération des nouveaux fichiers
for f in $(curl 'http://files.data.gouv.fr/sirene/' -s | grep 'sirene_[0-9]*_E_Q.zip' -o)
do
  wget http://files.data.gouv.fr/sirene/$f -nc -q
done
# traitement des fichiers en parallèle
# décompression, géocodage, compression et envoi sur serveur
ls -1 *.zip | sort -r | parallel -j 8 bash batch.sh {}

. ~/.keychain/t7500-sh
rsync geo-sirene* root@dedi2017.cquest.org:/var/www/html/data/geo_sirene/quotidien/ -a
