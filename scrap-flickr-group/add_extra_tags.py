#!/usr/bin/env python

import sys, pymongo

_id = sys.argv[1]

with open(sys.argv[2], "r") as f:
    tags = f.read()

db = pymongo.Connection("localhost", 27017)["flickr"]
photo = db['photos'].find_one({'_id': _id})

for line in tags.split('\n'):
    if not "object_tags" in photo:
        photo["object_tags"] = []
    if line and line not in photo["object_tags"]:
        photo["object_tags"].append(line)

db['photos'].update({'_id': _id}, photo)

