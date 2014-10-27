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
  "Высшее образование": "Higher education",
  "Неполное высшее образование": "Undergraduate education",
  "Основное общее образование": "Basic general education",
  "Начальное (общее) образование": "Primary general education",
  "Среднее (полное) общее образование": "Secondary general education",
  "Начальное профессиональное образование": "Primary professional education",
  "Среднее профессиональное образование": "Secondary professional education",
  "Наладчик VI разряда*": "Fixer",
  "Монтажник VI разряда*": "Installer",
  "Электромонтер VI разряда*": "Electrician",
  "Слесарь-сантехник VI разряда*": "Plumber",
  "Слесарь VI разряда*": "Locksmith",
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
positions_head = ["id","position_order","date","salary_rate","position","salary","department","subdepartment"]
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

table = {}
with open("people-years.csv", "w") as years:
    positions_head.append("year")
    print >> years, ",".join(positions_head)
    for p in people:
        for i, po in enumerate(p["positions"]):
            if po["department"] not in table:
                table[po["department"]] = {}
            po["year"] = yearize(po)
            try:
                nexty = yearize(p['positions'][i+1])
            except:
                nexty = 2016
            while po["year"] < nexty:
                if po["year"] not in table[po["department"]]:
                    table[po["department"]][po["year"]] = 0
                table[po["department"]][po["year"]] += 1
                print >> years, p["id"]+","+",".join(['"%s"' % a.encode("utf-8").replace('"', '""') if type(a) is unicode else str(a) for a in [po[h] for h in positions_head if h != "id"]])
                po["year"] += 1

with open("departments-years.csv", "w") as depts:
    print >> depts, "department,year,total"
    for d in table:
        for y in table[d]:
            print >> depts, ",".join([d, str(y), str(table[d][y])])

