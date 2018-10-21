import os
import time
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring

import json

from xmljson import yahoo
import requests
import sqlite3

### Links
annidurl = 'https://cdn.animenewsnetwork.com/encyclopedia/api.xml?title='
annallurl = 'https://cdn.animenewsnetwork.com/encyclopedia/reports.xml?id=155&nlist=all'

### Store jobs
# Create dir if doesnt exist
os.makedirs('data',exist_ok=True)

# DB connection
jobsdb = sqlite3.connect('data/appdata.db')
j = jobsdb.cursor()
j.execute('''CREATE TABLE IF NOT EXISTS jobs (id int, type text, source text, UNIQUE(id))''')
j.execute('''CREATE TABLE IF NOT EXISTS last (id int, source text)''')
jobsdb.commit()
print('DB creation part done')

# Getting last ID
j.execute('SELECT id FROM last WHERE source = ?', ('ANN',))
lastid = j.fetchone()
if lastid is None:
    lastid = 0
    j.execute('INSERT INTO last VALUES (?,?)', (0, 'ANN',))
    jobsdb.commit()
else:
    lastid = lastid[0]
print('Last ID check done')


# Req
r = requests.get(annallurl)
print('Req done')

# Add jobs
# TODO: Get only necessary IDs instead of all using lastid
root = ET.fromstring(r.text)
dblist = []
for item in root.findall('item'):
    iid = int(item.find('id').text)
    if iid <= lastid:
        break
    itype = item.find('type').text
    isource = 'ANN'
    dblist.append(tuple((iid, itype, isource)))
j.executemany('INSERT OR IGNORE INTO jobs VALUES (?,?,?)', dblist)
jobsdb.commit()
print('Jobs commit done')

lid = int(root[1][0].text)
lidsource = 'ANN'
lidtuple = (lid, lidsource)
j.execute("UPDATE last SET id = ? WHERE source = ?", lidtuple)
jobsdb.commit()
print('Last ID commit done - ' + str(lid))

# Jobs to storables
os.makedirs('data/ann/',exist_ok=True)
j.execute('SELECT id FROM jobs')
joblist = j.fetchall()
for animeid in joblist:
    time.sleep(1)
    r = requests.get(annidurl + str(animeid[0]))

    # if XML
    if 'xml' == 'xml':
        os.makedirs('data/ann/xml/',exist_ok=True)
        if not r.status_code == requests.codes.ok:
            while not r.status_code == requests.codes.ok:
                print('Request failed, bad status code')
                time.sleep(1)
                r = requests.get(annidurl + str(animeid[0]))
        with open('data/ann/xml/' + str(animeid[0]) + '.xml', 'w', encoding="utf-8") as file:
            file.write(r.text)
        print('Added anime as XML: ' + str(animeid[0]))




