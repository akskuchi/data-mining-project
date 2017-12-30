#include <boost/graph/adjacency_list.hpp>
#include <iostream>
#include <fstream>
#include <vector>
#include <iomanip>
#include <boost/graph/strong_components.hpp>
#include <boost/graph/graph_utility.hpp>
#include <boost/graph/floyd_warshall_shortest.hpp>
#include <algorithm>
#include <map>
#include <set>
#include <boost/graph/filtered_graph.hpp>
#include <boost/graph/johnson_all_pairs_shortest.hpp>
#include <boost/make_shared.hpp>
#include <boost/graph/filtered_graph.hpp>
#include <boost/graph/graph_utility.hpp>
#include <boost/range/iterator_range.hpp>

using namespace std;

set<unsigned long> component_vertices;
map<string, unsigned long> vertex_mapping1;
map<unsigned long, string> vertex_mapping2;
set<pair<int, int>> lscc_edge_list, lscc_edge_list_final;

// Create a typedef for the Graph type
typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::directedS, boost::property<boost::vertex_index_t, int>, boost::property<boost::edge_index_t, int>> Graph;

// typedef subgraph < Graph > SubGraph;
typedef typename boost::graph_traits<Graph>::vertex_descriptor Vertex;
typedef typename boost::graph_traits<Graph>::edge_descriptor Edge;
typedef boost::graph_traits<Graph> GraphTraits;

// Iterators
typedef boost::graph_traits<Graph>::vertex_iterator vertex_iter;
typedef boost::graph_traits<Graph>::edge_iterator edge_iter;
typedef boost::property_map<Graph, boost::vertex_index_t>::type VertexIndexMap;
typedef boost::property_map<Graph, boost::edge_index_t>::type EdgeIndexMap;
typedef boost::shared_ptr<std::vector<unsigned long>> vertex_component_map;

struct EdgeInComponent {
    vertex_component_map mapping_;
    unsigned long which_;
    Graph const &master_;

    EdgeInComponent(vertex_component_map m, unsigned long which, Graph const &master)
            : mapping_(m), which_(which), master_(master) {}

    template<typename Edge>
    bool operator()(Edge const &e) const {
        return mapping_->at(source(e, master_)) == which_
               || mapping_->at(target(e, master_)) == which_;
    }
};

struct VertexInComponent {
    vertex_component_map mapping_;
    unsigned long which_;

    VertexInComponent(vertex_component_map m, unsigned long which)
            : mapping_(m), which_(which) {}

    template<typename Vertex>
    bool operator()(Vertex const &v) const {
        return mapping_->at(v) == which_;
    }
};

struct AnyVertex {
    template<typename Vertex>
    bool operator()(Vertex const &) const { return true; }
};

typedef boost::filtered_graph<Graph, EdgeInComponent, VertexInComponent> ComponentGraph;

Graph g;
int lscc_label = -1;

vector<ComponentGraph> lscc_subgraph(Graph const &g) {
    unsigned long num_v = num_vertices(g);
    vertex_component_map mapping = boost::make_shared<std::vector<unsigned long>>(num_v);

    size_t num = strong_components(g, mapping->data());
    cout << "total strongly connected components 2: " << num << "\n";


    vector<ComponentGraph> component_graphs;

    component_graphs.emplace_back(g, EdgeInComponent(mapping, static_cast<unsigned long>(lscc_label), g),
                                  VertexInComponent(mapping,
                                                    static_cast<unsigned long>(lscc_label)));

    return component_graphs;
}

int main() {
    // read the di-graph into memory
    ifstream infile("/Users/kaushiksurikuchi/CLionProjects/data-mining-cpp/soc-pokec-relationships.txt");

    string _node_u, _node_v;
    unsigned long node_u = 0, node_v = 0, node = 0;
    while (infile >> _node_u >> _node_v) {
        if (vertex_mapping1.find(_node_u) != vertex_mapping1.end()) {
            node_u = vertex_mapping1[_node_u];
        } else {
            vertex_mapping1[_node_u] = node++;
            node_u = vertex_mapping1[_node_u];
            vertex_mapping2[node_u] = _node_u;
        }

        if (vertex_mapping1.find(_node_v) != vertex_mapping1.end()) {
            node_v = vertex_mapping1[_node_v];
        } else {
            vertex_mapping1[_node_v] = node++;
            node_v = vertex_mapping1[_node_v];
            vertex_mapping2[node_v] = _node_v;
        }

        boost::add_edge(node_u, node_v, g);
    }

    unsigned long num_of_vertices = boost::num_vertices(g), num_of_edges = boost::num_edges(g);;
    cout << "actual graph has " << num_of_vertices << " vertices and " << num_of_edges << " edges\n";

    // compute strongly connected components of the graph
    typedef boost::graph_traits<boost::adjacency_list<boost::vecS, boost::vecS, boost::directedS> >::vertex_descriptor Vertex;
    vector<int> component(num_of_vertices), discover_time(num_of_vertices);
    vector<boost::default_color_type> color(num_of_vertices);
    vector<Vertex> root(num_of_vertices);
    int num_of_scc = strong_components(g, boost::make_iterator_property_map(component.begin(),
                                                                            get(boost::vertex_index, g)),
                                       boost::root_map(boost::make_iterator_property_map(root.begin(),
                                                                                         get(boost::vertex_index,
                                                                                             g))).color_map(
                                               make_iterator_property_map(color.begin(), get(boost::vertex_index,
                                                                                             g))).discover_time_map(
                                               boost::make_iterator_property_map(discover_time.begin(),
                                                                                 get(boost::vertex_index, g))));

    cout << "total strongly connected components 1: " << num_of_scc << endl;

    map<int, long> component_frequency;
    for (int label : component) {
        component_frequency[label]++;
    }

    // identify the largest strongly connected component
    long lscc_num_nodes = 0;
    for (int scc_label = 0; scc_label < num_of_scc; ++scc_label) {
        long scc_num_nodes = component_frequency[scc_label];
        if (scc_num_nodes >= lscc_num_nodes) {
            lscc_label = scc_label;
            lscc_num_nodes = scc_num_nodes;
        }
    }
    cout << "largest strongly connected component: " << lscc_label << "\n";

    for (auto const &_component : lscc_subgraph(g)) {
        lscc_edge_list.clear();
        for (auto e :  boost::make_iterator_range(edges(_component)))
            lscc_edge_list.insert(std::make_pair(source(e, _component), target(e, _component)));

        if (lscc_edge_list_final.empty() or lscc_edge_list.size() > lscc_edge_list_final.size()) {
            lscc_edge_list_final = lscc_edge_list;
        }
    }
    cout << "number of edges in lscc: " << lscc_edge_list_final.size() << "\n";


    // writing lscc to file as edge-list
    ofstream lwcc_stream;
    lwcc_stream.open("/Users/kaushiksurikuchi/Downloads/lscc_4.txt");
    auto it = lscc_edge_list_final.begin();
    while (it != lscc_edge_list_final.end()) {
        lwcc_stream << (*it).first << "\t" << (*it).second << "\n";
        it++;
    }
    lwcc_stream.close();
    cout << "extracting lscc done!\n";

    return 0;
}