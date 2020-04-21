#! /usr/bin/python3
import sys
import csv
import json
import re
import gzip

# modules installés par pip
import requests
import sqlite3
import marshal

# modules locaux
from normadresse.normadresse import abrev

score_min = 0.30

# URL à appeler pour géocodage BAN, BANO et POI OSM
addok_ban = 'http://localhost:7979/search/'
addok_bano = 'http://localhost:7878/search'
addok_poi = 'http://localhost:7777/search'

geocode_count = 0

# effecture une req. sur l'API de géocodage
def geocode(api, params, l4):
    params['autocomplete'] = 0
    params['q'] = params['q'].strip()
    try:
        r = requests.get(api, params)
        j = json.loads(r.text)
        global geocode_count
        geocode_count += 1
        if 'features' in j and len(j['features']) > 0:
            j['features'][0]['l4'] = l4
            j['features'][0]['geo_l4'] = ''
            j['features'][0]['geo_l5'] = ''
            if api != addok_poi:
                # regénération lignes 4 et 5 normalisées
                name = j['features'][0]['properties']['name']

                ligne4 = re.sub(r'\(.*$', '', name).strip()
                ligne4 = re.sub(r',.*$', '', ligne4).strip()
                ligne5 = ''
                j['features'][0]['geo_l4'] = abrev(ligne4).upper()
                if '(' in name:
                    ligne5 = re.sub(r'.*\((.*)\)', r'\1', name).strip()
                    j['features'][0]['geo_l5'] = abrev(ligne5).upper()
                if ',' in name:
                    ligne5 = re.sub(r'.*,(.*)', r'\1', name).strip()
                    j['features'][0]['geo_l5'] = abrev(ligne5).upper()
                # ligne 4 et 5 identiques ? on supprime la 5
                if j['features'][0]['geo_l5'] == j['features'][0]['geo_l4']:
                    j['features'][0]['geo_l5'] = ''
            return(j['features'][0])
        else:
            return(None)
    except:
        print(json.dumps({'action': 'erreur', 'api': api,
                         'params': params, 'l4': l4}))
        return(None)


def trace(txt):
    if False:
        print(txt)


if len(sys.argv) > 2:
    stock = False
    sirene_csv = csv.reader(open(sys.argv[1], 'r', encoding='utf-8'),
                            delimiter=',')
    sirene_geo = csv.writer(gzip.open(sys.argv[2], 'wt', compresslevel=9))
    conn = None
    if len(sys.argv) > 3:
        conn = sqlite3.connect(sys.argv[3])
        conn.execute('''CREATE TABLE IF NOT EXISTS cache_addok (adr text, geo text,
                     score numeric)''')
        conn.execute('CREATE INDEX IF NOT EXISTS cache_addok_adr ON cache_addok (adr)')  # noqa
        conn.execute('DELETE FROM cache_addok WHERE score<0.7')
