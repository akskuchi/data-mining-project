from graph_tool import topology

import networkx as nx
import numpy as np
import multiprocessing as mp
from functools import partial


def compute_shortest_path_distances_parallel(graph):
    num_cores = mp.cpu_count()
    pool = mp.Pool(processes=num_cores)

    parallel_function = partial(nx.single_source_shortest_path_length, graph)
    sources = [source for source in graph]
    shortest_paths = pool.map(parallel_function, sources)

    pool.close()
    pool.join()

    distances = []
    for _dict in shortest_paths:
        for key, value in _dict.items():
            distances.append(value)

    return distances


def compute_shortest_path_distances(graph, directed):
    shortest_path_lengths = topology.shortest_distance(graph, directed=directed)
    distances = []
    vertices = graph.get_vertices()

    for v1 in vertices:
        for v2 in vertices:
            if v1 != v2:
                distances.append(shortest_path_lengths[v1][v2])

    return distances


def mean_distance(distances):
    return np.mean(distances)


def median_distance(distances):
    return np.median(distances)


def diameter(distances):
    return np.max(distances)


def effective_diameter(distances):
    return np.percentile(distances, 90)
