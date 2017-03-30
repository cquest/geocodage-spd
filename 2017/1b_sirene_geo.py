#! /usr/bin/python3
import sys
import csv
import requests
import json
import re
import sqlite3
import marshal

score_min = 0.30

# URL à appeler pour géocodage BAN et BANO
addok_ban = 'http://localhost:7979/search/'
addok_bano = 'http://localhost:7878/search'

geocode_count = 0

# effecture une req. sur l'API de géocodage
def geocode(api, params, l4):
    params['autocomplete']=0
    r = requests.get(api, params)
    try:
        j = json.loads(r.text)
        global geocode_count
        geocode_count += 1
        if 'features' in j and len(j['features'])>0:
            j['features'][0]['l4'] = l4
            return(j['features'][0])
        else:
            return(None)
    except:
        return(None)

def trace(txt):
    if False:
        print(txt)

sirene_csv = csv.reader(open(sys.argv[1],'r'))
sirene_geo = csv.writer(open('geo-'+sys.argv[1],'w'))

# chargement de la liste des communes et lat/lon
communes = csv.DictReader(open('communes-plus-20140630.csv','r'))
commune_insee = []
commune_latitude = []
commune_longitude = []
for commune in communes:
    commune_insee.append(commune['\ufeffinsee'])
    commune_latitude.append(round(float(commune['lon_centro']),6))
    commune_longitude.append(round(float(commune['lat_centro']),6))

# chargement de la liste des mairies et lat/lon
mairies = csv.DictReader(open('communes_mairies.csv','r'))
mairies_insee = []
mairies_latitude = []
mairies_longitude = []
for mairie in mairies:
    if mairie['lat'] != '' and mairie['lng'] !='':
        mairies_insee.append(mairie['codeinsee'])
        mairies_latitude.append(round(float(mairie['lat']),6))
        mairies_longitude.append(round(float(mairie['lng']),6))


header = None
ok = 0
total = 0
cache = 0
numbers = re.compile('(^[0-9]*)')
stats = {'action':'progress','housenumber':0,'interpolation':0,'street':0,'locality':0,'municipality':0,'vide':0,'townhall':0,'fichier':sys.argv[1]}


conn = sqlite3.connect('cache_geo/cache_addok_'+sys.argv[1]+'.db')
conn.execute('CREATE TABLE IF NOT EXISTS cache_addok (adr text, geo text)')
conn.execute('CREATE INDEX IF NOT EXISTS cache_addok_adr ON cache_addok (adr)')

