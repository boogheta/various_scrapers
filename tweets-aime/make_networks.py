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

def clean_low_degree(graph, min_degree=1):
    for n in graph.nodes():
        if graph.degree(n) < min_degree:
            graph.remove_node(n)

G = nx.DiGraph()
with open('all-tweets-aime-with-discussions.csv', 'rb') as csvfile:
    try:
        for row in csv.DictReader(csvfile):
            if not G.has_node(row['id']):
                G.add_node(row['id'])
            G.node[row['id']]['label'] = row['text'].decode('utf-8')
            G.node[row['id']]['user'] = row['user_id']
            G.node[row['id']]['lang'] = row['lang']
            if row['reply_to_id']:
                if not G.has_node(row['reply_to_id']):
                    G.add_node(row['reply_to_id'])
                G.add_edge(row['reply_to_id'], row['id'])
    except Exception as e:
        print "Problem reading placemarks_coords.csv :"
        raise e

clean_low_degree(G)
write_graph_in_format(G, "aime-tweets-conv")

