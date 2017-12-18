import logging

import graph_tool as gt
from graph_tool import topology
import networkx as nx
import read_graph
import statistics

logger = logging.getLogger('analysis')
hdlr = logging.FileHandler('../output.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def convert_nx_gt(graph):
    edge_list = graph.edges()

    sources = []
    targets = []

    for e in edge_list:
        sources.append(e.source())
        targets.append(e.target())

    edge_list = zip(sources, targets)
    return nx.DiGraph(edge_list)


def compute_statistics(component, directed=True):
    shortest_paths = statistics.compute_shortest_path_distances(component, directed)
    # shortest_paths = statistics.compute_shortest_path_distances_parallel(convert_nx_gt(component))
    logger.info('computed shortest path lengths')

    logger.info('mean distance: {}'.format(statistics.mean_distance(shortest_paths)))
    logger.info('median distance: {}'.format(statistics.median_distance(shortest_paths)))
    logger.info('diameter: {}'.format(statistics.diameter(shortest_paths)))
    logger.info('effective diameter: {}'.format(statistics.effective_diameter(shortest_paths)))


def analyse(filename):
    directed_graph = read_graph.as_directed(filename)

    lscc = gt.GraphView(directed_graph, vfilt=topology.label_largest_component(directed_graph, directed=True))
    logger.info('nodes and edges of lscc: {}, {}'.format(lscc.num_vertices(), lscc.num_edges()))
    compute_statistics(lscc, True)

    # lwcc = gt.GraphView(directed_graph, vfilt=topology.label_largest_component(directed_graph, directed=False))
    # logger.info('nodes and edges of lwcc: {}, {}'.format(lwcc.num_vertices(), lwcc.num_edges()))
    # compute_statistics(lwcc, False)
