#include <boost/config.hpp>

#include <algorithm>
#include <vector>
#include <utility>
#include <iostream>

#include <boost/graph/visitors.hpp>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/breadth_first_search.hpp>
#include <boost/property_map/property_map.hpp>
#include <boost/graph/graph_utility.hpp>
#include <fstream>
#include <cmath>

template<class ParentDecorator>
struct print_parent {
    print_parent(const ParentDecorator &p_) : p(p_) {}

    template<class Vertex>
    void operator()(const Vertex &v) const {
        std::cout << "parent[" << v << "] = " << p[v] << std::endl;
    }

    ParentDecorator p;
};


template<class NewGraph, class Tag>
struct graph_copier
        : public boost::base_visitor<graph_copier<NewGraph, Tag> > {
    typedef Tag event_filter;

    graph_copier(NewGraph &graph) : new_g(graph) {}

    template<class Edge, class Graph>
    void operator()(Edge e, Graph &g) {
        boost::add_edge(boost::source(e, g), boost::target(e, g), new_g);
    }

private:
    NewGraph &new_g;
};

template<class NewGraph, class Tag>
inline graph_copier<NewGraph, Tag>
copy_graph(NewGraph &g, Tag) {
    return graph_copier<NewGraph, Tag>(g);
}

int diameter = INT_MIN;

std::vector<int> distances;

int main(int, char *[]) {
    typedef boost::adjacency_list<
            boost::mapS, boost::vecS, boost::directedS,
            boost::property<boost::vertex_color_t, boost::default_color_type,
                    boost::property<boost::vertex_degree_t, int,
                            boost::property<boost::vertex_in_degree_t, int,
                                    boost::property<boost::vertex_out_degree_t, int> > > >
    > Graph;

    // read the strongest component into memory
    std::ifstream infile("/Users/kaushiksurikuchi/Downloads/lscc_1.txt");
    Graph G;
    unsigned long node_u = 0, node_v = 0;
    while (infile >> node_u >> node_v) {
        boost::add_edge(node_u, node_v, G);
    }

    unsigned long num_v = boost::num_vertices(G), num_e = boost::num_edges(G);
    std::cout << "number of vertices and edges in the component: " << num_v << " " << num_e << "\n";

    distances.clear();
    typedef Graph::vertex_descriptor Vertex;
    std::pair<boost::graph_traits<Graph>::vertex_iterator, boost::graph_traits<Graph>::vertex_iterator> verticesIteratorRange = boost::vertices(
            G);

    for (boost::graph_traits<Graph>::vertex_iterator vertexIterator = verticesIteratorRange.first;
         vertexIterator != verticesIteratorRange.second; ++vertexIterator) {
        Graph G_copy(num_v);
        // Array to store predecessor (parent) of each vertex. This will be
        // used as a Decorator (actually, its iterator will be).
        std::vector<Vertex> p(num_v);
        // VC++ version of std::vector has no ::pointer, so
        // I use ::value_type* instead.
        typedef std::vector<Vertex>::value_type *Piter;

        // Array to store distances from the source to each vertex .  We use
        // a built-in array here just for variety. This will also be used as
        // a Decorator.
        boost::graph_traits<Graph>::vertices_size_type d[num_v];
        std::fill_n(d, num_v, 0);

        // The source vertex
        Vertex s = *(vertexIterator);
        p[s] = s;
        boost::breadth_first_search
                (G, s,
                 boost::visitor(boost::make_bfs_visitor
                                        (std::make_pair(boost::record_distances(d, boost::on_tree_edge()),
                                                        std::make_pair
                                                                (boost::record_predecessors(&p[0],
                                                                                            boost::on_tree_edge()),
                                                                 copy_graph(G_copy, boost::on_examine_edge()))))));

//    boost::print_graph(G);
//    boost::print_graph(G_copy);

        if (num_v < 11) {
            std::cout << "distances: ";
#ifdef BOOST_OLD_STREAM_ITERATORS
            std::copy(d, d + 5, std::ostream_iterator<int, char>(std::cout, " "));
#else
            std::copy(d, d + 5, std::ostream_iterator<int>(std::cout, " "));
#endif
            std::cout << std::endl;

            std::for_each(boost::vertices(G).first, boost::vertices(G).second,
                          print_parent<Piter>(&p[0]));
        } else {
            // store distances from current vertex to other vertices
            for (int pos = 0; pos < num_v; ++pos) {
                if ((int) d[pos] > 0)
                    distances.push_back((int) d[pos]);
                diameter = std::max(diameter, (int) d[pos]);
            }
        }
    }

    std::cout << "diameter: " << diameter << "\n";
    std::cout << "mean distance : "
              << (double) std::accumulate(distances.begin(), distances.end(), 0) / (double) distances.size()
              << "\n";
    std::sort(distances.begin(), distances.end());
    double median = 0;
    if (distances.size() & 1) {
        // odd case
        median = distances[(distances.size() - 1) / 2];
    } else {
        // even case
        median += distances[(distances.size() - 1) / 2];
        median += distances[(distances.size()) / 2];
        median /= 2.0;
    }

    std::cout << "median distance : " << median << "\n";

    // (effective diameter)
    int n = int(round(0.9 * distances.size() + 0.5));
    std::cout << "effective diameter: " << distances[n - 1] << "\n";

    return 0;
}