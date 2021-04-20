#!/usr/bin/env python
# -*- coding:

import sys, re, json, html
from itertools import groupby

filepath = sys.argv[1]
pdffile = filepath.replace("pdfs/", "").replace(".xml", ".pdf")

drawMap = False
if len(sys.argv) > 2:
    drawMap = True

with open(filepath, 'r') as xml_file:
    xml = xml_file.read()

# Reorder xml lines
ordered_xml = []
page = []
is_mc2021 = int(pdffile.startswith("2021-qualifies-MC"))
def extract_position(line):
    nature = 0 if line.startswith('<page') else 1
    positions = [0, 0]
    if nature:
        positions = [int(v) for i, v in enumerate(line.split('"')[1:4]) if i != 1]
    if nature and is_mc2021 and positions[1] < 100:
        positions[0] -= 1
    return tuple([nature] + positions)

sort_and_uniq = lambda page: list(i for i, x in groupby(sorted(page, key=extract_position)))

for line in xml.split("\n"):
    if line.startswith('</page'):
        ordered_xml += sort_and_uniq(page)
        page = []
    if line.startswith('<text') or line.startswith('<page'):
        page.append(line)
ordered_xml += sort_and_uniq(page)

re_clean_blanks = re.compile(r"\s+")
re_clean_section = re.compile(r"^(\d+)\s*[:-]\s*(\S.+)")
def clean_section(s):
    s = s.replace("<b>", "")
    s = s.replace("</b>", "")
    s = s.replace("Section ", "")
    s = s.replace("SECTION ", "")
    s = re_clean_section.sub(r"\1 (\2)", s)
    return s.strip()

l1 = 200
l2 = 400

page = 0
topvals = {}
leftvals = {}
maxtop = 0
maxleft = 0
results = []
headers = ["nom", "nom d'usage", "prénom", "section", "source", "page"]
record = ["", "", "", "", "", ""]
cursection = ""
re_line = re.compile(r'<page number|text top="(\d+)" left="(-?\d+)"[^>]*font="(\d+)">(.*)</text>', re.I)
for line in ordered_xml:
    #print("DEBUG %s" % line, file=sys.stderr)
    if line.startswith('<page'):
        page += 1
        continue

    attrs = re_line.search(line)
    if not attrs or not attrs.groups():
        raise Exception("WARNING : line detected with good font but wrong format %s" % line)

    top = int(attrs.group(1))
    left = int(attrs.group(2))
    font = int(attrs.group(3))
    text = attrs.group(4).replace("&amp;", "&").strip()

    lowtext = text.lower()
    if not text or lowtext in ['section', 'nom', "nom d'usage", 'prenom',',', '\x01'] or lowtext.startswith("qualifi") or lowtext.startswith("liste") or lowtext.startswith("mise en ligne") or lowtext.startswith("page ") or lowtext.startswith("maître") or lowtext.startswith("professeur"):
        continue
    text = html.unescape(text)
    text = re_clean_blanks.sub(r" ", text)
    if text.startswith("<b"):
        if ("b>Section" in text or "b>SECTION" in text) and " Nom" not in text and text != "<b>Section</b>":
            cursection = clean_section(text)
        continue
    try:
        text = int(text)
        if (pdffile.startswith("2019") or pdffile.startswith("2020")) and top < 1200:
            cursection = text
        else:
            continue
    except:
        pass

    if top > maxtop:
        maxtop = top
    if not font in topvals:
        topvals[font] = []
    topvals[font].append(top)

    if left < 0 or top < 0:
        print('WARNING : element detected "outside" the page: %s' % line, file=sys.stderr)
        left = max(left, 0)
        top = max(top, 0)
    if left > maxleft:
        maxleft = left
    if not font in leftvals:
        leftvals[font] = []
    leftvals[font].append(left)

    if drawMap:
        continue

    #print("DEBUG %s %s %s %s" % (font, left, top, text), file=sys.stderr)
    if left < l1:
        if pdffile.startswith("2020-qualifies-MC-MNHN") or pdffile.startswith("2021"):
            record[3], record[0] = [a.strip() for a in text.split(" ", 1)]
        else:
            record[0] = text
    elif left < l2:
        record[1] = text
    else:
        record[2] = text
    if record[2]:
        record[3] = record[3] or cursection
        record[4] = pdffile
        record[5] = page
        if not record[0]:
            print("WARNING: incomplete record (%s) on page %s for the following line: %s" % (record, page, line), file=sys.stderr)
        else:
            results.append(record)
        record = ["", "", "", "", "", ""]

if not drawMap:
    print(",".join(['"%s"' % h for h in headers]))
    for i in results:
        print(",".join([str(i[a]) if isinstance(i[a], int) else "\"%s\"" % i[a].replace('"', '""') for a,_ in enumerate(i)]))

else:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib import cm

    fig = plt.figure(figsize=(8.5, 12))
    ax = fig.add_subplot(111)
    ax.grid(True, fillstyle='left')
    nf = len(leftvals)
    for font in leftvals:
        color = cm.jet(1.5*font/nf)
        ax.plot(leftvals[font], topvals[font], 'ro', color=color, marker=".")
        plt.figtext((font+1.)/(nf+1), 0.95, "font %d" % font, color=color)
    plt.xticks(np.arange(0, maxleft + 50, 50))
    plt.yticks(np.arange(0, maxtop + 50, 50))
    plt.xlim(0, maxleft + 50)
    plt.ylim(0, maxtop + 50)
    plt.gca().invert_yaxis()
    mappath = filepath.replace(".xml", ".png").replace("pdfs/", "pdfmaps/")
    fig.savefig(mappath)
    fig.clf()
    plt.close(fig)

