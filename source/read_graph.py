import logging

import networkx as nx
import os

# create logger
logger = logging.getLogger('read graph')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def as_directed(edge_list_file):
    path = os.path.join(os.path.dirname(__file__), '..', edge_list_file)
    logger.info(path)
    graph = nx.read_edgelist(path, create_using=nx.DiGraph(), nodetype=int)
    logger.info('number of nodes in the graph: {}'.format(len(graph.nodes())))
    return graph


def as_undirected(edge_list_file):
    path = os.path.join(os.path.dirname(__file__), '..', edge_list_file)
    logger.info(path)
    graph = nx.read_edgelist(path, nodetype=int)
    logger.info('number of nodes in the graph: {}'.format(len(graph.nodes())))
    return graph
