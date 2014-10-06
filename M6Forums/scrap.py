#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, json, requests
import lxml.html as html
from time import sleep
from datetime import datetime, timedelta
from pymongo import MongoClient


with open("config.json") as f:
    conf = json.load(f)

db = MongoClient()["m6forums"][conf["forum"]]

def clean(t):
    return t[0].text_content().encode("utf-8").strip("\n\t \r")

months = {
  'janv.': 1,
  'févr.': 2,
  'mars': 3,
  'avril': 4,
  'mai': 5,
  'juin': 6,
  'juil.': 7,
  'août': 8,
  'sept.': 9,
  'oct.': 10,
  'nov.': 11,
  'déc.': 12
}
re_date = re.compile(r"(\d+) (\D+) (\d+)")
extract_dat = lambda x: (x.year, x.month, x.day)
def format_date(d):
    dat, tim = clean(d).split(" à ")
    if dat == "Aujourd'hui":
        now = datetime.today()
        yr, mt, dy = extract_dat(now)
    elif dat == "Hier":
        now = datetime.today() - timedelta(days=1)
        yr, mt, dy = extract_dat(now)
    else:
        dat = dat.replace("Le ", "")
        dy, mon, yr = re_date.match(dat).groups()
        mt = months[mon]
    hr, mn = tim.replace("mn", "").split("h")
    return datetime(int(yr), mt, int(dy), int(hr), int(mn)).isoformat()

# Collect threads list
for subforum in conf["subfora"]:
    url_0 = "http://www.m6.fr/%s/forum/%s" % (conf["forum"], subforum + "/" if subforum else "")
    cururl = url_0
    while cururl:
        page = html.fromstring(requests.get(cururl).text)
        print >> sys.stderr, "[INFO] Downloading %s" % cururl
        threads = page.find_class("sujet")
        for t in threads:
            tid = int(t.xpath("@id")[0].replace("sujet", ""))
            existing = db.find_one({"_id": tid})
            thread = {"_id": tid}
            thread["modified_at"] = format_date(t.xpath("div[@class='last_post']/div[@class='date']"))
            thread["modified_by"] = clean(t.xpath("div[@class='last_post']/div[@class='membre']/a"))
            thread["modified_by_id"] = t.xpath("div[@class='last_post']/div[@class='membre']/a/@href")[0].encode("utf-8").replace("http://www.m6.fr/forum/profil/", "").rstrip("/")
            if existing and existing["modified_at"].encode("utf-8") == thread["modified_at"] and existing["modified_by_id"].encode("utf-8") == thread["modified_by_id"]:
                continue

            thread["forum"] = conf["forum"]
            thread["subforum"] = subforum

            title = t.xpath("div[@class='titre']/div/a[@class='title']")
            thread["url"] = title[0].xpath("@href")[0]
            if not thread["url"].startswith("http"):
                thread["url"] = "http://www.m6.fr/%s" % thread["url"].lstrip("/")
            thread["title"] = clean(title)

            thread["nb_messages"] = int(clean(t.xpath("div[@class='rep']")))

            thread["created_at"] = format_date(t.xpath("div[@class='auteur']/div[@class='date']"))
            thread["created_by"] = clean(t.xpath("div[@class='auteur']/div[@class='membre']/a"))
            thread["created_by_id"] = t.xpath("div[@class='auteur']/div[@class='membre']/a/@href")[0].encode("utf-8").replace("http://www.m6.fr/forum/profil/", "").rstrip("/")

            thread["pinned"] = "stick" in t.get("class")
            thread["to_scrap"] = True
            db.update({"_id": tid}, thread, upsert=True)

        nextpage = page.find_class("next")
        if nextpage:
            cururl = nextpage[0].xpath("@href")[0]
            sleep(1)
        else:
            cururl = None



