#!/usr/bin/env python

import os, csv, re
import requests

urlize = lambda url: url[url.find(".do?")+4:]

def download(url, debug=False):
    page = urlize(url)
    if not os.path.isdir(".cache"):
        os.makedirs(".cache")
    fil = os.path.join(".cache", page)
    if not os.path.exists(fil):
        if debug:
            print url, "->", page
        data = requests.get(url).content
        with open(fil, "w") as f:
            f.write(data)
    else:
        with open(fil) as f:
            data = f.read()
    return data.decode("utf-8")

cleanCsv = lambda x: x.strip().decode('utf-8')

regexps = [
    (re.compile(r"([\r\n\s]|<br\/?>)+"), " "),
    (re.compile(r"\s+"), " "),
    (re.compile(r"&amp;"), "&"),
    (re.compile(r"&#039;"), "'"),
    (re.compile(r"&#034;"), '"'),
    (re.compile(r' style="[^"]+"'), ""),
    (re.compile(r' class="searchResultsTableColumnName"'), "")
]
def clean_html(html):
    for regex, repl in regexps:
        html = regex.sub(repl, html)
    return html

re_next = re.compile(r'(-p=\d+)"><img src="/transparencyinitiative/meetings/wel/img/displaytag/next.gif"')
re_elements = re.compile(r'<tr class="(?:even|odd)">(.*?)</tr>')
re_span = re.compile(r'<\/?span>')
re_date = re.compile(r'^\D*(\d+)/(\d+)/(\d+)\D*$')
re_name = re.compile(r'^.*-->\s*(.*)\s*$')
re_regid = re.compile(r'^.*displaylobbyist\.do\?id=(.*?)">.*$')
def scrapePage(url, agenda):
    html = download(url)
    nextUrl = re_next.search(html)
    nextUrl = nextUrl.group(1) if nextUrl else None

    meetings = []
    html = clean_html(html)
    elements = re_elements.findall(html)
    shiftidx = 0
    cabinet = (agenda['Fonction'].strip() == "Commissioner's Cabinet")
    if cabinet:
        shiftidx = 1
    for element in elements:
        canceled = ('<span>' in element)
        element = re_span.sub('', element)
        metas = element.split(' </td> <td> ')
        meeting = {
            'date': re_date.sub(r'\3-\2-\1', metas[0 + shiftidx]),
            'location': metas[1 + shiftidx].strip(),
            'lobby': re_name.sub(r'\1', metas[2 + shiftidx]),
            'lobby_id': re_regid.sub(r'\1', metas[2 + shiftidx]),
            'subject': metas[3 + shiftidx].replace(' </td>', '').strip(),
            'canceled': canceled,
            'source': url
        }
        if cabinet:
            meeting['official'] = metas[0].replace(' <td> ', '').strip()
        else:
            meeting['official'] = cleanCsv(agenda['Name'])
        meeting['office'] = cleanCsv(agenda['Office'])
        meeting['fonction'] = cleanCsv(agenda['Fonction'])
        meeting['direction'] = cleanCsv(agenda['Direction'])
        meetings.append(meeting)
    return meetings, nextUrl

def scrapeOne(agenda):
    url = agenda["Url"]
    allMeetings = []
    while url:
        meetings, nextPage = scrapePage(url, agenda)
        allMeetings += meetings
        url = "%s&d-6679426%s" % (agenda["Url"], nextPage) if nextPage else None
    return allMeetings

def scrapeAll(agendas):
    meetings = []
    for agenda in agendas:
        if "meeting.do" not in agenda["Url"]:
            continue
        meetings += scrapeOne(agenda)
    return meetings

format_str = lambda x: ('"%s"' % x.replace('"', '""') if ',' in x else x)
format_csv = lambda x: (format_str(x) if type(x) is unicode else str(x)).encode('utf-8')
def write_csv(data, headers, openedfile):
    print >> openedfile, headers.encode('utf-8')
    for row in data:
        print >> openedfile, ",".join([format_csv(row[h]) for h in headers.split(',')])

if __name__ == "__main__":
    # source: http://www.transparencyinternational.eu/european-commissions-lobbying-meetings/
    with open('liste_agendas_TI.csv') as f:
        data = scrapeAll(list(csv.DictReader(f)))
    headers = "official,office,fonction,direction,date,lobby,lobby_id,subject,location,canceled,source"
    with open('EU_commission_lobbying_meetings.csv', 'w') as f:
        write_csv(data, "official,office,fonction,direction,date,lobby,lobby_id,subject,location,canceled,source", f)
