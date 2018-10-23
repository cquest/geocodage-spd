#! /usr/bin/python3
# builtin modules
import sys
import json
import time
import gzip

# required modules
import requests

# local modules
import config

# on demande un token pour la session
token_request = requests.post('https://api.insee.fr/token',
                              data = {'grant_type':'client_credentials'},
                              headers={'Authorization': 'Basic '+config.auth})
if token_request.status_code != 200:
    print('ERR', token_request.status_code, token_request.text)
    exit()

t = token_request.json()
access_token = t['access_token']

# paramètres pour cette exécution
date = sys.argv[1]
url = 'https://api.insee.fr/entreprises/sirene/V3/siret'
query = 'dateDernierTraitementEtablissement:'+date
outfile = date+'-sirene.json.gz'

# création du fichier de sortie, json compressé gzip
output = gzip.open(outfile, "wt")
headers = {'Accept': 'application/json',
           'Authorization': 'Bearer '+access_token}

nombre = 10000
curseur = '*'
total = 0
maxi = 1

while total < maxi:
    params = {'q': query, 'nombre': nombre, 'curseur': curseur}
    r = requests.get(url, params=params, headers=headers)
    if r.status_code == 429:  # throttle !
        print('throttle...start')
        time.sleep(1)
        print('throttle...end')
    elif r.status_code != 200:
        print('ERROR:', r.status_code, r.text)
        time.sleep(1)
    else:
        sirets = r.json()
        if maxi == 1:
            maxi = int(r.headers['X-Total-Count'])
        if 'etablissements' in sirets:
            for siret in sirets['etablissements']:
                output.write(json.dumps(siret)+'\n')
            total = total + len(sirets['etablissements'])
            if 'curseurSuivant' in sirets['header']:
                curseur = sirets['header']['curseurSuivant']
                print(round(100*total/int(r.headers['X-Total-Count']), 2),
                      '%', r.headers['X-Total-Count'])
            else:
                break
        else:
            break

output.close()
