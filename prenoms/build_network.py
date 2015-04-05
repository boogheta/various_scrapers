#!/usr/bin/env node
# -*- coding: utf-8 -*-

import sys, os
import csv, json
import networkx as nx
from networkx.readwrite import json_graph

class Graph(nx.Graph):

    def write_graph_in_format(self, filerootname, fileformat='gexf'):
        fileformat = fileformat.lower()
        filename = "%s.%s" % (filerootname.replace(" ", "_"), fileformat)
        if fileformat == 'json':
            with open(filename, 'w') as f:
                json.dump(json_graph.node_link_data(self), f)
        elif fileformat == 'net':
            nx.write_pajek(self, filename)
        elif fileformat == 'gexf':
            nx.write_gexf(self, filename)

    def add_node(self, node, **kwargs):
        if self.has_node(node):
            self.node[node]['occurences'] += 1
        else:
            nx.Graph.add_node(self, node, occurences=1)
        for key, value in kwargs.items():
            try:
                value = float(value)
            except ValueError:
                pass
            if key in self.node[node] and \
              isinstance(value, float) and isinstance(self.node[node][key], float):
                self.node[node][key] += value
            elif key not in self.node[node]:
                self.node[node][key] = value
        if "label" not in self[node]:
            self.node[node]["label"] = node

    def add_edge(self, node1, node2, weight=1):
        if not self.has_node(node1):
            self.add_node(node1)
        if not self.has_node(node2):
            self.add_node(node2)
        if self.has_edge(node1, node2):
            self[node1][node2]['weight'] += weight
        else:
            nx.Graph.add_edge(self, node1, node2, weight=weight)

    def clear_unlinked_nodes(self):
        for n in self.copy().nodes_iter():
            if not self.degree(n):
                self.remove_node(n)


if __name__ == "__main__":
    source = sys.argv[1]
    G = Graph()
    with open(source) as f:
        for n in json.load(f):
            nb_recent_births=sum(n["years_frequencies"][-5:])
            G.add_node("%s_%s"%(n["name"],n["sex"]), sex=n["sex"], name=n["name"],url=n["url"],nb_recent_births=nb_recent_births)
            for s in n["similars"]:
                G.add_edge("%s_%s"%(n["name"],n["sex"]),"%s_%s"%(s["name"],n["sex"]),s["weight"])

    G.clear_unlinked_nodes()

    output = source.replace(".json", "")
    #G.write_graph_in_format(output, "net")
    #G.write_graph_in_format(output, "json")
    G.write_graph_in_format(output, "gexf")

