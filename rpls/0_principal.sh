# création table postgres
psql -c "drop table if exists rpls ;
create table rpls (DROIT int,DEPCOM text,CODEPOSTAL text,libcom text,
  NUMVOIE text,INDREP text,TYPVOIE text,NOMVOIE text,
  NUMAPPT text,NUMBOITE text,ESC text,COULOIR text,ETAGE text,
  COMPLIDENT text,ENTREE text,BAT text,IMMEU text,COMPLGEO text,LIEUDIT text,
  QPV int,TYPECONST text,NBPIECE int,SURFHAB text,CONSTRUCT text,LOCAT text,PATRIMOINE text,
  ORIGINE int,FINAN int,FINANAUTRE text,CONV text,NUMCONV text,DATCONV text,
  NEWLOGT int,CUS int,DPEDATE text,DPEENERGIE text,DPESERRE text,
  SRU_EXPIR text,SRU_ALINEA text,CODSEGPATRIM text,LIBSEGPATRIM text);
"

# csv vers postgres pour les fichiers par région
for f in *.csv
do
  echo $f
  csvcut -C dep -d ';' -e 'iso8859-1' $f > /tmp/rpls.csv
  psql -c "\copy rpls from '/tmp/rpls.csv' with (format csv, header true)"
  rm /tmp/rpls.csv
done

# csv vers postgres pour les fichiers par département (ile de france)
for f in *_dep*.csv
do
  echo $f
  psql -c "\copy rpls from '$f' with (format csv, header true, delimiter ';', encoding 'iso8859-1')"
done

psql -c "  create index rpls_depcom on rpls (depcom);"

# export un fichier csv par département
for D in `seq -w 1 19` 2A 2B `seq 21 95` `seq 971 974`
do
  psql -c "\copy (SELECT * FROM rpls WHERE depcom like '$D%') to rpls_dep$D.csv with (format csv, header true)"
done

# géocodage des fichiers csv départementaux par taille décroissante
time wc -c rpls_dep*.csv | sort -n -r | grep 'rpls_dep.*.csv' -o | parallel -t python ../1_geocodage_rpls.py  {} \> {}.log

# génération du fichier nationale géocodé
head -n 1 geo-rpls_dep01.csv > geo-rpls.csv
for f in geo-rpls_*.csv
do
  tail -n +2 $f >> geo-rpls.csv
done
