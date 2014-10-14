#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys, re, json, requests
from hashlib import md5
from urllib import quote_plus as urlencode


def download(url, page):
    dldir = os.path.join(".cache", md5(url).hexdigest())
    if not os.path.isdir(dldir):
        os.makedirs(dldir)
    fil = os.path.join(dldir, "%s.dublin.xml" % page)
    if not os.path.exists(fil):
        pageUrl = "%s&startRecord=%s" % (url, 1 + 100*page)
        print pageUrl
        data = requests.get(pageUrl).content
        with open(fil, "w") as f:
            f.write(data)
    #else:
    #    with open(fil) as f:
    #        data = f.read()

def buildUrl(conf, reverse=False):
    rootUrl = "http://www.worldcat.org/webservices/catalog/search/worldcat/sru"
    keywords = '"%s"' % " ".join(conf["keywords"]).encode("utf-8")
    searchFields = ["kw", "ti", "su", "nt"]
    args = {
      "wskey": conf["api_key"],
      "maximumRecords": 100,
      #"recordSchema": "info%3Asrw%2Fschema%2F1%2Fmarcxml",
      "recordSchema": "info%3Asrw%2Fschema%2F1%2Fdc",
      "sortKeys": "Date%s" % (",,0" if reverse else ""),
      "servicelevel": "full",
      "frbrGrouping": "on",
      "query": urlencode(" or ".join(["srw.%s any %s" % (fld, keywords) for fld in searchFields]))
    }
    return "%s?%s" % (rootUrl, "&".join(["%s=%s" % (k, v) for k,v in args.items()]))


if __name__ == "__main__":
    with open("config.json") as f:
        conf = json.load(f)
    url = buildUrl(conf)
    revurl = buildUrl(conf, reverse=True)
    i = 0
    while i < 100:
        download(url, i)
        download(revurl, i)
        i += 1
