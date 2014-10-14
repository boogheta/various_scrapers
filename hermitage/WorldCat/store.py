#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, re
from pymongo import MongoClient

db = MongoClient()["books-ermitage"]["worldcat"]

re_clean_markup = re.compile(r"<[^>]+>")
def clean(x):
    return re_clean_markup.sub("", x)

re_extract_field = re.compile(r"^<[^:]*:([^> ]+)[ >]")
def extract_field_name(line):
    return re_extract_field.search(line).group(1)

def add_field(field, line, record):
    value = clean(line)
    if field not in record:
        record[field] = value
    elif type(record[field]) == list:
        if value not in record[field]:
            record[field].append(value)
    elif value != record[field]:
        record[field] = [record[field], value]

def load_and_save(page, reverse=False):
    dldir = "679c86da7dc28512d1ec192e9da42cb4" if not reverse else "25d5539ba272c838d57310651f9e20a0"
    with open(os.path.join(".cache", dldir, "%s.dublin.xml" % page)) as f:
        data = f.read()
    read = False
    for line in data.split("\n"):
        if line == "<oclcdcs>":
            read = True
            record = {}
        elif line == "</oclcdcs>":
            read = False
            db.update({"_id": record['_id']}, record, upsert=True)
        elif not read:
            continue
        if line.startswith("<oclcterms:recordIdentifier>"):
            record['_id'] = clean(line)
        elif line.startswith("<dc:") or line.startswith("<oclcterms:"):
            field = extract_field_name(line)
            add_field(field, line, record)

if __name__ == "__main__":
    i = 0
    while i < 100:
        print i
        load_and_save(i)
        load_and_save(i, reverse=True)
        i += 1
