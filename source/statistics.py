import networkx as nx
import numpy as np


def compute_shortest_path_distances(graph):
    shortest_paths = dict(nx.all_pairs_shortest_path_length(graph))
    distances = []
    for key1, value1 in shortest_paths.items():
        for key2, value2 in value1.items():
            distances.append(value2)

    return distances


def mean_distance(distances):
    return np.mean(distances)


def median_distance(distances):
    return np.median(distances)


def diameter(graph):
    return nx.diameter(graph)


def effective_diameter(graph):
    """
    TODO: http://www.l3s.de/~anand/lsdm16/lectures/lsdm16-lecture-7-graphs.pdf
    :param graph: the connected component
    """
    eccentricities = nx.eccentricity(graph)
    distances = [value for value in eccentricities.values()]

    return np.max(distances)
