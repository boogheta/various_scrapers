#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, csv, json
from datetime import date

dico = {}
with open("vocab.en-ru.csv") as f:
    for t in csv.reader(f):
        if t[0] in ["", "russian"]:
            continue
        dico[t[0]] = t[1].strip()

manual_translations = {
  "Учетно-хранительская часть": "Conservatory/Archivist",
  "Высшее образование": "College",
  "Неполное высшее образование": "Undergraduate education",
  "Основное общее образование": "Secondary school",
  "Начальное (общее) образование": "Primary school",
  "Среднее (полное) общее образование": "High school",
  "Начальное профессиональное образование": "Professional school",
  "Среднее профессиональное образование": "Professional college",
  "Наладчик VI разряда*": "Technician",
  "Монтажник VI разряда*": "Fitter",
  "Электромонтер VI разряда*": "Electrician",
  "Слесарь-сантехник VI разряда*": "Plumber",
  "Слесарь VI разряда*": "Blacksmith",
  "Столяр VI разряда*": "Joiner",
  "Столяр VI разряда": "Joiner",
  "Водиттель автомобиля": "Driver"
}
missingdico = {}
def translate(t):
    t = t.strip()
    if t in dico:
        return dico[t]
    if t in manual_translations:
        return "%s (%s)" % (manual_translations[t], t)
    if t and t not in missingdico:
        print "[WARNING] missing translation for %s" % t
        missingdico[t] = True
    return t

format_float = lambda x: float(x.replace(" ", "").replace(",", "."))

def format_date(d):
    dat = [int(a) for a in d.split(".")]
    dat.reverse()
    return date(*dat).isoformat()

re_xp = re.compile(r"лет:\s*(\d+) мес:\s*(\d+) дн:\s*(\d+)$")
def calc_xp(t):
    try:
        return format_float(t)
    except:
        mat = re_xp.search(t)
        return float(mat.group(1)) + float(mat.group(2))/12 + float(mat.group(3))/365

people = []
guy = {}
with open("DB.en.csv") as f:
    for line in csv.reader(f):
        if line[0] == "Employee":
            continue
        if line[0]:
            if guy:
                people.append(guy)
            guy = {
              "id": line[0].replace("Работник: id = ", ""),
              "birth_date": format_date(line[1]),
              "education": translate(line[3]),
              "experience": calc_xp(line[4]),
              "hiring_date": format_date(line[5]),
              "positions": []
            }
            n_pos = 0
        guy["positions"].append({
          "order": n_pos,
          "date": format_date(line[6]),
          "salary_rate": format_float(line[8]),
          "education": guy["education"],
          "position": translate(line[9]),
          "salary": format_float(line[10]),
          "department": translate(line[11]),
          "subdepartment": translate(line[12])
        })
        n_pos += 1

people.append(guy)

from pprint import pprint
with open("DB.en.json", "w") as f:
    json.dump(people, f, indent=2)

metas_head = ["id","birth_date","education","experience","hiring_date","n_positions","first_salary","current_salary","n_departments","n_subdepartments"]
positions_head = ["id","position_order","date","salary_rate","education","position","salary","department","subdepartment"]
with open("people-metas.csv", "w") as metas, open("people-positions.csv", "w") as positions:
    print >> metas, ",".join(metas_head)
    print >> positions, ",".join(positions_head)
    for p in people:
        p["n_departments"] = len(set([po["department"] for po in p["positions"]]))
        p["n_subdepartments"] = len(set(["%s-%s" % (po["department"], po["subdepartment"]) for po in p["positions"]]))
        p["n_positions"] = len(p["positions"])
        p["first_salary"] = p["positions"][0]["salary"]
        p["current_salary"] = p["positions"][-1]["salary"]
        print >> metas, ",".join(['"%s"' % a.encode("utf-8").replace('"', '""') if type(a) is unicode else str(a) for a in [p[h] for h in metas_head]])
        for po in p["positions"]:
            po["position_order"] = po["order"]
            print >> positions, p["id"]+","+",".join(['"%s"' % a.encode("utf-8").replace('"', '""') if type(a) is unicode else str(a) for a in [po[h] for h in positions_head if h != "id"]])


yearize = lambda p: int(p["date"][:4])

