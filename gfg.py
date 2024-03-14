from expr_lexer import ExprLexer
import pydot
import queue

class Vertex:
    def __init__(self, label, long_name, type):
        self.label = label
        self.long_name = long_name
        self.type = type
        self.is_call = False
        self.is_return = False
        self.is_entry = False
        self.is_exit = False
        self.is_scan = False
        self.incoming_edges = {}  # Map to store incoming edges (source vertex: token)
        self.outgoing_edges = {}  # Map to store outgoing edges (destination vertex: token)

    def __str__(self):
        return f"{self.long_name}"
    
    def __repr__(self):
        return f"{self.long_name}\ntype={self.type}\nis_call={self.is_call}\nis_return={self.is_return}\n"
    
    def __hash__(self):
        return hash(self.label)
    
    def __eq__(self, other):
        return isinstance(other, Vertex) and self.label == other.label

def add_edge(src, dest, label):
    src.outgoing_edges[dest.label] = label
    dest.incoming_edges[src.label] = label
    # print(f"\t\t\tcreating edge from {src.long_name} to {dest.long_name} with LABEL: {label}")

class GFG:
    def __init__(self, lexer):
        self.vertices = {}
        self.lexer = lexer
        self.lexer.build()
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

        # each vertex in the graph is assigned an integer label
        curr_label = 0

        # create the start and end vertex for the start producition first
        # ensures that the start vertex for the gfg is vertex 0
        # ensures that the end vertex for the gfg is vertex 1
        self.vertices[curr_label] = Vertex(curr_label, f"•{start_producition}", "start")
        self.vertices[curr_label + 1] = Vertex(curr_label + 1, f"{start_producition}•", "end")

        self.map_prod_name_to_start[start_producition] = curr_label
        self.map_start_to_end[curr_label] = curr_label + 1
        self.map_end_to_start[curr_label + 1] = curr_label
        curr_label += 2

        # create start and vertex for every other production
        for prod_name in productions:
            if prod_name is not start_producition:
                self.vertices[curr_label] = Vertex(curr_label, f"•{prod_name}", "start")
                self.graph.add_node(pydot.Node(f"•{prod_name}", shape="circle"))

                self.vertices[curr_label + 1] = Vertex(curr_label + 1, f"{prod_name}•", "end")
                self.graph.add_node(pydot.Node(f"{prod_name}•", shape="circle"))

                self.map_prod_name_to_start[prod_name] = curr_label
                self.map_start_to_end[curr_label] = curr_label + 1
                self.map_end_to_start[curr_label + 1] = curr_label
                curr_label += 2

        # for each production create necessary nodes
        for prod_name, prods in productions.items():
            for prod_rhs in prods:
                # print(f"\tCreating production: {prod_name}→{prod_rhs}")

                # previous vertex in the production
                prev_vertex = self.vertices[self.map_prod_name_to_start[prod_name]]
                # set if previous vertex as a call vertex
                end_vertex = None 
                edge_label = ""
                prefix_label = f"{prod_name}→"
                is_entry = True

                for term in prod_rhs:
                    new_vertex = Vertex(curr_label, f"[{prefix_label}•{term}]", "production")
                    new_vertex.is_entry = is_entry
                    is_entry = False
                    if prev_vertex.is_call:
                        new_vertex.is_return = True
                        self.map_call_to_return[prev_vertex.label] = new_vertex.label
                        self.map_return_to_call[new_vertex.label] = prev_vertex.label

                    self.graph.add_node(pydot.Node(f"[{prefix_label}•{term}]", shape="circle"))
                    self.vertices[curr_label] = new_vertex
                    curr_label += 1

                    # add edge from prev_node to new_vertex with appropriate label
                    src_vertex = end_vertex if prev_vertex.is_call else prev_vertex
                    add_edge(src_vertex, new_vertex, edge_label)
                    color = "red" if edge_label == "" else "black"
                    self.graph.add_edge(pydot.Edge(src_vertex.long_name, new_vertex.long_name, label=edge_label, color=color))

                    if term in self.lexer.tokens:
                        # print(f"\t\t{term} is a terminal")
                        new_vertex.is_scan = True
                        edge_label = f"{term}"
                        prev_vertex = new_vertex
                        end_vertex = None
                    elif term in productions:
                        # print(f"\t\t{term} is a production")
                        new_vertex.is_call = True
                        start = self.map_prod_name_to_start[term]
                        end = self.map_start_to_end[start]
                        # add edge from call vertex to start vertex of production
                        self.graph.add_edge(pydot.Edge(new_vertex.long_name, self.vertices[start].long_name, color="red"))
                        add_edge(new_vertex, self.vertices[start], "")
                        # set prev_vertex to prod• so next edge source is correct
                        prev_vertex = new_vertex
                        end_vertex = self.vertices[end]
                        edge_label = ""
                    else:
                        print(f"\t\TODO RAISE ERROR unrecognized term: {term}") 
                        return
                    
                    prefix_label = prefix_label + f"{term},"

                exit_vertex = Vertex(curr_label, f"[{prefix_label}•]", "production")
                exit_vertex.is_entry = is_entry
                exit_vertex.is_exit = True
                if prev_vertex.is_call:
                    exit_vertex.is_return = True
                    self.map_call_to_return[prev_vertex.label] = exit_vertex.label
                    self.map_return_to_call[exit_vertex.label] = prev_vertex.label

                self.vertices[curr_label] = exit_vertex
                curr_label += 1

                src_vertex = end_vertex if prev_vertex.is_call else prev_vertex
                if prev_vertex.is_call:
                    print("GOING FROM END TO EXIT", src_vertex.long_name, exit_vertex.long_name)
                add_edge(src_vertex, exit_vertex, edge_label)
                color = "red" if edge_label == "" else "black"
                self.graph.add_edge(pydot.Edge(src_vertex.long_name, exit_vertex.long_name, color=color, label=edge_label))

                # create edge from exit vertex to end vertex
                end_vertex = self.vertices[self.map_start_to_end[self.map_prod_name_to_start[prod_name]]]
                add_edge(exit_vertex, end_vertex, "")
                self.graph.add_edge(pydot.Edge(exit_vertex.long_name, end_vertex.long_name, color="red"))

        print(self.vertices)
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

            vertex = self.vertices[label]

            if vertex.type == "end":
                if label in sigma_end_to_call[tag]:
                    for call_label, call_tag in sigma_end_to_call[tag][label]:
                        return_label = self.map_call_to_return[call_label]
                        if (return_label, call_tag) not in curr_sigma_set:
                            print("putting end", (return_label, call_tag))
                            curr_sigma_set.add((return_label, call_tag))
                            label_queue.put((return_label, call_tag))
                else:
                    print("ERROR NO CALL FOR END, label", label, tag, sigma_end_to_call)
            elif vertex.type == "production" and vertex.is_call:
                # should only be one outgoing edge
                for dest_label, edge_label in vertex.outgoing_edges.items():
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
                for dest_label, edge_label in vertex.outgoing_edges.items():
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
                vertex_label, tag = element
                vertex = self.vertices[vertex_label]

                if vertex.is_scan:
                    for dest_label, edge_label in vertex.outgoing_edges.items():
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