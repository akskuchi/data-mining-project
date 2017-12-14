import logging
import statistics

import read_graph
import networkx as nx

logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def compute_statistics(component):
    shortest_paths = statistics.compute_shortest_path_distances(component)

    logger.info('mean distance: {}'.format(statistics.mean_distance(shortest_paths)))
    logger.info('median distance: {}'.format(statistics.median_distance(shortest_paths)))
    logger.info('diameter: {}'.format(statistics.diameter(component)))
    # logger.info('effective distance: {}'.format(statistics.effective_diameter(component)))


def wiki_vote_network():
    directed_graph = read_graph.as_directed('resources/wiki-Vote.txt')

    lscc = max(nx.strongly_connected_component_subgraphs(directed_graph), key=len)
    # lwcc = max(nx.weakly_connected_component_subgraphs(nx.to_undirected(directed_graph)), key=len)

    logger.info('nodes and edges of lscc: {}, {}'.format(nx.number_of_nodes(lscc), nx.number_of_edges(lscc)))
    # logger.info('nodes and edges of lwcc: {}{}'.format(nx.number_of_nodes(lwcc), nx.number_of_edges(lwcc)))

    compute_statistics(lscc)


if __name__ == '__main__':
    logger.info('starting project')
    wiki_vote_network()
