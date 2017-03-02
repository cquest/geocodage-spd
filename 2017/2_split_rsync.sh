#! /bin/bash

echo $1
mkdir -p communes

# entête des fichiers CSV par commune
for i in `csvcut -c 23,24 $1 | sort -u | sed 's/,//' | grep '^[0-9]'`; do
  head -n 1 geo-sirene_92.csv > 2017-01/communes/$i.csv;
done

# split des fichiers
tail -n +2 $1 | awk -v FPAT='[^,]*|"[^"]*"' '{print >> "communes/"$23$24".csv"}' 

