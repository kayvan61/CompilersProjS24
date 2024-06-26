import pydot

class SppfNode_Old:
    def __init__(self, node_def, long_name, type):
        self.label = node_def[0]
        self.start = node_def[1]
        self.end = node_def[2]
        self.long_name = long_name
        self.rebuilt = False
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
        return isinstance(other, SppfNode_Old) and self.label == other.label

class Sppf_Old:

    def __init__(self, use_dot):
        self.use_dot = use_dot
        self.nodes = {}
        if self.use_dot:
            self.graph = pydot.Dot("sppf_graph", graph_type="digraph", bgcolor="white")
        
    def rebuild_with_root(self, root_node):
        if self.use_dot:
            self.graph = pydot.Dot("sppf_graph", graph_type="digraph", bgcolor="white")
        root = self.nodes[root_node]
        self.rebuild_node(root)
    
    def rebuild_node(self, node):
        if node.rebuilt:
            return

        node.rebuilt = True
        if self.use_dot:
            if node.type == "packed":
                self.graph.add_node(pydot.Node(node.get_pydot_label(), label="", shape="circle"))
            else:
                self.graph.add_node(pydot.Node(node.get_pydot_label(), shape="circle"))
            
        for dst,_ in node.outgoing_edges.items():
            self.rebuild_node(self.nodes[dst])
            if self.use_dot:
                self.graph.add_edge(pydot.Edge(node.get_pydot_label(), self.nodes[dst].get_pydot_label()))
            

    def add_node(self, node_def, long_name, type):
        if node_def not in self.nodes:
            node = SppfNode_Old(node_def, long_name, type)
            self.nodes[node_def] = node
            if self.use_dot:
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
            if self.use_dot:
                self.graph.add_edge(pydot.Edge(src_node.get_pydot_label(), dest_node.get_pydot_label()))
            # print(f"\t\t\tcreating edge from {src.long_name} to {dest.long_name} with LABEL: {label}")

    def add_family(self, parent, child1, child2):
        packed_node_def = (f"{child1},{child2}", child1, child2)

        self.add_node(packed_node_def, "", "packed")

        self.add_edge(parent, packed_node_def)
        self.add_edge(packed_node_def, child1)
        self.add_edge(packed_node_def, child2)






