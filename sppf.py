import pydot

# class SppfNode:
#     def __init__(self, node_def, long_name, type, use_pydot):
#         self.label = node_def[0]
#         self.start = node_def[1]
#         self.end = node_def[2]
#         if use_pydot:
#             self.long_name = long_name
#             self.type = type # symbol, packed, intermediate
#         # self.incoming_edges = {}  # Map to store incoming edges (source node: token consumed)
#         self.outgoing_edges = {}  # Map to store outgoing edges (destination node: token consumed)

#     def get_pydot_label(self):
#         if self.type == "packed":
#             return self.label
#         else:
#             return f"({self.long_name}, {self.start}, {self.end})"

#     def __str__(self):
#         return f"{self.long_name}"
    
#     def __repr__(self):
#         return f"{self.long_name}"
    
#     def __hash__(self):
#         return hash(self.label, self.start, self.end)
    
#     def __eq__(self, other):
#         return isinstance(other, SppfNode) and self.label == other.label and self.start == other.start and self.end == other.end


class Sppf:

    def __init__(self, use_pydot=True):
        self.nodes = set()
        self.edges = {} # maps source to dest
        self.use_pydot = use_pydot
        self.packed_id = -1
        if self.use_pydot:
            self.graph = pydot.Dot("sppf_graph", graph_type="digraph", bgcolor="yellow")
            self.map_node_to_label = {}

    def add_node(self, node_def, long_name, type):
        if node_def not in self.nodes:
            # node = SppfNode(node_def, long_name, type, self.use_pydot)
            self.nodes.add(node_def)
            if self.use_pydot:
                if type == "packed":
                    self.map_node_to_label[node_def] = node_def

                    self.graph.add_node(pydot.Node(node_def, label="", shape="circle"))
                else :
                    label = f"{long_name}, {node_def[1]}, {node_def[2]}"
                    self.map_node_to_label[node_def] = label
                    
                    self.graph.add_node(pydot.Node(label, shape="circle"))
                    
        else:
            pass
            # print(f"Node: {node_def} already exists in graph")

    def add_edge(self, src, dest):
        # src_node = self.nodes[src]
        # dest_node = self.nodes[dest]

        src_children = None
        add_set = False

        if src not in self.edges:
            src_children = set()
            add_set = True
        else:
            src_children = self.edges[src]

        if dest not in src_children:
            src_children.add(dest)

        if add_set:
            self.edges[src] = src_children

        # src_node.outgoing_edges[dest] = ""
        # dest_node.incoming_edges[src] = ""

        # optional edges in pydot for gfs visualization, scan edges are black, 
        # epsilon edges are red
        if self.use_pydot:
            self.graph.add_edge(pydot.Edge(self.map_node_to_label[src], self.map_node_to_label[dest]))
        # print(f"\t\t\tcreating edge from {src.long_name} to {dest.long_name} with LABEL: {label}")

    def add_family(self, parent, child1, child2):
        packed_node_def = self.packed_id
        self.packed_id -= 1

        self.add_node(packed_node_def, "", "packed")

        self.add_edge(parent, packed_node_def)
        self.add_edge(packed_node_def, child1)
        self.add_edge(packed_node_def, child2)







