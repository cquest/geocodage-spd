# sirene_2017002_E_Q.zip > 2017002_E_Q
FILE=$(echo $1 | sed 's/.zip//;s/sirene_//')
GEO="geo-sirene_$FILE"

if [ ! -f $GEO.csv.gz ]
then
  . ~/.keychain/t7500-sh
  echo $1
  unzip -oq $1
  mv sirc*$FILE*.csv sirene_$FILE.csv
  cd ..
  ~/.virtualenvs/sirene/bin/python 1b_sirene_geo.py quotidien/sirene_$FILE.csv quotidien/$GEO.csv > quotidien/$GEO.log \
  && gzip -9 quotidien/$GEO.csv \
  && rm quotidien/sirene_$FILE.csv \
  && rsync quotidien/$GEO* root@dedi2017.cquest.org:/var/www/html/data/geo_sirene/quotidien/ -a
fi
