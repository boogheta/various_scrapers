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

G = nx.DiGraph()
with open('/tmp/all-tweets-aime-with-discussions.csv', 'rb') as csvfile:
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

write_graph_in_format(G, "aime-tweets-conv")

