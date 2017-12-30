import logging
import random

import networkx as nx

import read_graph
import statistics
import time
import numpy as np
import matplotlib.pyplot as plt

logger = logging.getLogger('analysis')
hdlr = logging.FileHandler('../output.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

accuracy_array = [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]

# wiki-Vote stats
exact_median_lscc1, exact_mean_lscc1, exact_diameter_lscc1, exact_effective_diameter_lscc1 = 3, 2.876, 9, 4
exact_median_lwcc1, exact_mean_lwcc1, exact_diameter_lwcc1, exact_effective_diameter_lwcc1 = 3, 3.247, 7, 4

# soc-Epinions1 stats
exact_median_lscc2, exact_mean_lscc2, exact_diameter_lscc2, exact_effective_diameter_lscc2 = 4, 4.419, 16, 6
exact_median_lwcc2, exact_mean_lwcc2, exact_diameter_lwcc2, exact_effective_diameter_lwcc2 = 4, 4.310, 15, 5


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
    """
    compute the statistics based on the shortest-path-lengths
    :param shortest_paths: shortest-path-lengths
    """
    logger.info('mean distance: {}'.format(statistics.mean_distance(shortest_paths)))
    logger.info('median distance: {}'.format(statistics.median_distance(shortest_paths)))
    logger.info('diameter: {}'.format(statistics.diameter(shortest_paths)))
    logger.info('effective diameter: {}'.format(statistics.effective_diameter(shortest_paths)))


def exact_analysis(filename, component_type=None):
    """
    perform exact analysis for the component
    :param filename: component edgelist filename
    :param component_type: lscc / lwcc / graph
    """
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


def random_pairs(filename, cc_type, accuracy_param, plot=False):
    """
    selects random pairs to perform all-pair-shortest-paths
    :param filename: component edgelist filename
    :param cc_type: largest strongly/weakly connected component identifier (lscc / lwcc)
    :param accuracy_param: accuracy controlling param
    :param plot: True / False
    :return: shortest-path-lengths
    """
    start = time.time()

    component = None

    if cc_type == 'lscc':
        component = read_graph.as_directed(filename)
    elif cc_type == 'lwcc':
        component = read_graph.as_undirected(filename)

    sample_pairs = n_random_permutations(component.nodes(), int(accuracy_param * nx.number_of_nodes(component)))
    num_sample_pairs = int(accuracy_param * nx.number_of_nodes(component))
    shortest_paths = statistics.compute_shortest_path_distances_pairs(component, sample_pairs, num_sample_pairs)
    logger.info('computed shortest path lengths')
    if not plot:
        compute_statistics(shortest_paths)
    else:
        return shortest_paths
    print('complete code: \t', int(divmod(time.time() - start, 60)[0]), 'min:', int(divmod(time.time() - start, 60)[1]), 's')


def random_sources(filename, cc_type, accuracy_param, plot=False):
    """
    selects random sources to perform all-pair-shortest-paths
    :param filename: component edgelist filename
    :param cc_type: largest strongly/weakly connected component identifier (lscc / lwcc)
    :param accuracy_param: accuracy controlling param
    :param plot: True / False
    :return: shortest-path-lengths
    """
    start = time.time()

    component = None

    if cc_type == 'lscc':
        component = read_graph.as_directed(filename)
    elif cc_type == 'lwcc':
        component = read_graph.as_undirected(filename)

    num_sample_sources = int(accuracy_param * nx.number_of_nodes(component))
    sample_sources = random.sample(component.nodes(), num_sample_sources)
    shortest_paths = statistics.compute_shortest_path_distances_parallel(component, sources=sample_sources)
    logger.info('computed shortest path lengths')
    if not plot:
        compute_statistics(shortest_paths)
    else:
        return shortest_paths

    print('complete code: \t', int(divmod(time.time() - start, 60)[0]), 'min:', int(divmod(time.time() - start, 60)[1]), 's')


def approx_algo_fm(filename, cc_type, num_bitstrings=8, max_iter=12, len_bitstrings=64):
    """
    Flajolet-Martin algo (http://math.cmu.edu/~ctsourak/tkdd10.pdf)
    :param filename: component edgelist filename
    :param cc_type: largest strongly/weakly connected component identifier (lscc / lwcc)
    :param num_bitstrings: number of hash functions
    :param max_iter: number of iterations
    :param len_bitstrings: hash function range
    """
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
    distances = []

    for h in range(1, max_iter):
        changed = 0
        for node in nodes:
            for l in range(1, num_bitstrings):
                neighbors = nx.neighbors(component, node)
                bitmaps[l, h, node] = bitmaps[l, h - 1, node]
                for neighbor in neighbors:
                    bitmaps[l, h, node] |= bitmaps[l, h - 1, neighbor]
                    distances.append(h)

            for l in range(1, num_bitstrings):
                if not np.array_equal(bitmaps[l, h, node], bitmaps[l, h - 1, node]):
                    changed += 1

        neighborhood[h] = statistics.neighborhood_sum(bitmaps, nodes, num_bitstrings, h)
        if changed == 0:
            h_max = h
            break

    # logger.info('mean distance of the component: {}'.format(int(np.mean(distances))))
    # logger.info('median distance of the component: {}'.format(int(np.median(distances))))
    # logger.info('diameter of the component: {}'.format(h_max))
    # logger.info('effective diameter of the component: {}'.format(int(np.median(distances))))

    print('median distance of the component: {}'.format(int(np.median(neighborhood))))
    print('mean distance of the component: {}'.format(int(np.mean(neighborhood))))
    print('diameter of the component: {}'.format(h_max))

    smallest_h = -1
    perfect_match = False
    for h in range(max_iter):
        if neighborhood[h] == 0.9 * neighborhood[h_max]:
            perfect_match = True
            smallest_h = h
            break
        elif neighborhood[h] > 0.9 * neighborhood[h_max]:
            smallest_h = h
            break

    if perfect_match:
        # logger.info('effective diameter: ', smallest_h)
        print('effective diameter: ', smallest_h)
    else:
        # logger.info('effective diameter: ', statistics.interpolate(smallest_h, h_max, neighborhood))
        print('effective diameter: ', statistics.interpolate(smallest_h, h_max, neighborhood))


def plot_compare_approx_exact(means, medians, diameters, eff_diameters, stats):
    """
    compares the approx and exact statistics
    :param means: mean distances of various accuracy params
    :param medians: median distances of various accuracy params
    :param diameters: diameters of various accuracy params
    :param eff_diameters: effective diameters of various accuracy params
    :param stats: exact network statistics
    """
    plt.figure(figsize=(12, 6))
    plt.plot(accuracy_array, medians, label='Median distance', color='navy')
    plt.axhline(stats[0], linestyle='dashed', color='navy')

    plt.plot(accuracy_array, means, label='Mean distance', color='r')
    plt.axhline(stats[1], linestyle='dashed', color='r')

    plt.plot(accuracy_array, diameters, label='Diameter', color='orange')
    plt.axhline(stats[2], linestyle='dashed', color='orange')

    plt.plot(accuracy_array, eff_diameters, label='Effective Diameter', color='g')
    plt.axhline(stats[3], linestyle='dashed', color='g')

    plt.legend()
    plt.xlabel('accuracy')
    plt.ylabel('distance')
    plt.savefig('lscc_1_2.png')


def approx_analysis(filename, component_type, scheme, plot=False, network_index=1):
    """
    computes approximate network analysis
    :param filename: component edgelist filename
    :param component_type: largest strongly/weakly connected component identifier (lscc / lwcc)
    :param scheme: approximation scheme to choose (random-pairs, random-sources, F&M algo)
    :param plot: plot param which decides whether to plot compare with exact stats (True / False)
    :param network_index: network identifier (1, 2, 3, 4), we are only dealing with 1, 2 network
    """
    if scheme == 1:
        if not plot:
            random_pairs(filename, component_type, 0.1)
        else:
            global accuracy_array
            means = []
            medians = []
            diameters = []
            eff_diameters = []

            for accuracy in accuracy_array:
                path_lengths = random_pairs(filename, component_type, accuracy, plot)
                means.append(statistics.mean_distance(path_lengths))
                medians.append(statistics.median_distance(path_lengths))
                diameters.append(statistics.diameter(path_lengths))
                eff_diameters.append(statistics.effective_diameter(path_lengths))

            if network_index == 1:
                if component_type == 'lscc':
                    stats = [3, 2.876, 9, 4]
                else:
                    stats = [3, 3.247, 7, 4]
            else:
                if component_type == 'lscc':
                    stats = [4, 4.419, 16, 6]
                else:
                    stats = [4, 4.310, 15, 5]

            plot_compare_approx_exact(means, medians, diameters, eff_diameters, stats)

    elif scheme == 2:
        if not plot:
            random_sources(filename, component_type, 0.1)
        else:
            global accuracy_array
            means = []
            medians = []
            diameters = []
            eff_diameters = []

            for accuracy in accuracy_array:
                path_lengths = random_sources(filename, component_type, accuracy * 0.1, plot)
                means.append(statistics.mean_distance(path_lengths))
                medians.append(statistics.median_distance(path_lengths))
                diameters.append(statistics.diameter(path_lengths))
                eff_diameters.append(statistics.effective_diameter(path_lengths))

            if network_index == 1:
                if component_type == 'lscc':
                    stats = [3, 2.876, 9, 4]
                else:
                    stats = [3, 3.247, 7, 4]
            else:
                if component_type == 'lscc':
                    stats = [4, 4.419, 16, 6]
                else:
                    stats = [4, 4.310, 15, 5]

            plot_compare_approx_exact(means, medians, diameters, eff_diameters, stats)
    elif scheme == 3:
        approx_algo_fm(filename, component_type)