for et in sirene_csv:
    if header is None:
        header = et+['longitude','latitude','geo_score','geo_type','geo_adresse','geo_id','geo_ligne']
        sirene_geo.writerow(header)
    else:
        total = total + 1

        # géocodage de l'adresse géographique
        # au cas où numvoie contiendrait autre chose que des chiffres...
        numvoie = numbers.match(et[16]).group(0)

        indrep = et[17]
        typvoie = et[18]
        libvoie = et[19]

        if numvoie == '' and numbers.match(libvoie).group(0):
            numvoie = numbers.match(libvoie).group(0)
            libvoie = libvoie[len(numvoie):]


        # typvoie incorrect
        if typvoie == 'PRO':
            typvoie = 'PROM'

        # élimination des LD / LIEU-DIT des libellés
        if typvoie == 'LD':
            typvoie = ''
        libvoie = re.sub(r'^PRO ','PROMENADE ',libvoie)
        libvoie = re.sub(r'^LD ','',libvoie)
        libvoie = re.sub(r'^LIEU(.|)DIT ','',libvoie)
        libvoie = re.sub(r'^ADRESSE INCOMPLETE.*','',libvoie)
        libvoie = re.sub(r'^SANS DOMICILE FIXE','',libvoie)

        # ou de la ligne 4 normalisée
        ligne4G = ('%s%s %s %s' % (numvoie, indrep, typvoie, libvoie)).strip()
        ligne4N = et[5].strip()
        ligne4D = et[12].strip()
        # code INSEE de la commune
        depcom = '%s%s' % (et[22],et[23])
        try:
            cursor = conn.execute('SELECT * FROM cache_addok WHERE adr=?', ('%s|%s|%s|%s' % (depcom,ligne4G,ligne4N,ligne4D), ))
            g = cursor.fetchone()
        except:
            g = None
        if g is not None:
            source = marshal.loads(g[1])
            cache = cache+1
        else:

            trace('%s / %s / %s' % (ligne4G, ligne4D, ligne4N))

            # géocodage BAN (ligne4 géo, déclarée ou normalisée si pas trouvé ou score insuffisant)
            ban = None
            if ligne4G != '':
               ban = geocode(addok_ban, {'q': ligne4G, 'citycode': depcom, 'limit': '1'},'G')
            if ban is None or ban['properties']['score']<score_min and ligne4N != ligne4G and ligne4N !='':
                ban = geocode(addok_ban, {'q': ligne4N, 'citycode': depcom, 'limit': '1'},'N')
                trace('+ ban  L4N')
            if ban is None or ban['properties']['score']<score_min and ligne4D != ligne4N and ligne4D != ligne4G and ligne4D !='':
                ban = geocode(addok_ban, {'q': ligne4D, 'citycode': depcom, 'limit': '1'},'D')
                trace('+ ban  L4D')


            # géocodage BANO (ligne4 géo, déclarée ou normalisée si pas trouvé ou score insuffisant)
            bano = None
            if ligne4G != '':
                bano = geocode(addok_bano, {'q': ligne4G, 'citycode': depcom, 'limit': '1'},'G')
            if bano is None or bano['properties']['score']<score_min and ligne4N != ligne4G and ligne4N !='':
                bano = geocode(addok_bano, {'q': ligne4N, 'citycode': depcom, 'limit': '1'},'N')
                trace('+ bano L4N')
            if bano is None or bano['properties']['score']<score_min and ligne4D != ligne4N and ligne4D != ligne4G and ligne4D !='':
                bano = geocode(addok_bano, {'q': ligne4D, 'citycode': depcom, 'limit': '1'},'D')
                trace('+ bano L4D')

            if ban is not None:
                ban_score = ban['properties']['score']
                ban_type = ban['properties']['type']
                if ['village','town','city'].count(ban_type)>0:
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
                    bano['properties']['id'] = '%s_%s' % (bano['properties']['id'],bano['properties']['housenumber'])
                bano_type = bano['properties']['type']
                if ['village','town','city'].count(bano_type)>0:
                    bano_type = 'municipality'
            else:
                bano_score = 0
                bano_type = ''

            # choix de la source
            source = None

            # on a un numéro... on cherche dessus
            if numvoie != '' :
                # numéro trouvé dans les deux bases, on prend BAN sauf si score inférieur de 20% à BANO
                if ban_type == 'housenumber' and bano_type == 'housenumber' and ban_score > score_min and ban_score >= bano_score/1.2:
                    source = ban
                elif ban_type == 'housenumber' and ban_score > score_min:
                    source = ban
                elif bano_type == 'housenumber' and bano_score > score_min:
                    source = bano
                # on cherche une interpollation dans BAN
                elif ban is None or ban_type == 'street' and int(numvoie)>2:
                    ban_avant = geocode(addok_ban, {'q': '%s %s %s' % (int(numvoie)-2, typvoie, libvoie), 'citycode': depcom, 'limit': '1'},'G')
                    ban_apres = geocode(addok_ban, {'q': '%s %s %s' % (int(numvoie)+2, typvoie, libvoie), 'citycode': depcom, 'limit': '1'},'G')
                    if ban_avant is not None and ban_apres is not None:
                        if ban_avant['properties']['type'] == 'housenumber' and ban_apres['properties']['type'] == 'housenumber' and ban_avant['properties']['score']>0.5 and ban_apres['properties']['score']>score_min :
                            source = ban_avant
                            source['geometry']['coordinates'][0] = round((ban_avant['geometry']['coordinates'][0]+ban_apres['geometry']['coordinates'][0])/2,6)
                            source['geometry']['coordinates'][1] = round((ban_avant['geometry']['coordinates'][1]+ban_apres['geometry']['coordinates'][1])/2,6)
                            source['properties']['score'] = (ban_avant['properties']['score']+ban_apres['properties']['score'])/2
                            source['properties']['type'] = 'interpolation'
                            source['properties']['id'] = ''
                            source['properties']['label'] = numvoie + ban_avant['properties']['label'][len(ban_avant['properties']['housenumber']):]

            # on essaye sans l'indice de répétition (BIS, TER qui ne correspond pas ou qui manque en base)
            if source is None and ban is None and indrep != '':
                trace('supp. indrep BAN : %s %s %s' % (numvoie, typvoie, libvoie))
                addok = geocode(addok_ban, {'q': '%s %s %s' % (numvoie, typvoie, libvoie), 'citycode': depcom, 'limit': '1'},'G')
                if addok is not None and addok['properties']['type'] == 'housenumber' and addok['properties']['score'] > score_min:
                    addok['properties']['type'] = 'interpolation'
                    source = addok
                    trace('+ ban  L4G-indrep')
            if source is None and bano is None and indrep != '':
                trace('supp. indrep BANO: %s %s %s' % (numvoie, typvoie, libvoie))
                addok = geocode(addok_bano, {'q': '%s %s %s' % (numvoie, typvoie, libvoie), 'citycode': depcom, 'limit': '1'},'G')
                if addok is not None and addok['properties']['type'] == 'housenumber' and addok['properties']['score'] > score_min:
                    addok['properties']['type'] = 'interpolation'
                    source = addok
                    trace('+ bano L4G-indrep')

            # pas trouvé ? on cherche une rue
            if source is None and typvoie != '':
                if ban_type == 'street' and bano_type == 'street' and ban_score > score_min and ban_score >= bano_score/1.2:
                    source = ban
                elif ban_type == 'street' and ban_score > score_min:
                    source = ban
                elif bano_type == 'street' and bano_score > score_min:
                    source = bano

            # pas trouvé ? on cherche sans numvoie
            if source is None and numvoie != '':
                trace('supp. numvoie : %s %s %s' % (numvoie, typvoie, libvoie))
                addok = geocode(addok_ban, {'q': '%s %s' % (typvoie, libvoie), 'citycode': depcom, 'limit': '1'},'G')
                if addok is not None and addok['properties']['type'] == 'street' and addok['properties']['score'] > score_min:
                    source = addok
                    trace('+ ban  L4G-numvoie')
            if source is None and numvoie != '':
                addok = geocode(addok_bano, {'q': '%s %s' % (typvoie, libvoie), 'citycode': depcom, 'limit': '1'},'G')
                if addok is not None and addok['properties']['type'] == 'street' and addok['properties']['score'] > score_min:
                    source = addok
                    trace('+ bano L4G-numvoie')


            # pas trouvé ? tout type accepté...
            if source is None:
                if ban_score > score_min and ban_score >= bano_score*0.8:
                    source = ban
                elif ban_score > score_min:
                    source = ban
                elif bano_score > score_min:
                    source = bano

            # on conserve le résultat dans le cache sqlite
            cursor = conn.execute('INSERT INTO cache_addok VALUES (?,?)', ('%s|%s|%s|%s' % (depcom,ligne4G,ligne4N,ligne4D), marshal.dumps(source)))

        if source is None:
            # attention latitude et longitude sont inversées dans le fichier CSV et donc la base sqlite
            row = et+['','',0,'','','','']
            try:
                i = commune_insee.index(depcom)
                row = et+[commune_longitude[i],commune_latitude[i],0,'municipality','',commune_insee[i],'']
                if ligne4G.strip() !='':
                    if typvoie == '' and ['CHEF LIEU','CHEF-LIEU','BOURG','LE BOURG','AU BOURG'].count(libvoie)>0:
                        stats['locality']+=1
                        ok = ok +1
                    else:
                        stats['municipality']+=1
                        print(json.dumps({'action':'manque','siren': et[0], 'nic': et[1], 'adr_insee': depcom, 'adr_texte': ligne4G.strip()},sort_keys=True))
                else:
                    stats['vide']+=1
                    ok = ok +1
            except:
                pass
            sirene_geo.writerow(row)
        else:
            ok = ok +1
            if ['village','town','city'].count(source['properties']['type'])>0:
                source['properties']['type'] = 'municipality'
            stats[source['properties']['type']]+=1
            sirene_geo.writerow(et+[source['geometry']['coordinates'][0],
                                    source['geometry']['coordinates'][1],
                                    round(source['properties']['score'],2),
                                    source['properties']['type'],
                                    source['properties']['label'],
                                    source['properties']['id'],
                                    source['l4']])
        if total % 1000 == 0:
            stats['geocode_cache'] = cache
            stats['count'] = total
            stats['geocode_count'] = geocode_count
            stats['efficacite'] = round(100*ok/total,2)
            print(json.dumps(stats,sort_keys=True))
            conn.commit()

stats['geocode_cache'] = cache
stats['count'] = total
stats['geocode_count'] = geocode_count
stats['action'] = 'final'
stats['efficacite'] = round(100*ok/total,2)
print(json.dumps(stats,sort_keys=True))
conn.commit()
