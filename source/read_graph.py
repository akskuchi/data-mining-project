import logging

import networkx as nx
import os

logger = logging.getLogger('read graph')
hdlr = logging.FileHandler('../output.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def as_directed(edge_list_file):
    path = os.path.join(os.path.dirname(__file__), '..', edge_list_file)
    graph = nx.read_edgelist(path, create_using=nx.DiGraph(), nodetype=int)
    logger.info('number of nodes in the graph: {}'.format(len(graph.nodes())))
    return graph


def as_undirected(edge_list_file):
    path = os.path.join(os.path.dirname(__file__), '..', edge_list_file)
    logger.info(path)
    graph = nx.read_edgelist(path, nodetype=int)
    logger.info('number of nodes in the graph: {}'.format(len(graph.nodes())))
    return graph
