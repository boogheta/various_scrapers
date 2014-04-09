#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Meetup's API doc: http://www.meetup.com/meetup_api/docs/

import sys, os, re
import requests, urllib
import json, yaml
from pymongo import Connection
import time

mongo = Connection()
mongo.drop_database('meetup')
db = mongo['meetup']

users = {}
events = {}
queriedmembers = []
bad_fields = ['venue', 'fee']

api_url = "http://api.meetup.com/2/%s.json?key=4b3617803cf752618c793195955&"

with open(os.path.join('data', 'groups.yml'), 'r') as f:
    groups = yaml.load(f.read()).values()

escape_url = lambda url: os.path.join('data', urllib.quote(url).replace("/", "%2F"))

def download_page(url):
    urlfile = escape_url(url)
    if os.path.exists(urlfile):
        try:
            with open(urlfile, 'r') as f:
                res = f.read()
            return res, False
        except Exception as e:
            print >> sys.stderr, "[ERROR] while reading cached file %s (%s: %s)", (urlfile, type(e), e)
            pass
    time.sleep(0.1)
    res = requests.get(url).content
    with open(urlfile, 'w') as f:
        f.write(res)
    return res, True

def download_json(url):
    content, new = download_page(url)
    try:
        res = json.loads(content)
    except Exception as e:
        print >> sys.stderr, "[ERROR] JSON badly formatted %s: %s" % (url, content.encode('utf-8'))
        res = {}
    if new and res and not 'problem' in res:
        print >> sys.stderr, "[DEBUG] Downloaded and cached %s" % url
    if "metas" in res and "next" in res['metas'] and res['metas']['next']:
        more = download_json(res['metas']['next'])
        res['results'] += more['results']
    return res

re_member_ids = re.compile(r'/members/(\d+)[\'"\\]')
def download_members(group_slug, event_id):
    url = "http://www.meetup.com/%s/events/%s/" % (group_slug, event_id)
    extra = "?__fragment=past-attendee-list&p_attendeeList=%s"
    page = 0
    content, _ = download_page(url)
    evusers = []
    new = True
    while content and new:
        new = 0
        for i in re_member_ids.findall(content):
            i = int(i)
            if i not in evusers:
                new += 1
                evusers.append(i)
        page += 1
        content, _ = download_page(url + extra % page)
    evusers.sort()
    print "[INFO] -> found %s users registered for event %s of %s" % (len(evusers), event_id, group_slug)
    return evusers

def get_api_results(method, group, dico):
    group_url = api_url % method + "group_id=%s" % group['id']
    if method == "events":
        group_url += "&status=upcoming,past"
    res = download_json(group_url)
    ids = []
    if not 'results' in res:
        print >> sys.stderr, "[WARNING] Error while downloading %s:" % group_url, res
        os.remove(escape_url(group_url))
        time.sleep(5)
    else:
        for el in res['results']:
            el['_id'] = el['id']
            ids.append(el['id'])
            if el['id'] not in dico:
                dico[el['id']] = el
            if method == "events":
                el['group'] = group['id']
            elif method == "members":
                el['groups'] = []
                if el['id'] not in queriedmembers:
                    member_url = api_url % "groups" + "member_id=%s" % el['id']
                    membergroups = download_json(member_url)
                    if not 'results' in membergroups:
                        os.remove(escape_url(member_url))
                        if 'code' in membergroups and membergroups['code'] != "not_authorized":
                            print >> sys.stderr, "[WARNING] Error while downloading %s:" % member_url, membergroups
                    else:
                        el['groups'] = [int(g['id']) for g in membergroups['results']]
                if group['id'] not in el:
                    el['groups'].append(group['id'])
    group[method] = ids

for group in groups:
    print "[INFO] * Query %s %s " % (group['name'].encode('utf-8'), group['link'].encode('utf-8'))
    # Get group users
    get_api_results("members", group, users)
    # Get group events
    events = {}
    get_api_results("events", group, events)
    # Save data in corresponding table
    group['_id'] = group['id']
    db["groups"].save(group)
    for e in events.values():
        e['_id'] = e['id']
        e['members'] = download_members(group['link'].rstrip('/').replace('http://www.meetup.com/', ''), e['id'])
        db["events"].save(e)
    for u in users.values():
        u['_id'] = u['id']
        db['users'].save(u)

