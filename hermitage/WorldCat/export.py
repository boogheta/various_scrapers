#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re
from pymongo import MongoClient

db = MongoClient()["books-ermitage"]["worldcat"]

fields = {}
langs = {}
types = {}
lines = {}

def add_value(dico, val):
    if val not in dico:
        dico[val] = 0
    dico[val] += 1

def format_field(values):
    if type(values) == list:
        return "|".join(values)
    return values

def find_lang(l):
    if type(l) == list:
        for v in l:
            if len(v) == 3:
                return v
        return format_field(l)
    return l

def find_year(t):
    date = format_field(t)
    match = re_year.search(date)
    if match:
        return match.group(2)
    return ""

re_year = re.compile(r"(^|\D)(\d{4})(\D|$)")

lines = []
for r in db.find():
    lines.append({
      "id": r["_id"],
      "creator": format_field(r.get("creator", "")),
      "date": format_field(r.get('date', "")),
      "format": format_field(r.get("format", "")),
      "year": find_year(r.get("date", "")),
      "language": find_lang(r["language"]),
      "publisher": format_field(r.get("publisher", r.get("publisher/", ""))),
      "title": format_field(r["title"]),
      "type": format_field(r.get("type", ""))
    })
    for k in r:
        add_value(fields, k)
        if k == "language":
            if type(r[k]) == list:
                for v in r[k]:
                    add_value(langs, v)
            else:
                add_value(langs, r[k])
        elif k == "type":
            if type(r[k]) == list:
                for v in r[k]:
                    add_value(types, v)
            else:
                add_value(types, r[k])

lines_head = ["id","title","creator","publisher","date","year","language","type","format"]
with open("books-metas.csv", "w") as books:
    print >> books, ",".join(lines_head)
    for p in lines:
        print >> books, ",".join(['"%s"' % a.encode("utf-8").replace('"', '""') if type(a) is unicode else str(a) for a in [p[h] for h in lines_head]])


from pprint import pprint
pprint(fields)

print "\n-----\nLANGS:\n"

pprint(langs)

print "\n-----\nTYPES:\n"
pprint(types)
