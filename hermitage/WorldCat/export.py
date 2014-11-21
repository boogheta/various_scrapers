#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re, sys
from pymongo import MongoClient

db = MongoClient()["books-ermitage"]["worldcat"]

fields = {}
langs = {}
keywords = {}
lines = {}

selection = {}
if len(sys.argv) > 1:
    ids = []
    with open(sys.argv[1]) as f:
        ids = [l for l in f.read().split("\n") if l]
    selection = {"_id": {"$in": ids}}

def add_value(dico, val, year=None):
    if val not in dico:
        dico[val] = (0 if year is None else {})
    if year is None:
        dico[val] += 1
    elif year:
        add_value(dico[val], year)

def format_field(values):
    if type(values) == list:
        return "|".join([v.replace("|", "/") for v in values])
    return values.replace("|", "/")

def find_lang(l):
    if type(l) == list:
        for v in l:
            if len(v) == 3:
                return v.lower()
        return format_field(l)
    return l.lower()

def find_year(t):
    date = format_field(t)
    match = re_year.search(date)
    if match:
        return match.group(2)
    return ""

re_year = re.compile(r"(^|\D)(\d{4})(\D|$)")

minyear = 2100
lines = []
for r in db.find(selection):
    book = {
      "id": r["_id"],
      "creator": format_field(r.get("creator", "")),
      "date": format_field(r.get('date', "")),
      "format": format_field(r.get("format", "")),
      "year": find_year(r.get("date", "")),
      "language": find_lang(r["language"]),
      "publisher": format_field(r.get("publisher", r.get("publisher/", ""))),
      "title": format_field(r["title"]),
      "type": format_field(r.get("type", ""))
    }
    if book["year"]:
        minyear = min(minyear, int(book['year']))
    if selection:
        book["keywords"] = format_field(r.get("subject", ""))
    lines.append(book)
    for k in r:
        add_value(fields, k)

lines_head = ["id","title","creator","publisher","date","year","language","type","format"]
if selection:
    lines_head.append("keywords")

with open("%sbooks-metas.csv" % ("good-" if selection else ""), "w") as books:
    print >> books, ",".join(lines_head)
    for p in lines:
        print >> books, ",".join(['"%s"' % a.encode("utf-8").replace('"', '""') if type(a) is unicode else str(a) for a in [p[h] for h in lines_head]])
        if selection:
            add_value(langs, p["language"], p["year"])
            for k in p["keywords"].split("|"):
                add_value(keywords, k.lower().strip(), p["year"])
if selection:
    allyears = []
    while minyear < 2016:
        allyears.append(minyear)
        minyear += 1

    with open("good-books-langs-years.csv", "w") as f:
        print >> f, "lang,%s,total" % ",".join([str(a) for a in allyears])
        for l in langs:
            line = [l]
            for y in allyears:
                line.append(str(langs[l].get(str(y), 0)))
            line.append(str(sum([langs[l][y] for y in langs[l]])))
            print >> f, ",".join(line)
    with open("good-books-keywords-years.csv", "w") as f:
        print >> f, "keyword,%s,total" % ",".join([str(a) for a in allyears])
        for k in keywords:
            line = ['"%s"' % k.replace('"', '""').encode("utf-8")]
            for y in allyears:
                line.append(str(keywords[k].get(str(y), 0)))
            line.append(str(sum([keywords[k][x] for x in keywords[k]])))
            print >> f, ",".join(line)

from pprint import pprint
pprint(fields)

