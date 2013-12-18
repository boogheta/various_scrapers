#!/usr/bin/env python

import sys, pymongo

_id = sys.argv[1]

with open(sys.argv[2], "r") as f:
    tags = f.read()

db = pymongo.Connection("localhost", 27017)["flickr"]
photo = db['photos'].find_one({'_id': _id})

z_w = int(photo['width_z']) if 'width_z' in photo else 640
z_h = int(photo['height_z']) if 'height_z' in photo else float(photo['o_height']) * z_w / float(photo['o_width'])

photo["object_tags"] = []
for line in tags.split('\n'):
    if line:
        vals = line.split(',')
        tag = {"hpos": 100.*(int(vals[0])+int(vals[2])/2)/z_w, "vpos": 100.*(int(vals[1])+int(vals[3])/2)/z_h, "tag": ",".join(vals[4:])}
        photo["object_tags"].append(tag)

db['photos'].update({'_id': _id}, photo)

