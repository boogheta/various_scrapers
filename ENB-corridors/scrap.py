#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, sys, json, requests
import HTMLParser
htmldecode = HTMLParser.HTMLParser().unescape

re_clean_url = re.compile(r"[^a-z0-9]", re.I)
re_dblquotes = re.compile(ur"[«»„‟“”\x93\x94]|\xe2\x80(\x9c|\x9d)")
re_quotes = re.compile(ur"[’‘`‛\x92]|ï¿½|\xe2\x80(\x99|\x98)")
re_dash = re.compile(ur"[——–\x96\x97]|â\x80\"|\xe2\x80(\x93|\x94)")
re_traildots = re.compile(ur"…|\xe2\x80\xa6")
re_et = re.compile(ur"é|\xc3\xa9")
re_aa = re.compile(ur"à|\xc3\xa0")
re_n = re.compile(ur"ń|Å\x84")
re_nn = re.compile(ur"ñ|\xc3\xb1")
re_uu = re.compile(ur"ú|\xc3\xba")
re_deg = re.compile(ur"°|\xc2\xb0")
def download(url):
    cache = re_clean_url.sub('-', url)
    try:
        with open("/tmp/%s" % cache) as f:
            summary = f.read().decode("utf-8")
    except:
        r = requests.get(url)
        if r.status_code == 404:
            if "enb125603e.html" in url:
                return download("http://www.iisd.ca/vol12/enb12603e.html")
            if "enb12300.html" in url:
                return download("http://www.iisd.ca/vol12/enb12300e.html")
            print >> sys.stderr, "WARNING 404", url
        summary = r.text
        with open("/tmp/%s" % cache, "w") as f:
            f.write(summary.encode("utf-8"))
    res = htmldecode(summary.replace("&nbsp;", " "))
    res = res.replace(u"\xc2\xa0", " ")
    res = re_quotes.sub("'", res)
    res = re_dblquotes.sub('"', res)
    res = re_dash.sub('-', res)
    res = re_et.sub(u'é', res)
    res = re_aa.sub(u'à', res)
    res = re_nn.sub(u'ñ', res)
    res = re_n.sub(u'ń', res)
    res = re_uu.sub(u'ù', res)
    res = re_deg.sub(u'°', res)
    res = re_traildots.sub('...', res)
    return res.encode("utf-8")

re_clean_line = re.compile(r"</?em>")
re_clean_links = re.compile(r"</?a [^>]*>")
re_extract_linkstart = re.compile(r'/[^/]*$')
re_extract_link = re.compile(r'^.* href="([^"]+)"')
re_section = re.compile(r'</tr><tr><th colspan="4"><h3>(?:<a href[^>]>)*([^<]*)(?:</a>)*</h3>(.*)\|(.*)\|([^<]*)<', re.I)
re_report = re.compile(r'Issue\s*#\s*(\d+)</td><td>([^<]+)<.*<a href="(/vol.*)" class="html"', re.I)
re_match_corridor = re.compile(r"<(([a-zA-Z0-9]+)[^>]*)>\s*IN\s*THE\s*(BRE+ZEWAY|COR+IDOR)S?\s*<")
re_extract_single_text = re.compile(r"^.*</h1>(.*)<script.*$", re.I)
re_clean_spaces = re.compile(r"[\s\r\n]+")
re_clean_comments = re.compile(r"<!--.*?--!?>", re.M)
re_clean_html = re.compile(r"<[^>]+>")
re_search_corridors = re.compile(r"( IN THE (?:BRE+ZEWAY|COR+IDOR)S(?:\s*[\dIV]+)? (.*?)) (?:[A-Z\s:\-]{12}|This issue of the Earth|\^ up to top)")
def get_list_metas():
    done = []
    summary = download("http://www.iisd.ca/enb/vol12/")
    for line in summary.split("\n"):
        line = re_clean_line.sub("", line)
        if "<h3>" in line:
            line = re_clean_links.sub("", line)
            try:
                metas = re_section.search(line)
                eventtitle = metas.group(1).strip()
                eventid = metas.group(2).strip()
                eventdates = metas.group(3).strip()
                eventlocation = metas.group(4).strip()
            except:
                print >> sys.stderr, "WARNING: misformatted line %s" % line
        elif "HTML" in line:
            try:
                metas = re_report.search(line)
                issue = metas.group(1).strip()
                date = metas.group(2).strip()
                url = metas.group(3).strip()
            except:
                print >> sys.stderr, "WARNING: misformatted line %s" % line
                continue
            if url.startswith("/"):
                url = "http://www.iisd.ca%s" % url
            paragraphs = extract_corridors(url)
            if paragraphs:
                done.append({
                    "event": eventtitle,
                    "eventid": eventid,
                    "dates": eventdates,
                    "location": eventlocation,
                    "issue": issue,
                    "date": date,
                    "url": url,
                    "text": paragraphs
                })
    print len(done)
    return done

def extract_corridors(url):
    content = download(url)
    typecorridor = re_match_corridor.search(content)
    text = ""
    if not typecorridor:
        return
    if typecorridor.group(2) == "a":
        url2 = re_extract_link.sub(r"\1", typecorridor.group(1))
        if url2.startswith("/"):
            url2 = "http://www.iisd.ca%s" % url2
        if not url2.startswith("http"):
            url2 = "%s/%s" % (re_extract_linkstart.sub("", url), url2)
        content = re_clean_spaces.sub(" ", download(url2))
        url = url2
        text = re_clean_html.sub("", re_extract_single_text.sub(r"\1", content)).strip()
    else:
        content = re_clean_spaces.sub(" ", content)
        content = re_clean_comments.sub("", content)
        content = re_clean_html.sub("", content)
        content = re_clean_spaces.sub(" ", content)
        corridor = re_search_corridors.search(content)
        while corridor:
            text += " %s" % corridor.group(2)
            content = content.replace(corridor.group(1), "")
            corridor = re_search_corridors.search(content)
    return text.strip()

def format_csv(val):
    val = format_comma(val)
    try:
        return val.encode("utf-8")
    except:
        return val

def format_comma(val):
    if "," in val:
        return '"%s"' % val.replace('"', '""')
    return val

if __name__ == "__main__":
    data = get_list_metas()
    with open("corridors.json", "w") as f:
        json.dump(data, f, indent=2)
    keys = data[0].keys()
    with open("corridors.csv", "w") as f:
        print >> f, ",".join(keys)
        for d in data:
            print >> f, ",".join([format_csv(d[k]) for k in keys])
