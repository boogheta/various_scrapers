#!/usr/bin/env python
# -!- coding: utf-8

import csv, sys

guests = {}
with open('TI_Commission_guests.csv') as f:
    for row in csv.DictReader(f):
        guests[row["id"]] = row

headers = []
meetings = []
with open('TI_Commission_meetings.csv') as f:
    for m in csv.DictReader(f):
        if not headers:
            for k in m.keys():
                headers.append(k)
        try:
            guest = guests[m["guestid"]]
            for k in guest.keys():
                gk = "guest_%s" % k
                if gk not in headers:
                    headers.append(gk)
                m[gk] = guest[k]
        except:
            if m["guest"]:
                m["guest_name"] = m["guest"]
            else:
                print >> sys.stderr, "WARNING, guest could not be found", m
        del(m["guest"])
        meetings.append(m)

with open('TI_Commission_meetings_with_guests.csv', 'w') as f:
    writer = csv.DictWriter(f, fieldnames=headers)
    writer.writeheader()
    for m in meetings:
        writer.writerow(m)

