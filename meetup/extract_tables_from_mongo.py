#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re, time
from datetime import datetime
from pymongo import Connection
db = Connection()['meetup']

def joinints(arr):
    return '|'.join([str(el) for el in arr])

def format_csv_arr(arr):
    return ','.join([e.strip() for e in ['"%s"' % el.replace('"', '""') if ',' in el or '"' in el else el for el in arr]])

def format_csv_dico(dico, fields):
    arr = [dico[field].encode('utf-8') if type(dico[field]) is unicode else str(dico[field]) for field in fields]
    return format_csv_arr(arr)

re_clean_newlines = re.compile(r'\s*[\n\r]+\s*', re.M|re.U)
def fill_same_fields(source, fields):
    dico = {}
    for f in fields:
        dico[f] = source.get(f, '')
    dico['US_state'] = source.get('state', '')
    dico['description'] = source.get('description', source.get('bio', ''))
    dico['description'] = re_clean_newlines.sub(r'<br>', dico['description'])
    dico['source_url'] = source.get('link', source.get('event_url', ''))
    return dico

def format_date(ts):
    if not ts:
        return ''
    return datetime.fromtimestamp(ts/1000).isoformat()[:10]

groups = {}
users = {}

# Write events table
# EVENTS/MEETUPS ID Nom de l'évènement  Date évènement  Heure évènement Lieu de l'évènement (qui n'est pas la ville, mais le nom d'une boîte où d'un endroit, le plus souvent : se présente comme une URL d'adresse GoogleMaps, possible de l'obtenir ?)    GROUP ID / Nom du groupe de l'évènement Texte de présentation / programme de l'évènement    Commentaires sur la page de l'évènement USERS ID / noms des participants au meetup  Si possible, nombre de participants au meetup (bon, cela peut se générer en additionnant les ID...) Si possible, l'évaluation du meetup : une note en nombre d'étoiles (/5)
with open("events.csv", "w") as f:
    header = 'id,name,date,city,US_state,country,location_name,location_coordinates,group_id,description,nb_registered_users,list_public_users_ids,average_rating,nb_ratings,source_url'
    fields = header.split(',')
    print >> f, header
    for e in db['events'].find():
        event = fill_same_fields(e, fields)
        if 'venue' in e:
            event.update(fill_same_fields(e['venue'], fields))
            event['location_name'] = e['venue']['name']
            event['location_coordinates'] = "%s,%s" % (e['venue']['lat'], e['venue']['lon'])
        elif 'how_to_find_us' in e:
            event['location_name'] = e['how_to_find_us']
        event['date'] = format_date(e['time'])
        event['group_id'] = e['group']
        event['nb_registered_users'] = max(e['headcount'], len(e['members']))
        event['list_public_users_ids'] = joinints(e['members'])
        if 'rating' in e:
            event['average_rating'] = e['rating']['average']
            event['nb_ratings'] = e['rating']['count']
        print >> f, format_csv_dico(event, fields)
        if e['group'] not in groups:
            groups[e['group']] = int(time.time())*1000
        groups[e['group']] = min(groups[e['group']], e['created'])
        for u in e['members']:
            if u not in users:
                users[u] = {'groups': [], 'events': []}
            users[u]['events'].append(e['id'])


# Write groups table
# GROUP ID (groupe meetup / nom) ; Ville du groupe, éventuellement code région pr USA (pas nécessairement indiquée ds le nom) ; Texte de présentation du groupe local ; Date de création du meetup ; Nombre de "Self Quantifiers" affiché ; Nombres d'évaluations du groupe ; Nombre de meetups passés ; Liste des évènements organisés (par ID ou par nom ?) ; Noms des orgaisateurs (ou ID des organisateurs) ; Tags "A propos de nous" (décrivant les thématiques d'inscription du meetup) ; Sponsors du groupe (facultatif)
with open("groups.csv", "w") as f:
    header = 'id,name,city,US_state,country,first_date,description,nb_public_members,nb_public_events,list_events_ids,source_url'
    fields = header.split(',')
    print >> f, header
    for g in db['groups'].find():
        group = fill_same_fields(g, fields)
        last_update = datetime.strptime(g['updated'][12:31], '%Y-%m-%dT%H:%M:%S').timetuple()
        group['first_date'] = format_date(groups.get(g['id'], time.mktime(last_update)*1000))
        group['nb_public_members'] = len(g['members'])
        group['nb_public_events'] = len(g['events'])
        group['list_events_ids'] = joinints(g['events'])
        print >> f, format_csv_dico(group, fields)
        for u in g['members']:
            if u not in users:
                users[u] = {'groups': [], 'events': []}
            users[u]['groups'].append(g['id'])


# Write users table
# USER ID (personnes inscrites à au moins 1 meetup QS)  QS GROUP(S) ID(s) (Groupes du Quantified Self)  Texte de présentation (facultatif)  Date à laquelle le meetup QS a été rejoint ("membre depuis...") Lieu (d'habitation de l'utilisateur - peut être différent du Meetup d'appartenance) "Centres d'intérêt" de l'utilisateur (liste de thèmes)  Intitulés/ID de l'ensemble des meetups dont l'utilisateur est membre ("Membre de X autres Meetups") "Salutations" publiées sur le mur de ce user (facultatif)   (Possible d'avoir les events/meetups auxquels l'individu a participé ?) >>> J'ai l'impression que non, tout doit être reconstruit à partir de l'analyse des EVENTS/MEETUPS. J'espère qu'il y a bien un identifiant unique pour chaque utilisateur... pour qu'on puisse recouper leur participation à des évènements et des groupes différents ! Apparaît (facultatif) sur la page des Users : liens vers comptes Facebook, Twitter ou LinkedIn, notamment...
with open("users.csv", "w") as f:
    header = 'id,name,city,US_state,country,description,interest_themes,list_groups_ids,list_events_ids,source_url'
    fields = header.split(',')
    print >> f, header
    for u in db['users'].find():
        user = fill_same_fields(u, fields)
        user['interest_themes'] = '|'.join([t['urlkey'] for t in u['topics']])
        user['list_groups_ids'] = joinints(users[u['id']]['groups'])
        user['list_events_ids'] = joinints(users[u['id']]['events'])
        print >> f, format_csv_dico(user, fields)

