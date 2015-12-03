#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import shutil
import os

ROOTURL = "http://programme-candidats.interieur.gouv.fr/data-jsons/"

def downloadPDF(name, url):
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')
    with open(os.path.join('pdfs', name), 'wb') as f:
        r = requests.get(url, stream=True)
        r.raw.decode_content = True
        shutil.copyfileobj(r.raw, f)

regions = requests.get(ROOTURL + 'elections-1-regions.json').json()
for region in regions['regions']:
    listes = requests.get(ROOTURL + 'elections-1-regions-%s-candidacies.json' % region['id']).json()
    for liste in listes['lists']:
        codeId = "ER2015_%s_%s_tour1_" % (region["name"].replace(' ', ''), liste["name"].replace(' ', '')[:10])
        if not liste["isBulletinDummy"]:
            downloadPDF(codeId + "bulletinvote.pdf", "http://programme-candidats.interieur.gouv.fr" + liste["bulletinDeVote"])
        if not liste["isPropagandeDummy"]:
            downloadPDF(codeId + "professionfoi.pdf", "http://programme-candidats.interieur.gouv.fr" + liste["propagande"])

