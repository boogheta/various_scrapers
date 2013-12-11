#!/usr/bin/env python

import sys, pymongo
import simplejson as json

with open(sys.argv[1], "r") as f:
    data = json.load(f)

group = sys.argv[2] if len(sys.argv) > 2 else None

db = pymongo.Connection("localhost", 27017)["flickr"]

if "metas" in sys.argv[1]:
    metas = data['group']
    metas['_id'] = group
    db['groups'].save(metas)

elif "person" in data:
    user = data['person']
    user['_id'] = user['id']
    db['users'].save(user)

elif "photos" in data:
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

else:
    print "Couldn't identify what kind of data this file is : %s" % sys.argv[1]
