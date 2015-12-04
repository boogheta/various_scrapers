#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, csv
import requests
import shutil

def downloadPDF(filepath, filename, url):
    with open(os.path.join(filepath, filename), 'wb') as f:
        r = requests.get(url, stream=True)
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

if __name__ == '__main__':
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')
    HOSTURL = 'http://programme-candidats.interieur.gouv.fr'
    DATAURL = HOSTURL + '/data-jsons/'
    with open('listes.csv') as f:
        listeIds = dict((row['nom'], row['couleur politique']) for row in list(csv.DictReader(f, delimiter=';')))
    with open('regions.csv') as f:
        regionIds = dict((row['region'], row['sigle']) for row in list(csv.DictReader(f)))
    regions = requests.get(DATAURL + 'elections-1-regions.json').json()
    for region in regions['regions']:
        listes = requests.get(DATAURL + 'elections-1-regions-%s-candidacies.json' % region['id']).json()
        for liste in listes['lists']:
            regionId = regionIds[region['name']] if region['name'] in regionIds else region['name'].replace(' ', '')
            listeId = listeIds[liste['name']] if liste['name'] in listeIds else liste['name'].replace(' ', '')[:10]
            codeId = 'ER2015_%s_%s_tour1_' % (region['name'].replace(' ', ''), listeId)
            if not liste['isBulletinDummy']:
                downloadPDF('pdfs', codeId + 'bulletinvote.pdf', HOSTURL + liste['bulletinDeVote'])
            if not liste['isPropagandeDummy']:
                downloadPDF('pdfs', codeId + 'professionfoi.pdf', HOSTURL + liste['propagande'])