else:
    stock = True
    sirene_csv = csv.reader(open(sys.argv[1], 'r'))
    sirene_geo = csv.writer(open('geo-'+sys.argv[1], 'w'))
    conn = sqlite3.connect('cache_geo/cache_addok_'+sys.argv[1]+'.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS cache_addok (adr text, geo text,
                 score numeric)''')
    conn.execute('CREATE INDEX IF NOT EXISTS cache_addok_adr ON cache_addok (adr)')  # noqa
    conn.execute('DELETE FROM cache_addok WHERE score<0.7')

# chargement de la liste des communes et lat/lon
communes = csv.DictReader(open('communes-plus-20140630.csv', 'r'))
commune_insee = {}
for commune in communes:
    commune_insee[commune['\ufeffinsee']] = {'lat': round(float(commune['lon_centro']), 6),
                                             'lon': round(float(commune['lat_centro']), 6)}

# chargement des changements de codes INSEE
histo = csv.DictReader(open('histo_depcom.csv', 'r'))
histo_depcom = {}
for commune in histo:
    histo_depcom[commune['DEPCOM']] = commune

header = None
ok = 0
total = 0
cache = 0
numbers = re.compile('(^[0-9]*)')
stats = {'action': 'progress', 'housenumber': 0, 'interpolation': 0,
         'street': 0, 'locality': 0, 'municipality': 0, 'vide': 0,
         'townhall': 0, 'poi': 0, 'fichier': sys.argv[1]}
score_total = 0
score_count = 0
score_variance = 0

# regexp souvent utilisées
ccial = r'((C|CTRE|CENTRE|CNTRE|CENT|ESPACE) (CCIAL|CIAL|COM|COMM|COMMERC|COMMERCIAL)|CCR|C\.CIAL|C\.C|CCIAL|CC)'  # noqa

header = ['siren',
          'nic',
          'siret',
          'statutDiffusionEtablissement',
          'dateCreationEtablissement',
          'trancheEffectifsEtablissement',
          'anneeEffectifsEtablissement',
          'activitePrincipaleRegistreMetiersEtablissement',
          'dateDernierTraitementEtablissement',
          'etablissementSiege',
          'nombrePeriodesEtablissement',
          'complementAdresseEtablissement',
          'numeroVoieEtablissement',
          'indiceRepetitionEtablissement',
          'typeVoieEtablissement',
          'libelleVoieEtablissement',
          'codePostalEtablissement',
          'libelleCommuneEtablissement',
          'libelleCommuneEtrangerEtablissement',
          'distributionSpecialeEtablissement',
          'codeCommuneEtablissement',
          'codeCedexEtablissement',
          'libelleCedexEtablissement',
          'codePaysEtrangerEtablissement',
          'libellePaysEtrangerEtablissement',
          'complementAdresse2Etablissement',
          'numeroVoie2Etablissement',
          'indiceRepetition2Etablissement',
          'typeVoie2Etablissement',
          'libelleVoie2Etablissement',
          'codePostal2Etablissement',
          'libelleCommune2Etablissement',
          'libelleCommuneEtranger2Etablissement',
          'distributionSpeciale2Etablissement',
          'codeCommune2Etablissement',
          'codeCedex2Etablissement',
          'libelleCedex2Etablissement',
          'codePaysEtranger2Etablissement',
          'libellePaysEtranger2Etablissement',
          'dateDebut',
          'etatAdministratifEtablissement',
          'enseigne1Etablissement',
          'enseigne2Etablissement',
          'enseigne3Etablissement',
          'denominationUsuelleEtablissement',
          'activitePrincipaleEtablissement',
          'nomenclatureActivitePrincipaleEtablissement',
          'caractereEmployeurEtablissement',
          'longitude',
          'latitude',
          'geo_score',
          'geo_type',
          'geo_adresse',
          'geo_id',
          'geo_ligne',
          'geo_l4',
          'geo_l5']

sirene_geo.writerow(header)

for et in sirene_csv:
    # on ne tente pas le géocodage des adresses hors de France
    if et[20] == '' or re.match(r'^(978|98|99)',et[20]):
        row = et+['', '', 0, '', '', '', '', '', '']
        sirene_geo.writerow(row)
    else:
        total = total + 1
        # fichier SIRENE (stock et quotidien)
        #  géocodage de l'adresse géographique
        #  au cas où numvoie contiendrait autre chose que des chiffres...
        numvoie = numbers.match(et[12]).group(0)
        indrep = et[13]
        typvoie = et[14]
        libvoie = et[15]
        ligne4N = ''
        ligne4D = ''
        # code INSEE de la commune
        depcom = et[20]

        if numvoie == '' and numbers.match(libvoie).group(0):
            numvoie = numbers.match(libvoie).group(0)
            libvoie = libvoie[len(numvoie):]

        # typvoie incorrect ou à désabréger pour un score cohérent
        typ_abrege = {'PRO': 'PROMENADE',
                      'AV': 'AVENUE',
                      'BD': 'BOULEVARD',
                      'PL': 'PLACE',
                      'CAR': 'CARREFOUR',
                      'PAS': 'PASSAGE',
                      'IMP': 'IMPASSE'}
        if typvoie in typ_abrege:
            typvoie == typ_abrege[typvoie]

        # élimination des LD / LIEU-DIT des libellés
        if typvoie in ['LD', 'HAM']:
            typvoie = ''
        libvoie = re.sub(r'^PRO ', 'PROMENADE ', libvoie)
        libvoie = re.sub(r'^(LD|HAM|HAMMEAU) ', '', libvoie)
        libvoie = re.sub(r'^LIEU(.|)DIT ', '', libvoie)
        libvoie = re.sub(r'^ADRESSE INCOMPLETE.*', '', libvoie)
        libvoie = re.sub(r'^SANS DOMICILE FIXE', '', libvoie)
        libvoie = re.sub(r'^COMMUNE DE RATTACHEMENT', '', libvoie)

        # code insee inconnu ?
        if depcom != '' and depcom < '97000' and depcom in histo_depcom:
            if libvoie != '':
                libvoie = libvoie + " " + histo_depcom[depcom]['NCC']
            depcom = histo_depcom[depcom]['POLE']

        # ou de la ligne 4 normalisée
        ligne4G = ('%s%s %s %s' % (numvoie, indrep, typvoie, libvoie)).strip()
        if et[11] != '':
            ligne4D = ('%s%s %s %s %s' % (numvoie, indrep, typvoie, libvoie, et[11])).strip()

        try:
            cursor = conn.execute('SELECT * FROM cache_addok WHERE adr=?',
                                  ('%s|%s|%s|%s' % (depcom, ligne4G,
                                                    ligne4N, ligne4D), ))
            g = cursor.fetchone()
        except:
            g = None
        if g is not None:
            source = marshal.loads(g[1])
            cache = cache+1
        else:

            trace('%s / %s / %s' % (ligne4G, ligne4D, ligne4N))

            # géocodage BAN (ligne4 géo, déclarée ou normalisée si pas trouvé
            # ou score insuffisant)
            ban = None
            if ligne4G != '':
                ban = geocode(addok_ban, {'q': ligne4G, 'citycode': depcom,
                                          'limit': '1'}, 'G')
            if (ban is None or ban['properties']['score'] < score_min
               and ligne4N != ligne4G and ligne4N != ''):
                ban = geocode(addok_ban, {'q': ligne4N, 'citycode': depcom,
                                          'limit': '1'}, 'N')
                trace('+ ban  L4N')
            if (ban is None or ban['properties']['score'] < score_min
               and ligne4D != ligne4N and ligne4D != ligne4G
               and ligne4D != ''):
                ban = geocode(addok_ban, {'q': ligne4D, 'citycode': depcom,
                                          'limit': '1'}, 'D')
                trace('+ ban  L4D')

            # géocodage BANO (ligne4 géo, déclarée ou normalisée si pas trouvé
            # ou score insuffisant)
            bano = None
            if ban is None or ban['properties']['score'] < 0.9:
                if ligne4G != '':
                    bano = geocode(addok_bano, {'q': ligne4G,
                                                'citycode': depcom,
                                                'limit': '1'}, 'G')
                if (bano is None or bano['properties']['score'] < score_min
                   and ligne4N != ligne4G and ligne4N != ''):
                    bano = geocode(addok_bano, {'q': ligne4N,
                                                'citycode': depcom,
                                                'limit': '1'}, 'N')
                    trace('+ bano L4N')
                if (bano is None or bano['properties']['score'] < score_min
                   and ligne4D != ligne4N and ligne4D != ligne4G
                   and ligne4D != ''):
                    bano = geocode(addok_bano, {'q': ligne4D,
                                                'citycode': depcom,
                                                'limit': '1'}, 'D')
                    trace('+ bano L4D')

            if ban is not None:
                ban_score = ban['properties']['score']
                ban_type = ban['properties']['type']
                if ['village', 'town', 'city'].count(ban_type) > 0:
                    ban_type = 'municipality'
            else:
                ban_score = 0
                ban_type = ''
            if bano is not None:
                bano_score = bano['properties']['score']
                if bano['properties']['type'] == 'place':
                    bano['properties']['type'] = 'locality'
                bano['properties']['id'] = 'BANO_'+bano['properties']['id']
                if bano['properties']['type'] == 'housenumber':
                    bano['properties']['id'] = '%s_%s' % (bano['properties']['id'],  bano['properties']['housenumber'])
                bano_type = bano['properties']['type']
                if ['village', 'town', 'city'].count(bano_type) > 0:
                    bano_type = 'municipality'
            else:
                bano_score = 0
                bano_type = ''

            # choix de la source
            source = None
            score = 0

            # on a un numéro... on cherche dessus
            if numvoie != '':
                # numéro trouvé dans les deux bases, on prend BAN
                # sauf si score inférieur de 20% à BANO
                if (ban_type == 'housenumber' and bano_type == 'housenumber'
                   and ban_score > score_min and ban_score >= bano_score/1.2):
                    source = ban
                    score = ban['properties']['score']
                elif ban_type == 'housenumber' and ban_score > score_min:
                    source = ban
                    score = ban['properties']['score']
                elif bano_type == 'housenumber' and bano_score > score_min:
                    source = bano
                    score = bano['properties']['score']
                # on cherche une interpollation dans BAN
                elif ban is None or ban_type == 'street' and int(numvoie) > 2:
                    ban_avant = geocode(addok_ban, {'q': '%s %s %s' % (int(numvoie)-2, typvoie, libvoie), 'citycode': depcom, 'limit': '1'}, 'G')
                    ban_apres = geocode(addok_ban, {'q': '%s %s %s' % (int(numvoie)+2, typvoie, libvoie), 'citycode': depcom, 'limit': '1'}, 'G')
                    if ban_avant is not None and ban_apres is not None:
                        if (ban_avant['properties']['type'] == 'housenumber' and
                           ban_apres['properties']['type'] == 'housenumber' and
                           ban_avant['properties']['score'] > 0.5 and
                           ban_apres['properties']['score'] > score_min):
                            source = ban_avant
                            score = ban_avant['properties']['score']/2
                            source['geometry']['coordinates'][0] = round((ban_avant['geometry']['coordinates'][0]+ban_apres['geometry']['coordinates'][0])/2,6)
                            source['geometry']['coordinates'][1] = round((ban_avant['geometry']['coordinates'][1]+ban_apres['geometry']['coordinates'][1])/2,6)
                            source['properties']['score'] = (ban_avant['properties']['score']+ban_apres['properties']['score'])/2
                            source['properties']['type'] = 'interpolation'
                            source['properties']['id'] = ''
                            source['properties']['label'] = numvoie + ban_avant['properties']['label'][len(ban_avant['properties']['housenumber']):]

            # on essaye sans l'indice de répétition (BIS, TER qui ne correspond pas ou qui manque en base)
            if source is None and ban is None and indrep != '':
                trace('supp. indrep BAN : %s %s %s' % (numvoie, typvoie, libvoie))
                addok = geocode(addok_ban, {'q': '%s %s %s' % (numvoie, typvoie, libvoie), 'citycode': depcom, 'limit': '1'}, 'G')
                if addok is not None and addok['properties']['type'] == 'housenumber' and addok['properties']['score'] > score_min:
                    addok['properties']['type'] = 'interpolation'
                    source = addok
                    trace('+ ban  L4G-indrep')
            if source is None and bano is None and indrep != '':
                trace('supp. indrep BANO: %s %s %s' % (numvoie, typvoie, libvoie))
                addok = geocode(addok_bano, {'q': '%s %s %s' % (numvoie, typvoie, libvoie), 'citycode': depcom, 'limit': '1'}, 'G')
                if addok is not None and addok['properties']['type'] == 'housenumber' and addok['properties']['score'] > score_min:
                    addok['properties']['type'] = 'interpolation'
                    source = addok
                    trace('+ bano L4G-indrep')

            # pas trouvé ? on cherche une rue
            if source is None and typvoie != '':
                if ban_type == 'street' and bano_type == 'street' and ban_score > score_min and ban_score >= bano_score/1.2:
                    source = ban
                    score = ban['properties']['score']
                elif ban_type == 'street' and ban_score > score_min:
                    source = ban
                elif bano_type == 'street' and bano_score > score_min:
                    source = bano

            # pas trouvé ? on cherche sans numvoie
            if source is None and numvoie != '':
                trace('supp. numvoie : %s %s %s' % (numvoie, typvoie, libvoie))
                addok = geocode(addok_ban, {'q': '%s %s' % (typvoie, libvoie), 'citycode': depcom, 'limit': '1'}, 'G')
                if addok is not None and addok['properties']['type'] == 'street' and addok['properties']['score'] > score_min:
                    source = addok
                    trace('+ ban  L4G-numvoie')
            if source is None and numvoie != '':
                addok = geocode(addok_bano, {'q': '%s %s' % (typvoie, libvoie), 'citycode': depcom, 'limit': '1'}, 'G')
                if addok is not None and addok['properties']['type'] == 'street' and addok['properties']['score'] > score_min:
                    source = addok
                    trace('+ bano L4G-numvoie')

            # toujours pas trouvé ? tout type accepté...
            if source is None:
                if ban_score > score_min and ban_score >= bano_score*0.8:
                    source = ban
                elif ban_score > score_min:
                    source = ban
                elif bano_score > score_min:
                    source = bano

            # vraiment toujours pas trouvé comme adresse ?
            # on cherche dans les POI OpenStreetMap...
            if source is None:
                # Mairies et Hôtels de Ville...
                if ['MAIRIE','LA MAIRIE','HOTEL DE VILLE'].count(libvoie) > 0:
                    poi = geocode(addok_poi, {'q': 'hotel de ville', 'poi': 'townhall', 'citycode': depcom, 'limit': '1'}, 'G')
                    if poi is not None and poi['properties']['score'] > score_min:
                        source = poi
                # Gares...
                elif ['GARE', 'GARE SNCF', 'LA GARE'].count(libvoie) > 0:
                    poi = geocode(addok_poi, {'q': 'gare', 'poi': 'station', 'citycode': depcom, 'limit': '1'}, 'G')
                    if poi is not None and poi['properties']['score'] > score_min:
                        source = poi
                # Centres commerciaux...
                elif re.match(ccial, libvoie) is not None:
                    poi = geocode(addok_poi, {'q': re.sub(ccial, '\1 Galerie Marchande', libvoie), 'poi': 'mall', 'citycode': depcom, 'limit': '1'}, 'G')
                    if poi is not None and poi['properties']['score'] > 0.5:
                        source = poi
                elif re.match(ccial,libvoie) is not None:
                    poi = geocode(addok_poi, {'q': re.sub(ccial, '\1 Centre Commercial', libvoie), 'citycode': depcom, 'limit': '1'}, 'G')
                    if poi is not None and poi['properties']['score'] > 0.5:
                        source = poi
                # Aéroports et aérodromes...
                elif re.match(r'(AEROPORT|AERODROME)', libvoie) is not None:
                    poi = geocode(addok_poi, {'q': libvoie, 'poi': 'aerodrome', 'citycode': depcom, 'limit': '1'}, 'G')
                    if poi is not None and poi['properties']['score'] > score_min:
                        source = poi
                elif re.match(r'(AEROGARE|TERMINAL)', libvoie) is not None:
                    poi = geocode(addok_poi, {'q': re.sub(r'(AEROGARE|TERMINAL)', '', libvoie)+' terminal', 'poi': 'terminal', 'citycode': depcom, 'limit': '1'}, 'G')
                    if poi is not None and poi['properties']['score'] > score_min:
                        source = poi

                # recherche tout type de POI à partir du type et libellé de voie
                if source is None:
                    poi = geocode(addok_poi, {'q': typvoie+' '+libvoie,
                                              'citycode': depcom,
                                              'limit': '1'}, 'G')
                    if poi is not None and poi['properties']['score'] > 0.7:
                        source = poi

                if source is not None:
                    if source['properties']['poi'] != 'yes':
                        source['properties']['type'] = source['properties']['type']+'.'+source['properties']['poi']
                    print(json.dumps({'action': 'poi', 'adr_insee': depcom,
                                      'adr_texte': libvoie, 'poi': source},
                                     sort_keys=True))

            if source is not None and score == 0:
                score = source['properties']['score']

            # on conserve le résultat dans le cache sqlite
            if conn:
                key = ('%s|%s|%s|%s' % (depcom, ligne4G, ligne4N, ligne4D))
                cursor = conn.execute('INSERT INTO cache_addok VALUES (?,?,?)',
                                      (key, marshal.dumps(source), score))

        if source is None:
            # attention latitude et longitude sont inversées dans le fichier
            # CSV et donc la base sqlite
            row = et+['', '', 0, '', '', '', '', '', '']
            try:
                row = et+[commune_insee[depcom]['lon'],
                          commune_insee[depcom]['lat'],
                          0, 'municipality', '', commune_insee[i], '', '', '']
                if ligne4G.strip() != '':
                    if typvoie == '' and ['CHEF LIEU', 'CHEF-LIEU',
                                          'LE CHEF LIEU', 'LE CHEF-LIEU',
                                          'BOURG', 'LE BOURG', 'AU BOURG',
                                          'VILLAGE', 'AU VILLAGE',
                                          'LE VILLAGE'].count(libvoie) > 0:
                        stats['locality'] += 1
                        ok += 1
                    else:
                        stats['municipality'] += 1
                        print(json.dumps({'action': 'manque',
                                          'siret': et[0]+et[1],
                                          'adr_comm_insee': depcom,
                                          'adr_texte': ligne4G.strip(),
                                          'adr_norm': ligne4N.strip(),
                                          'adr_decl': ligne4D.strip()},
                                         sort_keys=True))
                else:
                    stats['vide'] += 1
                    ok += 1
            except:
                pass
            sirene_geo.writerow(row)
        else:
            ok += 1
            if ['village', 'town', 'city'].count(source['properties']['type']) > 0:
                source['properties']['type'] = 'municipality'
            stats[re.sub(r'\..*$', '', source['properties']['type'])] += 1
            sirene_geo.writerow(et+[source['geometry']['coordinates'][0],
                                    source['geometry']['coordinates'][1],
                                    round(source['properties']['score'], 2),
                                    source['properties']['type'],
                                    source['properties']['label'],
                                    source['properties']['id'],
                                    source['l4'] if 'l4' in source else '',
                                    source['geo_l4'] if 'geo_l4' in source else '',
                                    source['geo_l5'] if 'geo_l5' in source else ''])
            if 'score' in source['properties']:
                score_count = score_count + 1
                score_total = score_total + source['properties']['score']
                if score_count > 100:
                    score_variance = score_variance + (source['properties']['score'] - score_total / score_count) ** 2

        if total % 1000 == 0:
            stats['geocode_cache'] = cache
            stats['count'] = total
            stats['geocode_count'] = geocode_count
            if total>0:
                stats['efficacite'] = round(100*ok/total, 2)
            if score_count > 0:
                stats['geocode_score_avg'] = score_total / score_count
            if score_count > 100:
                stats['geocode_score_variance'] = score_variance / (score_count-101)
            print(json.dumps(stats, sort_keys=True))
            if conn:
                conn.commit()

stats['geocode_cache'] = cache
stats['count'] = total
stats['geocode_count'] = geocode_count
stats['action'] = 'final'
if total>0:
    stats['efficacite'] = round(100*ok/total, 2)
if score_count > 0:
    stats['geocode_score_avg'] = score_total / score_count
if score_count > 100:
    stats['geocode_score_variance'] = score_variance / (score_count-101)
print(json.dumps(stats, sort_keys=True))
if conn:
    conn.commit()
