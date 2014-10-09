#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, sys
from datetime import datetime
from pymongo import MongoClient

db = MongoClient()["m6forums"]['posts']

format = lambda x: '"' + x.replace('"', '""') + '"'

db.ensure_index([("thread_title", 1), ("created_at", 1)])

print "permalink,thread,author,text,timestamp,deleted"
for t in db.find(sort=[("thread_title", 1), ("created_at", 1)]):
    text = format(t["message"])
    title = format(t["thread_title"])
    print ",".join([a.encode("utf-8") if a else "" for a in [t["permalink"],title,t["author"],text,t["created_at"],str(t["deleted"])]])

