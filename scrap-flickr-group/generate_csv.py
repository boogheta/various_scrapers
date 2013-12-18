#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, pymongo

db = pymongo.Connection("localhost", 27017)["flickr"]

licenses = {
  "0": "All Rights Reserved",
  "1": "Attribution-NonCommercial-ShareAlike License",
  "2": "Attribution-NonCommercial License",
  "3": "Attribution-NonCommercial-NoDerivs License",
  "4": "Attribution License",
  "5": "Attribution-ShareAlike License",
  "6": "Attribution-NoDerivs License",
  "7": "No known copyright restrictions",
  "8": "United States Government Work"}

ct = 0
ph = {}
headers = ["id","url","title","date","url_original_img","url_squared_img","url_thumbnail_img","width","height","user","user_id","latitude","longitude","tags","description","views","groups","license","nb_object_tags"]
photos = []
photos_tags = []
full = []
for photo in db['photos'].find():
    ph['id'] = photo['_id']
    ph['url'] = "https://secure.flickr.com/%s/" % photo['_id']
    ph['title'] = photo['title']
    ph['date'] = photo['datetaken'][:10]
    try:
        ph['url_original_img'] = photo['url_o']
    except:
        ph['url_original_img'] = ""
    ph['url_squared_img'] = photo['url_s']
    ph['url_thumbnail_img'] = photo['url_t']
    try:
        ph['width'] = int(photo['o_width'])
    except:
        ph['width'] = int(photo['width_o'])
    try:
        ph['height'] = int(photo['o_height'])
    except:
        ph['height'] = int(photo['height_o'])
    try:
        ph['user'] = photo['ownername']
    except:
        ph['user'] = photo['pathalias']
    ph['user_id'] = photo['owner']
    ph['latitude'] = photo['latitude']
    ph['longitude'] = photo['longitude']
    ph['tags'] = photo['tags']
    ph['description'] = photo['description']['_content'].replace('\n', '')
    ph['views'] = photo['views']
    ph['groups'] = " ".join(photo['groups'])
    ph['license'] = licenses[photo['license']]
    if "object_tags" in photo:
        ph['nb_object_tags'] = len(photo['object_tags'])
    else:
        ph['nb_object_tags'] = 0

    line = u""
    for i in headers:
        if line:
            line += ','
        line += str(ph[i]) if isinstance(ph[i], int) or isinstance(ph[i], float) else "\"%s\"" % ph[i].replace('"', '""')
    photos.append(line)

    if "object_tags" in photo:
        for tag in photo['object_tags']:
            photos_tags.append('"%s","%s",%f,%f' % (tag['tag'].replace('\n', '').replace('"', '""'), ph['url'], tag['hpos'], tag['vpos']))
            full.append(line + ',"%s",%f,%f' % (tag['tag'].replace('\n', '').replace('"', ""), tag['hpos'], tag['vpos']))
            if tag['hpos'] > 100 or tag['vpos'] > 100:
                print "WARN", tag, ph['url']

with open("metas_photos.csv", "w") as ph_file:
    ph_file.write(",".join(['"%s"' % h for h in headers]) + "\n")
    for line in photos:
        ph_file.write(line.encode('utf-8') + "\n")

with open("tags_photos.csv", "w") as ph_file:
    ph_file.write('"tag","url","horiz_center_pos","vert_center_pos"\n')
    for line in photos_tags:
        ph_file.write(line.encode('utf-8') + "\n")

with open("photos_full.csv", "w") as ph_file:
    ph_file.write(",".join(['"%s"' % h for h in headers]) + '"tag","horiz_center_pos","vert_center_pos"\n')
    for line in full:
        ph_file.write(line.encode('utf-8') + "\n")

headers = ['id', 'alias', 'username', 'name', 'url', 'location', 'description', 'nb_photos', 'firstdate']
u = {}
users = []
for user in db['users'].find():
    u['id'] = user['_id']
    u['alias'] = user['path_alias']
    u['username'] = user['username']['_content']
    try:
        u['name'] = user['realname']['_content']
    except:
        u['name'] = u['username']
    u['url'] = user['profileurl']['_content']
    try:
        u['location'] = user['location']['_content']
    except:
        u['location'] = ''
    try:
        u['description'] = user['description']['_content'].replace('\n', ' ')
    except:
        u['description'] = ''
    u['nb_photos'] = user['photos']['count']['_content']
    try:
        u['firstdate'] = user['photos']['firstdatetaken']['_content'][:10]
    except:
        u['firstdate'] = ""
    line = u""
    for i in headers:
        if line:
            line += ','
        if not u[i]:
            u[i] = ''
        line += str(u[i]) if isinstance(u[i], int) or isinstance(u[i], float) else "\"%s\"" % u[i].replace('"', '""')
    users.append(line)

with open("metas_users.csv", "w") as ph_file:
    ph_file.write(",".join(['"%s"' % h for h in headers]) + "\n")
    for line in users:
        ph_file.write(line.encode('utf-8') + "\n")

headers = ['id', 'name', 'url', 'description', 'nb_users', 'nb_photos']
g = {}
groups = []
for group in db['users'].find():
    g['id'] = group['id']
    try:
        g['name'] = group['name']['_content']
    except:
        g['name'] = ''
    g['url'] = "https://secure.flickr.com/groups/%s/pool/" % group['id']
    try:
        g['description'] = group['description']['_content'].replace('\n', ' ')
    except:
        g['description'] = ''
    try:
        g['nb_users'] = group['members']['_content']
    except:
        g['nb_users'] = 0
    try:
        g['nb_photos'] = group['pool_count']['_content']
    except:
        g['nb_photos'] = 0
    line = u""
    for i in headers:
        if line:
            line += ','
        if not g[i]:
            g[i] = ''
        line += str(g[i]) if isinstance(g[i], int) or isinstance(g[i], float) else "\"%s\"" % g[i].replace('"', '""')
    groups.append(line)

with open("metas_groups.csv", "w") as ph_file:
    ph_file.write(",".join(['"%s"' % h for h in headers]) + "\n")
    for line in users:
        ph_file.write(line.encode('utf-8') + "\n")



