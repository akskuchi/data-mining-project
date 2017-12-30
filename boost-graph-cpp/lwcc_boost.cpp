#include <iostream>
#include <fstream>
#include <string>
#include <cstring>
#include <set>
#include <map>
#include <boost/graph/adjacency_list.hpp>
#include <boost/graph/connected_components.hpp>
#include <boost/make_shared.hpp>
#include <boost/graph/filtered_graph.hpp>
#include <boost/graph/graph_utility.hpp>
#include <boost/range/iterator_range.hpp>

using namespace boost;

std::set<unsigned long> component_vertices;
std::map<std::string, unsigned long> vertex_mapping1;
std::map<unsigned long, std::string> vertex_mapping2;
std::set<std::pair<int, int>> lwcc_edge_list, lwcc_edge_list_final;
int visited[10000000] = {};

// Create a typedef for the Graph type
typedef adjacency_list<vecS, vecS, undirectedS, property<vertex_index_t, int>, property<edge_index_t, int>> Graph;

// typedef subgraph < Graph > SubGraph;
typedef typename graph_traits<Graph>::vertex_descriptor Vertex;
typedef typename graph_traits<Graph>::edge_descriptor Edge;
typedef graph_traits<Graph> GraphTraits;

// Iterators
typedef graph_traits<Graph>::vertex_iterator vertex_iter;
typedef graph_traits<Graph>::edge_iterator edge_iter;
typedef property_map<Graph, vertex_index_t>::type VertexIndexMap;
typedef property_map<Graph, edge_index_t>::type EdgeIndexMap;

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

typedef filtered_graph<Graph, EdgeInComponent, VertexInComponent> ComponentGraph;

std::vector<ComponentGraph> lwcc_subgraph(Graph const &g) {
    vertex_component_map mapping = boost::make_shared<std::vector<unsigned long>>(num_vertices(g));
    size_t num = boost::connected_components(g, mapping->data());
    std::cout << "total weakly connected components: " << num << "\n";


    std::vector<ComponentGraph> component_graphs;

    for (size_t i = 0; i < num; i++)
        component_graphs.push_back(ComponentGraph(g, EdgeInComponent(mapping, i, g), VertexInComponent(mapping, i)));

    return component_graphs;
}

int main() {
    // read the un-di-graph into memory
    std::ifstream infile("/Users/kaushiksurikuchi/CLionProjects/data-mining-cpp/wiki-Vote.txt");
    Graph g;

    std::string _node_u, _node_v;
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
    std::cout << "actual graph has " << num_of_vertices << " vertices and " << num_of_edges << " edges\n";

    // compute weakly connected components of the graph

    for (auto const &component : lwcc_subgraph(g)) {
        lwcc_edge_list.clear();
        for (auto e :  make_iterator_range(edges(component)))
            lwcc_edge_list.insert(std::make_pair(source(e, component), target(e, component)));

        if (lwcc_edge_list_final.empty() or lwcc_edge_list.size() > lwcc_edge_list_final.size()) {
            lwcc_edge_list_final = lwcc_edge_list;
        }
    }

    std::cout << "number of edges in lwcc: " << lwcc_edge_list_final.size() << "\n";

    // writing lwcc to file as edge-list
    std::ofstream lwcc_stream;
    lwcc_stream.open("/Users/kaushiksurikuchi/Downloads/lwcc_1.txt");
    auto it = lwcc_edge_list_final.begin();
    while (it != lwcc_edge_list_final.end()) {
        lwcc_stream << (*it).first << "\t" << (*it).second << "\n";
        it++;
    }
    lwcc_stream.close();

    return 0;

}