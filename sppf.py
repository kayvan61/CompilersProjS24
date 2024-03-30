import pydot

class SppfNode:
    def __init__(self, node_def, long_name, type):
        self.label = node_def[0]
        self.start = node_def[1]
        self.end = node_def[2]
        self.long_name = long_name
        self.type = type # symbol, packed, intermediate
        self.incoming_edges = {}  # Map to store incoming edges (source node: token consumed)
        self.outgoing_edges = {}  # Map to store outgoing edges (destination node: token consumed)

    def get_pydot_label(self):
        if self.type == "packed":
            return self.label
        else:
            return f"({self.long_name}, {self.start}, {self.end})"

    def __str__(self):
        return f"{self.long_name}"
    
    def __repr__(self):
        return f"{self.long_name}"
    
    def __hash__(self):
        return hash(self.label)
    
    def __eq__(self, other):
        return isinstance(other, SppfNode) and self.label == other.label

class Sppf:

    def __init__(self):
        self.nodes = {}
        self.graph = pydot.Dot("sppf_graph", graph_type="digraph", bgcolor="yellow")

    def add_node(self, node_def, long_name, type):
        if node_def not in self.nodes:
            node = SppfNode(node_def, long_name, type)
            self.nodes[node_def] = node
            if type == "packed":
                self.graph.add_node(pydot.Node(node.get_pydot_label(), label="", shape="circle"))
            else :
                self.graph.add_node(pydot.Node(node.get_pydot_label(), shape="circle"))
        else:
            print(f"Node: {node_def} already exists in graph")

    def add_edge(self, src, dest):
        src_node = self.nodes[src]
        dest_node = self.nodes[dest]

        if dest not in src_node.outgoing_edges and src not in dest_node.incoming_edges:
            src_node.outgoing_edges[dest] = ""
            dest_node.incoming_edges[src] = ""

            # optional edges in pydot for gfs visualization, scan edges are black, 
            # epsilon edges are red
            self.graph.add_edge(pydot.Edge(src_node.get_pydot_label(), dest_node.get_pydot_label()))
            # print(f"\t\t\tcreating edge from {src.long_name} to {dest.long_name} with LABEL: {label}")

    def add_family(self, parent, child1, child2):
        packed_node_def = (f"{child1},{child2}", child1, child2)

        self.add_node(packed_node_def, "", "packed")

        self.add_edge(parent, packed_node_def)
        self.add_edge(packed_node_def, child1)
        self.add_edge(packed_node_def, child2)







