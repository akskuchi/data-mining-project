import logging

import networkx as nx

import read_graph
import statistics

logger = logging.getLogger('analysis')
hdlr = logging.FileHandler('../output.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def compute_statistics(component):
    shortest_paths = statistics.compute_shortest_path_distances(component)
    logger.info('computed shortest path lengths')

    logger.info('mean distance: {}'.format(statistics.mean_distance(shortest_paths)))
    logger.info('median distance: {}'.format(statistics.median_distance(shortest_paths)))
    logger.info('diameter: {}'.format(statistics.diameter(component)))
    logger.info('effective diameter: {}'.format(statistics.effective_diameter(component)))


def analyse(filename):
    directed_graph = read_graph.as_directed(filename)

    lscc = max(nx.strongly_connected_component_subgraphs(directed_graph), key=len)
    logger.info('nodes and edges of lscc: {}, {}'.format(nx.number_of_nodes(lscc), nx.number_of_edges(lscc)))
    compute_statistics(lscc)

    lwcc = max(nx.weakly_connected_component_subgraphs(directed_graph), key=len)
    lwcc = nx.to_undirected(lwcc)
    logger.info('nodes and edges of lwcc: {}, {}'.format(nx.number_of_nodes(lwcc), nx.number_of_edges(lwcc)))
    compute_statistics(lwcc)
