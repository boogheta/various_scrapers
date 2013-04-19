#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs
import simplejson as json

organisations = {}
placemarks = {}
authors =  {}
tags = {}
orgas_places = {}
orgas_tags = {}
places_authors = {}
places_tags = {}

def store_orga_place(org, pm):
    orgpmid = "%s-%s" % (org['id'], pm['id'])
    if orgpmid not in orgas_places:
        orgas_places[orgpmid] = {'id': orgpmid, 'organisation_id': int(org['id']), 'placemark_id': int(pm['id'])}

def store_tag(tag):
    tagid = int(tag['id'])
    try:
        tags[tagid]['tag'] = tag['tag']
    except:
        tags[tagid] = {'id': tagid, 'tag': ''}
    if 'tag' in tag:
        tags[tagid]['tag'] = tag['tag']

def store_author(aut):
    autid = int(aut['id'])
    if autid not in authors:
        authors[autid] = {'id': autid, 'name': '', 'organisation_id': ''}
    if 'name' in aut:
        authors[autid]['name'] = aut['name']
    if 'organisation' in aut and aut['organisation'] is not None:
        store_orga(aut['organisation'])
        authors[autid]['organisation_id'] = int(aut['organisation']['id'])

def store_orga(org):
    orgid = int(org['id'])
    if orgid not in organisations:
        organisations[orgid] = {'id': orgid, 'url': '', 'name': ''}
    for field in ['url', 'name']:
        if field in org:
            organisations[orgid][field] = org[field]
    if 'placemarks' in org:
        for pm in org['placemarks']:
            store_place(pm)
            store_orga_place(org, pm)
    if 'tags' in org:
        for tag in org['tags']:
            store_tag(tag)
            orgtagid = "%s-%s" % (orgid, tag['id'])
            if orgtagid not in orgas_tags:
                orgas_tags[orgtagid] = {'id': orgtagid, 'organisation_id': orgid, 'tag_id': int(tag['id'])}
    if 'authors' in org:
        for aut in org['authors']:
            store_author(aut)

def store_place(pm):
    pmid = int(pm['id'])
    if pmid not in placemarks:
        placemarks[pmid] = {'id': pmid, 'url': '', 'name': '', 'latitude': 0, 'longitude': 0}
    for field in ['url', 'name', 'latitude', 'longitude']:
        if field in pm:
            placemarks[pmid][field] = pm[field]
    if 'organisations' in pm:
        for org in pm['organisations']:
            store_orga(org)
            store_orga_place(org, pm)
    if 'tags' in pm:
        for tag in pm['tags']:
            store_tag(tag)
            pmtagid = "%s-%s" % (pmid, tag['id'])
            if pmtagid not in places_tags:
                places_tags[pmtagid] = {'id': pmtagid, 'placemark_id': pmid, 'tag_id': int(tag['id'])}
    if 'authors' in pm:
        for aut in pm['authors']:
            store_author(aut)
            pmautid = "%s-%s" % (pmid, aut['id'])
            if pmautid not in places_authors:
                places_authors[pmautid] = {'id': pmautid, 'placemark_id': pmid, 'author_id': int(aut['id'])}

with open('organisations.json', 'r') as orgas_file:
    try:
        text = orgas_file.read()
        orgas_json = json.loads(text)
    except Exception as e:
        orgas_json = []
        print "Problem reading organisations.json :"
        print e
with codecs.open('placemarks.json', 'r') as places_file:
    try:
        places_json = json.load(places_file)
    except Exception as e:
        places_json = []
        print "Problem reading placemarks.json :"
        print e

for org in orgas_json:
    store_orga(org)
for pm in places_json:
    store_place(pm)

