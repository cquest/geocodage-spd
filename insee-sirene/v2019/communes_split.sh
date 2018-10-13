#! /bin/bash

echo $1
mkdir -p communes

# entête des fichiers CSV par commune
HEAD=$(zcat $1 | head -n 1)
for i in `zcat $1 | csvcut -c codecommuneetablissement | sort -u | grep '^[0-9]'`; do
  echo $HEAD > communes/$i.csv;
done

# split des fichiers
zcat $1 | tail -n +2 | awk -v FPAT='[^,]*|"([^"]|"")*"' '{print >> "communes/"$21".csv"}'
