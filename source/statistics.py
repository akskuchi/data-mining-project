import networkx as nx
import numpy as np
import multiprocessing as mp
from functools import partial


def neighborhood_sum(b, n, k, h):
    neigh_sum = 0
    for ii in n:
        neigh_sum += neighborhood_func(b, k, h, ii)

    return neigh_sum


def neighborhood_func(b, k, h, i):
    s = 0
    for l in range(k):
        for _h in range(h):
            s += leftmost_zero(b[l, _h, i])

    return 2 ** (s / k) / 0.77351


def leftmost_zero(array):
    return np.where(array == 0)[0][0]


def compute_shortest_path_distances_pairs(component, pairs, num_pairs):
    distances = []
    counter = 0
    for (v1, v2) in pairs:
        distances.append(nx.shortest_path_length(component, v1, v2))
        if counter % int(num_pairs / 20) == 0:
            print(round(counter / num_pairs * 100, 1), '%')
        counter += 1

    return distances


def compute_shortest_path_distances_parallel(graph, sources):
    num_cores = mp.cpu_count()
    pool = mp.Pool(processes=num_cores)

    parallel_function = partial(nx.single_source_shortest_path_length, graph)
    shortest_paths = pool.map(parallel_function, sources)

    pool.close()
    pool.join()

    distances = []
    for _dict in shortest_paths:
        for key, value in _dict.items():
            distances.append(value)

    return distances


def mean_distance(distances):
    return np.mean(distances)


def median_distance(distances):
    return np.median(distances)


def diameter(distances):
    return np.max(distances)


def effective_diameter(distances):
    return np.percentile(distances, 90)


def interpolate(h, h_max, n_func):
    diameter_eff = h - 1
    diameter_eff += (0.9 * n_func[h_max] - n_func[h - 1]) / (n_func[h] - n_func[h - 1])
    return diameter_eff
