import csv
import logging

import os
from graph_tool.all import *

logger = logging.getLogger('read graph')
hdlr = logging.FileHandler('../output.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def as_directed(edge_list_file):
    path = os.path.join(os.path.dirname(__file__), '..', edge_list_file)
    graph = Graph()
    network = open(path, 'r')
    read_network = csv.reader(network, delimiter='\t', skipinitialspace=True)

    for edge in read_network:
        graph.add_edge(int(edge[0]), int(edge[1]))

    network.close()
    graph.set_directed(True)
    return graph


def as_undirected(edge_list_file):
    return as_directed(edge_list_file).set_directed(False)
