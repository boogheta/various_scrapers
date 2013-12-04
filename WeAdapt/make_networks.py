#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, codecs, csv
import networkx as nx
from networkx.readwrite import json_graph
from pprint import pprint

def write_graph_in_format(graph, filename, fileformat='gexf') :
    if fileformat.lower() == 'json' :
        json.dump(json_graph.node_link_data(graph), open(filename+".json",'w'))
    else :
        nx.write_gexf(graph, filename+".gexf")

def add_edge_weight(graph, node1, node2):
    if graph.has_edge(node1, node2):
        graph[node1][node2]['weight'] += 1
    else:
        graph.add_edge(node1, node2, weight=1)

def clean_empty_nodes(graph, field):
    for n in graph.nodes():
        if graph.node[n] != {} and not graph.node[n][field]:
            graph.remove_node(n)

def clean_unused(graph, node_type, field, value=1):
    for n in graph.nodes():
        if graph.node[n] != {} and graph.node[n]['type_node'] == node_type and graph.node[n][field] < value:
            graph.remove_node(n)

from json_to_sql import *
with open('placemarks_coords.csv', 'rb') as places_coords_file:
    try:
        for row in csv.DictReader(places_coords_file):
            placemarks[int(row['placemark_id'])]['country'] = row['country']
    except Exception as e:
        print "Problem reading placemarks_coords.csv :"
        raise e

# Prepare nodes
def add_org_nodes(graph):
    for oid,org in organisations.iteritems():
        graph.add_node('o%s'%oid, label=org['name'], nb_projects=0, nb_direct_tags=0, type_node='organisation')
    for op in orgas_places.itervalues():
        graph.node['o%s'%op['organisation_id']]['nb_projects'] += 1
    for ot in orgas_tags.itervalues():
        graph.node['o%s'%ot['organisation_id']]['nb_direct_tags'] += 1
    for pa in places_authors.itervalues():
        if authors[pa['author_id']]['organisation_id']:
            graph.node['o%s'%authors[pa['author_id']]['organisation_id']]['nb_projects'] += 1

def add_tag_nodes(graph):
    for tid,tag in tags.iteritems():
        graph.add_node('t%s'%tid, label=tag['tag'], nb_projects=0, nb_orgas=0, type_node='tag')
    for pt in places_tags.itervalues():
        graph.node['t%s'%pt['tag_id']]['nb_projects'] += 1
    for ot in orgas_tags.itervalues():
        graph.node['t%s'%ot['tag_id']]['nb_orgas'] += 1

def add_country_nodes(graph):
    for pm in placemarks.itervalues():
        if graph.has_node(pm['country']):
            graph.node[pm['country']]['nb_projects'] += 1
        else:
            graph.add_node(pm['country'], nb_projects=1, type_node='country')

#G = nx.Graph()
#add_country_nodes(G)
#write_graph_in_format(G, "weadapt-countries-nodes")
#
#H = nx.Graph()
#add_tag_nodes(H)
#write_graph_in_format(H, "weadapt-tags-nodes")
#
#H1 = nx.Graph()
#add_tag_nodes(H1)
#clean_empty_nodes(H1, 'nb_projects')
#write_graph_in_format(H1, "weadapt-tags-with-projects-nodes")
#
#H2 = nx.Graph()
#add_tag_nodes(H2)
#clean_empty_nodes(H2, 'nb_orgas')
#write_graph_in_format(H2, "weadapt-tags-with-orgas-nodes")
#
#I = nx.Graph()
#add_org_nodes(I)
#write_graph_in_format(I, "weadapt-orgs-nodes")



## Mono org --(aut)--pm--(aut)--> org
G1 = nx.Graph()
add_org_nodes(G1)
clean_empty_nodes(G1, 'nb_projects')
porgs = {}   # {id_proj: [list orgs])
for pa in places_authors.itervalues():
    if authors[pa['author_id']]['organisation_id']:
        if pa['placemark_id'] not in porgs:
            porgs[pa['placemark_id']] = []
        porgs[pa['placemark_id']].append('o%s'%authors[pa['author_id']]['organisation_id'])
