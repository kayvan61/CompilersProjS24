from expr_lexer import ExprLexer
import pydot
import queue

class Node:
    def __init__(self, label, long_name, type):
        self.label = label
        self.long_name = long_name
        self.type = type
        self.is_call = False
        self.is_return = False
        self.is_entry = False
        self.is_exit = False
        self.is_scan = False
        self.incoming_edges = {}  # Map to store incoming edges (source node: token consumed)
        self.outgoing_edges = {}  # Map to store outgoing edges (destination node: token consumed)

    def __str__(self):
        return f"{self.long_name}"
    
    def __repr__(self):
        return f"{self.long_name}"
    
    def __hash__(self):
        return hash(self.label)
    
    def __eq__(self, other):
        return isinstance(other, Node) and self.label == other.label

def add_edge(src, dest, label):
    src.outgoing_edges[dest.label] = label
    dest.incoming_edges[src.label] = label
    # print(f"\t\t\tcreating edge from {src.long_name} to {dest.long_name} with LABEL: {label}")

class GFG:
    def __init__(self, lexer):
        self.nodes = {}
        # self.lexer.tokens defines the set of terminals
        self.lexer = lexer
        self.lexer.build()

        # maps a production name to the start node label for that production
        self.map_prod_name_to_start = {}
        self.map_start_to_end = {}
        self.map_end_to_start = {}
        self.map_call_to_return = {}
        self.map_return_to_call = {}
        # simply used for debugging to visualize the gfg
        self.graph = pydot.Dot("my_graph", graph_type="digraph", bgcolor="yellow")

    # productions is a map string : list(list(str))
    # value is list of possible productions for a given production name
    # each production is a list of token names or production names
    def build_gfg(self, productions, start_producition="S"):
        # production : <start node label, end node label>

        # each node in the graph is assigned an integer label
        curr_label = 0

        # create the start and end node for the start producition first
        # ensures that the start node for the gfg is node 0
        # ensures that the end node for the gfg is node 1
        self.nodes[curr_label] = Node(curr_label, f"•{start_producition}", "start")
        self.nodes[curr_label + 1] = Node(curr_label + 1, f"{start_producition}•", "end")

        self.map_prod_name_to_start[start_producition] = curr_label
        self.map_start_to_end[curr_label] = curr_label + 1
        self.map_end_to_start[curr_label + 1] = curr_label
        curr_label += 2

        # create start and end node for every other production
        for prod_name in productions:
            if prod_name is not start_producition:
                self.nodes[curr_label] = Node(curr_label, f"•{prod_name}", "start")
                self.graph.add_node(pydot.Node(f"•{prod_name}", shape="circle"))

                self.nodes[curr_label + 1] = Node(curr_label + 1, f"{prod_name}•", "end")
                self.graph.add_node(pydot.Node(f"{prod_name}•", shape="circle"))

                self.map_prod_name_to_start[prod_name] = curr_label
                self.map_start_to_end[curr_label] = curr_label + 1
                self.map_end_to_start[curr_label + 1] = curr_label
                curr_label += 2

        # for each production create necessary nodes
        for prod_name, prods in productions.items():
            for prod_rhs in prods:
                # print(f"\tCreating production: {prod_name}→{prod_rhs}")

                # previous node in the production
                prev_node = self.nodes[self.map_prod_name_to_start[prod_name]]
                # set if previous node as a call node
                end_node = None 
                edge_label = ""
                prefix_label = f"{prod_name}→"
                is_entry = True

                for term in prod_rhs:
                    new_node = Node(curr_label, f"[{prefix_label}•{term}]", "production")
                    new_node.is_entry = is_entry
                    is_entry = False
                    if prev_node.is_call:
                        new_node.is_return = True
                        self.map_call_to_return[prev_node.label] = new_node.label
                        self.map_return_to_call[new_node.label] = prev_node.label

                    self.graph.add_node(pydot.Node(f"[{prefix_label}•{term}]", shape="circle"))
                    self.nodes[curr_label] = new_node
                    curr_label += 1

                    # add edge from prev_node to new_node with appropriate label
                    src_node = end_node if prev_node.is_call else prev_node
                    add_edge(src_node, new_node, edge_label)
                    color = "red" if edge_label == "" else "black"
                    self.graph.add_edge(pydot.Edge(src_node.long_name, new_node.long_name, label=edge_label, color=color))

                    if term in self.lexer.tokens:
                        # print(f"\t\t{term} is a terminal")
                        new_node.is_scan = True
                        edge_label = f"{term}"
                        prev_node = new_node
                        end_node = None
                    elif term in productions:
                        # print(f"\t\t{term} is a production")
                        new_node.is_call = True
                        start = self.map_prod_name_to_start[term]
                        end = self.map_start_to_end[start]
                        # add edge from call node to start node of production
                        self.graph.add_edge(pydot.Edge(new_node.long_name, self.nodes[start].long_name, color="red"))
                        add_edge(new_node, self.nodes[start], "")
                        # set prev_node to prod• so next edge source is correct
                        prev_node = new_node
                        end_node = self.nodes[end]
                        edge_label = ""
                    else:
                        print(f"\t\TODO RAISE ERROR unrecognized term: {term}") 
                        return
                    
                    prefix_label = prefix_label + f"{term},"

                exit_node = Node(curr_label, f"[{prefix_label}•]", "production")
                exit_node.is_entry = is_entry
                exit_node.is_exit = True
                if prev_node.is_call:
                    exit_node.is_return = True
                    self.map_call_to_return[prev_node.label] = exit_node.label
                    self.map_return_to_call[exit_node.label] = prev_node.label

                self.nodes[curr_label] = exit_node
                curr_label += 1

                src_node = end_node if prev_node.is_call else prev_node
                if prev_node.is_call:
                    print("GOING FROM END TO EXIT", src_node.long_name, exit_node.long_name)
                add_edge(src_node, exit_node, edge_label)
                color = "red" if edge_label == "" else "black"
                self.graph.add_edge(pydot.Edge(src_node.long_name, exit_node.long_name, color=color, label=edge_label))

                # create edge from exit node to end node
                end_node = self.nodes[self.map_start_to_end[self.map_prod_name_to_start[prod_name]]]
                add_edge(exit_node, end_node, "")
                self.graph.add_edge(pydot.Edge(exit_node.long_name, end_node.long_name, color="red"))

        print(self.nodes)
        print(self.map_call_to_return)
        print(self.map_return_to_call)        
        

        # graph.write_png("output.png")
                
    
    def eclosuer(self, sigma_sets, sigma_end_to_call):
        label_queue = queue.Queue()

        sigma_num = len(sigma_sets) - 1
        curr_sigma_set = sigma_sets[sigma_num]

        for element in curr_sigma_set:
            print("Putting ", element)
            label_queue.put(element)

        while not label_queue.empty():
            label, tag = label_queue.get()
            print("label ", label, curr_sigma_set)

            node = self.nodes[label]

            if node.type == "end":
                if label in sigma_end_to_call[tag]:
                    for call_label, call_tag in sigma_end_to_call[tag][label]:
                        return_label = self.map_call_to_return[call_label]
                        if (return_label, call_tag) not in curr_sigma_set:
                            print("putting end", (return_label, call_tag))
                            curr_sigma_set.add((return_label, call_tag))
                            label_queue.put((return_label, call_tag))
                else:
                    print("ERROR NO CALL FOR END, label", label, tag, sigma_end_to_call)
            elif node.type == "production" and node.is_call:
                # should only be one outgoing edge
                for dest_label, edge_label in node.outgoing_edges.items():
                    if edge_label == "":
                        # map corresponding end node to call node for when reach end node later
                        end_label = self.map_start_to_end[dest_label]
                        if end_label in sigma_end_to_call[sigma_num] and (label, tag) not in sigma_end_to_call[sigma_num][end_label]:
                            sigma_end_to_call[sigma_num][end_label].append((label, tag))
                            print("\t\tadding ", (label, sigma_num))
                        elif end_label not in sigma_end_to_call[sigma_num]:
                            sigma_end_to_call[sigma_num][end_label] = [(label, tag)] 
                            print("\t\tadding ", (label, sigma_num))
                    
                        if (dest_label, sigma_num) not in curr_sigma_set:
                            # call node so set tag to current sigma number
                            print("putting is_call", (dest_label, sigma_num))
                            curr_sigma_set.add((dest_label, sigma_num))
                            label_queue.put((dest_label, sigma_num))

                                               
            else:
                # loop through outgoing edges with empty string label
                # add their dests to same sigma set with same tag
                for dest_label, edge_label in node.outgoing_edges.items():
                    if edge_label == "" and (dest_label, tag) not in curr_sigma_set:
                        # propagate the current tag
                        print("other putting", (dest_label, tag))
                        curr_sigma_set.add((dest_label, tag))
                        label_queue.put((dest_label, tag))
        
        print("curr sigma set", curr_sigma_set)
        print("curr sigma end to call", sigma_end_to_call[-1])
        print("------------------------")


    def recognize_string(self,data):
        self.lexer.input(data)

        sigma_sets = []
        sigma_sets.append(set([(0, 0)]))
        sigma_end_to_call = []
        sigma_end_to_call.append({})

        print("eclouser sigma 0")
        self.eclosuer(sigma_sets, sigma_end_to_call)

        while True:
            tok = self.lexer.token()
            if not tok:
                break

            # create next sigma set
            next_set = set()

            # loop through all elements in prev sigma set and see if there is an edge with label tok
            for element in sigma_sets[-1]:
                node_label, tag = element
                node = self.nodes[node_label]

                if node.is_scan:
                    for dest_label, edge_label in node.outgoing_edges.items():
                        if (edge_label == tok.type):
                            # propagate current tag to next 
                            next_set.add((dest_label, tag))

            sigma_sets.append(next_set)
            sigma_end_to_call.append({})
            print("before eclosuer sigma:", next_set)
            self.eclosuer(sigma_sets, sigma_end_to_call)
            

        # check if <S•, 0> is in last sigma set 
        return (1, 0) in sigma_sets[-1]

        

if __name__ == "__main__":
    test_gfg = GFG(ExprLexer())

    productions = {
        "S": [["E"]],
        "E": [["number"],
              ["E", "plus", "E"],
              ["lparen", "E", "plus", "E", "rparen"]
        ]
    }

    test_gfg.build_gfg(productions, "S")

    # test_gfg.graph.write_png("output.png")

    data = "7 + 8 + 9"
    print(f"is {data} in language: {test_gfg.recognize_string(data)}")


    data = "(7+9"
    print(f"is {data} in language: {test_gfg.recognize_string(data)}")


    print("done")