#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys, re, json, requests
import lxml.html as html
from time import sleep
from datetime import datetime, timedelta
from pymongo import MongoClient


with open("config.json") as f:
    conf = json.load(f)

db = MongoClient()["m6forums"]

def clean(t):
    return t[0].text_content().encode("utf-8").strip("\n\t \r")

months = {
  'janv.': 1, 'févr.': 2, 'mars': 3, 'avril': 4, 'mai': 5, 'juin': 6,
  'juil.': 7, 'août': 8, 'sept.': 9, 'oct.': 10, 'nov.': 11, 'déc.': 12
}
re_date = re.compile(r"(\d+) (\D+) (\d+)")
re_date_sup = re.compile(r"^.*Message supprimé le (\d+/\d+/\d+ à \d+):(\d+)(?:$|\D.*$)")
extract_dat = lambda x: (x.year, x.month, x.day)
def format_date(d):
    try:
        d = clean(d)
    except:
        d = re_date_sup.sub(r"\1h\2", d)
    dat, tim = d.split(" à ")
    if dat == "Aujourd'hui":
        now = datetime.today()
        yr, mt, dy = extract_dat(now)
    elif dat == "Hier":
        now = datetime.today() - timedelta(days=1)
        yr, mt, dy = extract_dat(now)
    else:
        dat = dat.replace("Le ", "")
        try:
            dy, mon, yr = re_date.match(dat).groups()
            mt = months[mon]
        except:
            dy, mt, yr = dat.split("/")
    hr, mn = tim.replace("mn", "").split("h")
    return datetime(int(yr), int(mt), int(dy), int(hr), int(mn)).isoformat()

# Collect threads list
new_threads = 0
for subforum in conf["subfora"]:
    url_0 = "http://www.m6.fr/%s/forum/%s" % (conf["forum"], subforum + "/" if subforum else "")
    cururl = url_0
    while cururl:
        print >> sys.stderr, "[INFO] Downloading %s" % cururl
        page = html.fromstring(requests.get(cururl).text)
        threads = page.find_class("sujet")
        for t in threads:
            tid = int(t.xpath("@id")[0].replace("sujet", ""))
            existing = db["threads"].find_one({"_id": tid})
            thread = {"_id": tid}
            thread["modified_at"] = format_date(t.xpath("div[@class='last_post']/div[@class='date']"))
            thread["modified_by"] = clean(t.xpath("div[@class='last_post']/div[@class='membre']/a"))
            thread["modified_by_id"] = t.xpath("div[@class='last_post']/div[@class='membre']/a/@href")[0].encode("utf-8").replace("http://www.m6.fr/forum/profil/", "").rstrip("/")
            if existing and existing["modified_at"].encode("utf-8") == thread["modified_at"] and existing["modified_by_id"].encode("utf-8") == thread["modified_by_id"]:
                continue

            new_threads += 1

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
            db["threads"].update({"_id": tid}, thread, upsert=True)

        nextpage = page.find_class("next")
        if nextpage:
            cururl = nextpage[0].xpath("@href")[0]
            sleep(1)
        else:
            cururl = None

print >> sys.stderr, "[INFO] Found %s newly created/modified threads to collect" % new_threads


# Update new threads message list
new_posts = 0
threads_todo = db["threads"].find({"to_scrap": True}, fields=["url", "title"])
for t in threads_todo:
    cururl = t["url"]
    while cururl:
        print >> sys.stderr, "[INFO] Downloading %s" % cururl
        page = html.fromstring(requests.get(cururl).text)
        posts = page.find_class("message")
        for p in posts:
            pid = int(p.xpath("@id")[0].replace("message", ""))
            existing = db["posts"].find_one({"_id": pid})
            if existing:
                continue

            new_posts += 1
            post = {"_id": pid}
            post["permalink"] = "%s#%s" % (cururl, pid)


            date = p.xpath("div/div/div[@class='message_date']")
            if not date:
                post["deleted"] = True
                author = p.xpath("div[@class='profil pseudo']/a")
                post["author_picture"] = None
                post["message"] = clean(p.xpath("div[@class='messageContainer']"))
                if post["message"]:
                    post["created_at"] = format_date(post["message"])
                else:
                    post["created_at"] = None
            else:
                post["deleted"] = False
                author = p.xpath("div/div[@class='pseudo']/a")
                post["author_picture"] = p.xpath("div/div/div/img[@class='avatar']/@src")[0]
                post["message"] = clean(p.xpath("div/div[@class='messageContent']"))
                post["created_at"] = format_date(p.xpath("div/div/div[@class='message_date']"))
                #TODO post["reply_to_msgs"] =
                #TODO post["reply_to_users"] =

            post["author"] = clean(author)
            post["author_id"] = author[0].xpath("@href")[0].encode("utf-8").replace("http://www.m6.fr/forum/profil/", "").rstrip("/")

            post["thread_id"] = t["_id"]
            post["thread_title"] = t["title"]

            db["posts"].insert(post)

        nextpage = page.find_class("next")
        if nextpage:
            cururl = nextpage[0].xpath("@href")[0]
            if not cururl.startswith("http"):
                cururl = "http://www.m6.fr/%s" % cururl.lstrip("/")
            sleep(1)
        else:
            cururl = None

    db["threads"].update({"_id": t["_id"]}, {"$set": {"to_scrap": False}})

print >> sys.stderr, "[INFO] Collected %s new messages" % new_posts