for op in orgas_places.itervalues():
    oid = 'o%s'%op['organisation_id']
    if op['placemark_id'] not in porgs:
        porgs[op['placemark_id']] = []
    if oid not in porgs[op['placemark_id']]:
        porgs[op['placemark_id']].append(oid)
for orgs in porgs.itervalues():
    while len(orgs):
        co = orgs.pop()
        for o2 in orgs:
            add_edge_weight(G1, co, o2)
write_graph_in_format(G1, "weadapt-mono-orgas_projects")

## Mono tag --pm--> tag
G2 = nx.Graph()
add_tag_nodes(G2)
clean_empty_nodes(G2, 'nb_projects')
ptags = {}   # {id_proj: [list tags])
for pt in places_tags.itervalues():
    tid = 't%s'%pt['tag_id']
    if pt['placemark_id'] not in ptags:
        ptags[pt['placemark_id']] = []
    else:
        for tagid in ptags[pt['placemark_id']]:
            add_edge_weight(G2, tid, tagid)
    if tid not in ptags[pt['placemark_id']]:
        ptags[pt['placemark_id']].append(tid)
write_graph_in_format(G2, "weadapt-mono-tags_projects")


## Bipa country --pm--> tag (>1)
G3 = nx.DiGraph()
add_country_nodes(G3)
add_tag_nodes(G3)
clean_unused(G3, 'tag', 'nb_projects', 2)
for pt in places_tags.itervalues():
    tid = 't%s'%pt['tag_id']
    if G3.has_node(tid):
        add_edge_weight(G3, placemarks[int(pt['placemark_id'])]['country'], tid)
write_graph_in_format(G3, "weadapt-bi-countries-tags_projects")

## Bipa orga ----> tag (>1)
G4 = nx.DiGraph()
add_org_nodes(G4)
add_tag_nodes(G4)
clean_unused(G4, 'tag', 'nb_orgas', 2)
clean_unused(G4, 'organisation', 'nb_direct_tags', 1)
for ot in orgas_tags.itervalues():
    tid = 't%s'%ot['tag_id']
    oid = 'o%s'%ot['organisation_id']
    if G4.has_node(tid) and G4.has_node(oid):
        add_edge_weight(G4, oid, tid)

write_graph_in_format(G4, "weadapt-bi-orgas-tags")

## Bipa orga --pm--> tag (>1)
G5 = nx.DiGraph()
add_org_nodes(G5)
add_tag_nodes(G5)
clean_unused(G5, 'organisation', 'nb_projects', 1)
clean_unused(G5, 'tag', 'nb_projects', 2)
porgs = {}
for op in orgas_places.itervalues():
    oid = 'o%s'%op['organisation_id']
    if op['placemark_id'] not in porgs:
        porgs[op['placemark_id']] = []
    if oid not in porgs[op['placemark_id']]:
        porgs[op['placemark_id']].append(oid)
for pt in places_tags.itervalues():
    tid = 't%s'%pt['tag_id']
    if pt['placemark_id'] in porgs and G5.has_node(tid):
        for o in porgs[pt['placemark_id']]:
            add_edge_weight(G5, o, tid)
for n in G5.nodes():
    edges = G5.out_edges(n) + G5.in_edges(n)
    n_edges = len(edges)
    if G5.node[n]['type_node'] == 'tag' and n_edges < 2:
        for e in edges:
            G5.remove_edge(*e)
        G5.remove_node(n)
    elif G5.node[n]['type_node'] == 'organisation' and not n_edges:
        G5.remove_node(n)
write_graph_in_format(G5, "weadapt-bi-orgas-tags_projects")

## Bipa orga --pm--> country
G6 = nx.DiGraph()
add_country_nodes(G6)
add_org_nodes(G6)
for op in orgas_places.itervalues():
    add_edge_weight(G6, 'o%s'%op['organisation_id'], placemarks[int(op['placemark_id'])]['country'])
for n in G6.nodes():
    edges = G6.out_edges(n) + G6.in_edges(n)
    if G6.node[n]['type_node'] == 'organisation' and not len(edges):
        G6.remove_node(n)
write_graph_in_format(G6, "weadapt-bi-orgas-countries_projects")