if __name__ == "__main__":
    print "DROP TABLE organisation_placemark; DROP TABLE organisation_tag; DROP TABLE placemark_author; DROP TABLE placemark_tag; DROP TABLE author; DROP TABLE organisation; DROP TABLE placemark; DROP TABLE tag;"
    print "CREATE TABLE organisation (id BIGINT, name VARCHAR(256), url VARCHAR(256), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
    print "CREATE TABLE placemark (id BIGINT, name VARCHAR(256), url VARCHAR(256), latitude FLOAT, longitude FLOAT, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
    print "CREATE TABLE author (id BIGINT, name VARCHAR(256), organisation_id BIGINT default NULL, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
    print "ALTER TABLE author ADD CONSTRAINT aut_org_id FOREIGN KEY (organisation_id) REFERENCES organisation(id);"
    print "CREATE TABLE tag (id BIGINT AUTO_INCREMENT, tag VARCHAR(256), PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci;"
    print "CREATE TABLE organisation_placemark (id VARCHAR(16), organisation_id BIGINT, placemark_id BIGINT, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ENGINE = MyISAM;"
    print "ALTER TABLE organisation_placemark ADD CONSTRAINT orgpm_organisation_id FOREIGN KEY (organisation_id) REFERENCES organisation(id);"
    print "ALTER TABLE organisation_placemark ADD CONSTRAINT orgpm_placemark_id FOREIGN KEY (placemark_id) REFERENCES placemark(id);"
    print "CREATE TABLE organisation_tag (id VARCHAR(16), organisation_id BIGINT, tag_id BIGINT, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ENGINE = MyISAM;"
    print "ALTER TABLE organisation_tag ADD CONSTRAINT orgtg_organisation_id FOREIGN KEY (organisation_id) REFERENCES organisation(id);"
    print "ALTER TABLE organisation_tag ADD CONSTRAINT orgtg_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id);"
    print "CREATE TABLE placemark_author (id VARCHAR(16), placemark_id BIGINT, author_id BIGINT, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ENGINE = MyISAM;"
    print "ALTER TABLE placemark_author ADD CONSTRAINT pmaut_placemark_id FOREIGN KEY (placemark_id) REFERENCES placemark(id);"
    print "ALTER TABLE placemark_author ADD CONSTRAINT pmaut_author_id FOREIGN KEY (author_id) REFERENCES author(id);"
    print "CREATE TABLE placemark_tag (id VARCHAR(16), placemark_id BIGINT, tag_id BIGINT, PRIMARY KEY(id)) DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ENGINE = MyISAM;"
    print "ALTER TABLE placemark_tag ADD CONSTRAINT pmtag_placemark_id FOREIGN KEY (placemark_id) REFERENCES placemark(id);"
    print "ALTER TABLE placemark_tag ADD CONSTRAINT pmtag_tag_id FOREIGN KEY (tag_id) REFERENCES tag(id);"
    
    def cleantxt(txt):
        txt = txt.encode('utf-8')
        txt = txt.replace("'", "\\'")
        return txt
    
    def nullify(txt):
        if (txt == ""):
            return "NULL"
        return "'%s'" % txt
    
    for _, org in tags.iteritems():
        print "INSERT INTO tag (id, tag) VALUES ('%s', '%s');" % (org['id'], cleantxt(org['tag']))
    for _, org in placemarks.iteritems():
        print "INSERT INTO placemark (id, name, url, latitude, longitude) VALUES ('%s', '%s', '%s', '%s', '%s');" % (org['id'], cleantxt(org['name']), org['url'], org['latitude'], org['longitude'])
    for _, org in organisations.iteritems():
            print "INSERT INTO organisation (id, name, url) VALUES ('%s', '%s', '%s');" % (org['id'], cleantxt(org['name']), org['url'])
    for _, org in authors.iteritems():
        print "INSERT INTO author (id, name, organisation_id) VALUES ('%s', '%s', %s);" % (org['id'], cleantxt(org['name']), nullify(org['organisation_id']))
    for _, org in orgas_places.iteritems():
        print "INSERT INTO organisation_placemark (id, organisation_id, placemark_id) VALUES ('%s', '%s', '%s');" % (org['id'], org['organisation_id'], org['placemark_id'])
    for _, org in orgas_tags.iteritems():
        print "INSERT INTO organisation_tag (id, organisation_id, tag_id) VALUES ('%s', '%s', '%s');" % (org['id'], org['organisation_id'], org['tag_id'])
    for _, org in places_authors.iteritems():
        print "INSERT INTO placemark_author (id, placemark_id, author_id) VALUES ('%s', '%s', '%s');" % (org['id'], org['placemark_id'], org['author_id'])
    for _, org in places_tags.iteritems():
        print "INSERT INTO placemark_tag (id, placemark_id, tag_id) VALUES ('%s', '%s', '%s');" % (org['id'], org['placemark_id'], org['tag_id'])
    
    