import string
letters = ["A%s" % b for b in string.letters[26:]] + ["B%s" % b for b in string.letters[26:]]
hashmap = {}
minyear = 2016
for p in people:
    for po in p["positions"]:
        y = yearize(po)
        minyear = min(y,minyear)
        if po["department"] not in hashmap:
            hashmap[po["department"]] = {"_id": len(hashmap)}
        if po["subdepartment"] not in hashmap[po["department"]]:
            hashmap[po["department"]][po["subdepartment"]] = {"_id": letters[len(hashmap[po["department"]])-1]}
        if po["position"] not in hashmap[po["department"]][po["subdepartment"]]:
            hashmap[po["department"]][po["subdepartment"]][po["position"]] = len(hashmap[po["department"]][po["subdepartment"]])-1


with open("table-codes.csv", "w") as tab:
    print >> tab, "code,department,subdepartment,position"
    for d in hashmap:
        for s in hashmap[d]:
            if s == "_id":
                continue
            for p in hashmap[d][s]:
                if p == "_id":
                    continue
                code = "%s-%s-%02d" % (hashmap[d]["_id"], hashmap[d][s]["_id"], hashmap[d][s][p])
                print >> tab, ",".join(['"%s"' % a.replace('"', '""') for a in [code, d, s, p]])

allyears = [minyear]
y = minyear + 1
while y < 2016:
    allyears.append(y)
    y += 1

table = {}
listdeps = set()
listdeps2 = set()
depmatrix = {}
depmatrix2 = {}
with open("people-years.csv", "w") as years, open("people-matrix.csv", "w") as mat:
    positions_head.append("year")
    print >> years, ",".join(positions_head)
    print >> mat, "id,%s" % ','.join([str(a) for a in allyears])
    for p in people:
        line = [p["id"]]
        y0 = yearize(p["positions"][0])
        cury = allyears[0]
        while cury < y0:
            cury += 1
            line.append("")
        lastdep = ""
        lastdep2 = ""
        for i, po in enumerate(p["positions"]):
            if po["department"] not in table:
                table[po["department"]] = {}
            po["year"] = yearize(po)
            dep = ("%s / %s" % (po["department"], po["subdepartment"])).replace(",", "")
            if po["year"] > 2002:
                if lastdep and lastdep != dep:
                    listdeps.add(lastdep)
                    listdeps.add(dep)
                    if lastdep not in depmatrix:
                        depmatrix[lastdep] = {}
                    if dep not in depmatrix[lastdep]:
                        depmatrix[lastdep][dep] = 0
                    depmatrix[lastdep][dep] += 1
                if lastdep2 and lastdep2 != po["department"]:
                    listdeps2.add(po["department"])
                    if lastdep2 not in depmatrix2:
                        depmatrix2[lastdep2] = {}
                    if po['department'] not in depmatrix2[lastdep2]:
                        depmatrix2[lastdep2][po['department']] = 0
                    depmatrix2[lastdep2][po["department"]] += 1
            lastdep = dep
            lastdep2 = po['department']
            code = "%s-%s-%02d" % (hashmap[po["department"]]["_id"], hashmap[po["department"]][po["subdepartment"]]["_id"], hashmap[po["department"]][po["subdepartment"]][po["position"]])
            try:
                nexty = yearize(p['positions'][i+1])
            except:
                nexty = 2016
            while po["year"] < nexty:
                if po["year"] not in table[po["department"]]:
                    table[po["department"]][po["year"]] = 0
                table[po["department"]][po["year"]] += 1
                line.append(code)
                print >> years, p["id"]+","+",".join(['"%s"' % a.encode("utf-8").replace('"', '""') if type(a) is unicode else str(a) for a in [po[h] for h in positions_head if h != "id"]])
                po["year"] += 1
        print >> mat, ",".join(line)

with open("departments-years.csv", "w") as depts:
    print >> depts, "department,year,total"
    for d in table:
        for y in table[d]:
            print >> depts, ",".join([d, str(y), str(table[d][y])])

listdeps = list(listdeps)
listdeps.sort()
with open("subdepartments-matrix.csv", "w") as depts:
    print >> depts, "left_department," + ",".join(listdeps)
    for d in listdeps:
        print >> depts, "%s," % d + ",".join([str(depmatrix.get(d, {d2: 0}).get(d2, 0)) for d2 in listdeps])

listdeps = list(listdeps2)
listdeps.sort()
with open("departments-matrix.csv", "w") as depts:
    print >> depts, "left_department," + ",".join(listdeps)
    for d in listdeps:
        print >> depts, "%s," % d + ",".join([str(depmatrix2.get(d, {d2: 0}).get(d2, 0)) for d2 in listdeps])


