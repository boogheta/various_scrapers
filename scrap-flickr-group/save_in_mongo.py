#!/usr/bin/env python

import sys, pymongo
import simplejson as json

with open(sys.argv[1], "r") as f:
    data = json.load(f)

group = sys.argv[2]

db = pymongo.Connection("localhost", 27017)["flickr"]

if "metas" in sys.argv[1]:
    metas = data['group']
    metas['_id'] = group
    db['groups'].save(metas)
else:
    for photo in data['photos']['photo']:
        photo['_id'] = "%s/%s" % (photo['owner'], photo['id'])
        old = db['photos'].find_one({'_id': photo['_id']})
        if old and old['groups']:
            photo['groups'] = old['groups']
        else:
            photo['groups'] = []
        if group not in photo['groups']:
            photo['groups'].append(group)
        db['photos'].update({'_id': photo['_id']}, photo, upsert=True)

