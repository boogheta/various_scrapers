#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, csv, sys
import requests
import shutil

def downloadPDF(filepath, filename, url):
    filepath = os.path.join(filepath, filename)
    if os.path.exists(filepath):
        print >> sys.stderr, "WARNING: already existing PDF", filepath
        return
    with open(filepath, 'wb') as f:
        r = requests.get(url, stream=True)
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

if __name__ == '__main__':
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')
    HOSTURL = 'http://programme-candidats.interieur.gouv.fr'
    DATAURL = HOSTURL + '/data-jsons/'
    with open('listes.csv') as f:
        listeIds = dict((row['nom'].strip().decode('utf-8'), row['couleur politique'].strip()) for row in list(csv.DictReader(f)))
    with open('regions.csv') as f:
        regionIds = dict((row['region'].strip().decode('utf-8'), row['sigle'].strip()) for row in list(csv.DictReader(f)))
    for tour in [1, 2]:
        regions = requests.get(DATAURL + 'elections-%s-regions.json' % tour).json()
        for region in regions['regions']:
            listes = requests.get(DATAURL + 'elections-%s-regions-%s-candidacies.json' % (tour, region['id'])).json()
            for liste in listes['lists']:
                regionId = regionIds[region['name']] if region['name'] in regionIds else region['name'].replace(' ', '_')
                listeId = listeIds[liste['name']] if liste['name'] in listeIds else liste['name'].replace(' ', '_')[:10]
                name = liste["principal"].split(',')[0].replace(' ', '_')
                codeId = 'ER2015-%s-%s-%s-tour%s-' % (regionId, listeId, name, tour)
                if not liste['isBulletinDummy']:
                    downloadPDF('pdfs', codeId + 'bulletin_vote.pdf', HOSTURL + liste['bulletinDeVote'])
                else:
                    print >> sys.stderr, "WARNING: bulletin de vote missing for", codeId
                if not liste['isPropagandeDummy']:
                    downloadPDF('pdfs', codeId + 'profession_foi.pdf', HOSTURL + liste['propagande'])
                else:
                    print >> sys.stderr, "WARNING: profession de foi missing for", codeId

