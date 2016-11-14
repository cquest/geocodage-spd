create table sirene_ape as select ape as co_ape, libape from (select apet700 as ape, libapet as libape from sirene group by 1,2 union select apen700 as ape, libapen as libape from sirene group by 1,2) as a group by 1,2;

create table sirene_natetab as select natetab as co_natetab, libnatetab from sirene group by 1,2;

create table sirene_tef as select tefet as co_tef, libtefet as libtef from sirene group by 1,2;

alter table sirene drop column libapet;
alter table sirene drop column libapen;
alter table sirene drop column libnatetab;
alter table sirene drop column libtefet;
alter table sirene drop column libtefen;

vacuum full sirene;
