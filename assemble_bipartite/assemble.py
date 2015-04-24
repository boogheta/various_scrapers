#!/usr/bin/env python

import networkx as nx
from networkx_helpers import Graph

G = nx.read_gexf("delegation territory mapping.gexf", None, False)

goodnodes = [u"Brazil", u"Mexico", u"Peru", u"Ecuador", u"United States", u"Canada", u"France", u"United Kingdom", u"Poland", u"Russia", u"Japan", u"China", u"India", u"Bangladesh", u"Saudi Arabia", u"Iran", u"Australia", u"Philippines", u"Maldives", u"Ethiopia", u"Algeria", u"Democratic Republic of the Congo", u"Nigeria", u"South Africa", u"European Union", u"Amazon rainforest", u"Arctic Circle", u"Antarctic", u"Sahara", u"Forest", u"Soil", u"Ocean", u"Endangered species", u"Air (classical element)", u"Atmosphere", u"Indigenous peoples", u"Minority group ", u"Cloud computing", u"Environmental migrant", u"Mediterranean Sea", u"Religion", u"Tourism", u"Gaia hypothesis"]

G2 = Graph()

for n in G.nodes_iter():
    if n in goodnodes:
        G.node[n]["label"] = n
        G2.add_node(n, viz=G.node[n]["viz"])

done = set()
for e in G.edges_iter():
    done.add(e)
    if e[0] in goodnodes and e[1] in goodnodes:
        G2.add_edge(e[0], e[1], weight=G[e[0]][e[1]].get("weight", 1))
        print >> sys.stderr, 'ADD 1st level edge', e
    elif e[0] in goodnodes or e[1] in goodnodes:
        good = e[0] if e[0] in goodnodes else e[1]
        bad = e[1] if e[0] in goodnodes else e[0]
        for ed in nx.edges(G, bad):
            if ed in done or (ed[1], ed[0]) in done:
                continue
            other = ed[0] if ed[0] != bad else ed[1]
            if other in goodnodes:
                print >> sys.stderr, 'ADD 2nd level edge', good, other
                G2.add_edge(good, other, weight=min(G[good][bad].get("weight", 1), G[bad][other].get("weight", 1)))
            done.add(ed)

G2.write_graph_in_format("delegation territory mapping.assembled")
