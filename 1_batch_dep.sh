#! /bin/bash

mkdir -p sirene
mkdir -p sirene_geo

echo {01..19} 2A 2B {21..99} | sed 's/ /\n/g' | \
  parallel -j 24 -t csvgrep sirene_mini.csv -c DEPET -m {} \> sirene_{}.csv \; ./1b_sirene_geo.py sirene_{}.csv
