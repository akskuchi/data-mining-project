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


def diameter(distances):
    return np.max(distances)


def effective_diameter(distances):
    return np.percentile(distances, 90)
