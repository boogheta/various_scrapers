#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, sys, re
from datetime import datetime
from pymongo import MongoClient

db = MongoClient()["m6forums"]['posts']

re_cp1212 = re.compile(ur'[\x80-\x9F]')
def recode(x):
    if type(x) == unicode and re_cp1212.search(x):
        x = x.encode('latin1').decode('CP1252', 'ignore')
    return x.encode('utf8')

re_newline = re.compile(r"[\r\n]+")
uniline = lambda x: re_newline.sub(" ", x)
escaper = lambda x: '"%s"' % x.replace('"', '""')
formatt = lambda x: escaper(uniline(recode(x)))

db.ensure_index([("thread_title", 1), ("created_at", 1)])

print "permalink,thread,author,text,timestamp,deleted"
for t in db.find(sort=[("thread_title", 1), ("created_at", 1)]):
    print ",".join([formatt(a) if a else "" for a in [t["permalink"],t["thread_title"],t["author"],t["message"],t["created_at"],str(t["deleted"])]])

