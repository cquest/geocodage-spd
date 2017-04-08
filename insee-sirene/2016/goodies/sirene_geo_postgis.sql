/* ajoute la colonne géométrique */
alter table sirene_geo add geom geometry(point, 4326);

/* mise à jour de la colonne géométrique */
update sirene_geo set geom = st_setsrid(st_makepoint(longitude, latitude),4326);

/* création de l'index géométrique */
create index sirene_geo_geom on sirene_geo using gist (geom);
