echo "siren,statutdiffusionunitelegale,unitepurgeeunitelegale,datecreationunitelegale,sigleunitelegale,sexeunitelegale,prenom1unitelegale,prenom2unitelegale,prenom3unitelegale,prenom4unitelegale,prenomusuelunitelegale,pseudonymeunitelegale,identifiantassociationunitelegale,trancheeffectifsunitelegale,anneeeffectifsunitelegale,datederniertraitementunitelegale,nombreperiodesunitelegale,categorieentreprise,anneecategorieentreprise,datedebut,etatadministratifunitelegale,nomunitelegale,nomusageunitelegale,denominationunitelegale,denominationusuelle1unitelegale,denominationusuelle2unitelegale,denominationusuelle3unitelegale,categoriejuridiqueunitelegale,activiteprincipaleunitelegale,nomenclatureactiviteprincipaleunitelegale,nicsiegeunitelegale,economiesocialesolidaireunitelegale,caractereemployeurunitelegale"

zcat $1 | jq -s -r '.[]|[.siren,.uniteLegale.statutDiffusionUniteLegale,.uniteLegale.unitePurgeeUniteLegale,.uniteLegale.dateCreationUniteLegale,.uniteLegale.sigleUniteLegale,.uniteLegale.sexeUniteLegale,.uniteLegale.prenom1UniteLegale,.uniteLegale.prenom2UniteLegale,.uniteLegale.prenom3UniteLegale,.uniteLegale.prenom4UniteLegale,.uniteLegale.prenomUsuelUniteLegale,.uniteLegale.pseudonymeUniteLegale,.uniteLegale.identifiantAssociationUniteLegale,.uniteLegale.trancheEffectifsUniteLegale,.uniteLegale.anneeEffectifsUniteLegale,.uniteLegale.dateDernierTraitementUniteLegale,.uniteLegale.nombrePeriodesUniteLegale,.uniteLegale.categorieEntreprise,.uniteLegale.anneeCategorieEntreprise,.uniteLegale.dateDebut,.uniteLegale.etatAdministratifUniteLegale,.uniteLegale.nomUniteLegale,.uniteLegale.nomUsageUniteLegale,.uniteLegale.denominationUniteLegale,.uniteLegale.denominationUsuelle1UniteLegale,.uniteLegale.denominationUsuelle2UniteLegale,.uniteLegale.denominationUsuelle3UniteLegale,.uniteLegale.categorieJuridiqueUniteLegale,.uniteLegale.activitePrincipaleUniteLegale,.uniteLegale.nomenclatureActivitePrincipaleUniteLegale,.uniteLegale.nicSiegeUniteLegale,.uniteLegale.economieSocialeSolidaireUniteLegale,.uniteLegale.caractereEmployeurUniteLegale] | @csv'