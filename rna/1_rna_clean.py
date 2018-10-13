#! /usr/bin/python3
import sys
import csv

data_csv = csv.reader(open(sys.argv[1],'r'),delimiter=';')
data_geo = csv.writer(open('out-'+sys.argv[1],'w'))
header = None

for et in data_csv:
    if header is None:
        header = et+['dep','vide']
        data_geo.writerow(header)
    else:
        try:
            for f in range(0,len(et)):
                et[f] = et[f].replace('\n',' \\n ',999).replace('\r',' \\r ',999)
            if len(et)==41:
                if et[22][:2]=='97':
                    et = et+[et[22][:3],'']
                else:
                    et = et+[et[22][:2],'']
            else:
                if et[22][:2]=='97':
                    et = et+[et[22][:3],'']
                else:
                    et = et+[et[22][:2],'']
            data_geo.writerow(et)
        except:
            print(et[0],len(et))
