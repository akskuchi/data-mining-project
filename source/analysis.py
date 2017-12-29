import logging
import random

import networkx as nx
import bitarray

import read_graph
import statistics
import time
import numpy as np

logger = logging.getLogger('analysis')
hdlr = logging.FileHandler('../output.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)


def n_random_combinations(iterable, n, r=2):
    r_pairs = []
    iterable = tuple(iterable)
    for i in range(n):
        r_pairs.append(random_combination(iterable, r))
    return r_pairs


def random_combination(iterable, r=2):
    pool = tuple(iterable)
    n = len(pool)
    indices = sorted(random.sample(range(n), r))
    return tuple(pool[i] for i in indices)


def n_random_permutations(iterable, n, k=2):
    r_pairs = []
    iterable = tuple(iterable)
    for i in range(n):
        r_pairs.append(tuple(random.sample(tuple(iterable), k)))
    return r_pairs


def compute_statistics(shortest_paths):
    logger.info('mean distance: {}'.format(statistics.mean_distance(shortest_paths)))
    logger.info('median distance: {}'.format(statistics.median_distance(shortest_paths)))
    logger.info('diameter: {}'.format(statistics.diameter(shortest_paths)))
    logger.info('effective diameter: {}'.format(statistics.effective_diameter(shortest_paths)))


def exact_analysis(filename, component_type=None):
    if component_type == 'lscc':
        lscc = read_graph.as_directed(filename)
        logger.info('nodes and edges of lscc: {}, {}'.format(nx.number_of_nodes(lscc), nx.number_of_edges(lscc)))
        sources = [source for source in lscc]
        shortest_paths = statistics.compute_shortest_path_distances_parallel(lscc, sources)
        logger.info('computed shortest path lengths')
        compute_statistics(shortest_paths)

    elif component_type == 'lwcc':
        lwcc = read_graph.as_undirected(filename)
        logger.info('nodes and edges of lwcc: {}, {}'.format(nx.number_of_nodes(lwcc), nx.number_of_edges(lwcc)))
        sources = [source for source in lwcc]
        shortest_paths = statistics.compute_shortest_path_distances_parallel(lwcc, sources)
        logger.info('computed shortest path lengths')
        compute_statistics(shortest_paths)


def random_pairs(filename, cc_type):
    start = time.time()

    accuracy_param = 0.1
    component = None

    if cc_type == 'lscc':
        component = read_graph.as_directed(filename)
    elif cc_type == 'lwcc':
        component = read_graph.as_undirected(filename)

    sample_pairs = n_random_permutations(component.nodes(), int(accuracy_param * nx.number_of_nodes(component)))
    num_sample_pairs = int(accuracy_param * nx.number_of_nodes(component))
    shortest_paths = statistics.compute_shortest_path_distances_pairs(component, sample_pairs, num_sample_pairs)
    logger.info('computed shortest path lengths')
    compute_statistics(shortest_paths)
    print('complete code: \t', int(divmod(time.time() - start, 60)[0]), 'min:', int(divmod(time.time() - start, 60)[1]), 's')


def random_sources(filename, cc_type):
    start = time.time()

    accuracy_param = 0.1
    component = None

    if cc_type == 'lscc':
        component = read_graph.as_directed(filename)
    elif cc_type == 'lwcc':
        component = read_graph.as_undirected(filename)

    num_sample_sources = int(accuracy_param * nx.number_of_nodes(component))
    sample_sources = random.sample(component.nodes(), num_sample_sources)
    shortest_paths = statistics.compute_shortest_path_distances_parallel(component, sources=sample_sources)
    logger.info('computed shortest path lengths')
    compute_statistics(shortest_paths)
    print('complete code: \t', int(divmod(time.time() - start, 60)[0]), 'min:', int(divmod(time.time() - start, 60)[1]), 's')


def approx_algo_fm(filename, cc_type, num_bitstrings=8, max_iter=64, len_bitstrings=64):
    logger.info('Flajolet Martin approximation')
    component = None

    if cc_type == 'lscc':
        component = read_graph.as_directed(filename)
    elif cc_type == 'lwcc':
        component = read_graph.as_undirected(filename)

    nodes = nx.nodes(component)
    num_nodes = np.max(nodes) + 1

    bitmaps = np.zeros((num_bitstrings, max_iter, num_nodes, len_bitstrings), dtype=np.bool)

    for node in nodes:
        for l in range(num_bitstrings):
            bitmaps[l, 0, node] = np.array(list(np.binary_repr(len(list(nx.neighbors(component, node))), width=len_bitstrings))).astype(bool)

    h_max = -1
    neighborhood = np.zeros(max_iter)

    for h in range(1, max_iter):
        changed = 0
        for node in nodes:
            for l in range(1, num_bitstrings):
                neighbors = nx.neighbors(component, node)
                bitmaps[l, h, node] = bitmaps[l, h - 1, node]
                for neighbor in neighbors:
                    bitmaps[l, h, node] |= bitmaps[l, h - 1, neighbor]

            for l in range(1, num_bitstrings):
                if not np.array_equal(bitmaps[l, h, node], bitmaps[l, h - 1, node]):
                    changed += 1

        neighborhood[h] = statistics.neighborhood_sum(bitmaps, nodes, num_bitstrings, h)
        if changed == 0:
            h_max = h
            break

    logger.info('diameter of the component: {}'.format(h_max))
    logger.info('mean distance of the component: {}'.format(int(np.mean(neighborhood))))
    # smallest_h = -1
    # perfect_match = False
    # for h in range(max_iter):
    #     if neighborhood[h] == 0.9 * neighborhood[h_max]:
    #         perfect_match = True
    #         smallest_h = h
    #         break
    #     elif neighborhood[h] > 0.9 * neighborhood[h_max]:
    #         smallest_h = h
    #         break
    #
    # if perfect_match:
    #     logger.info('effective diameter: ', smallest_h)
    # else:
    #     logger.info('effective diameter: ', statistics.interpolate(smallest_h, h_max, neighborhood))


def approx_analysis(filename, component_type, scheme):
    if scheme == 1:
        random_pairs(filename, component_type)
    elif scheme == 2:
        random_sources(filename, component_type)
    elif scheme == 3:
        approx_algo_fm(filename, component_type)
