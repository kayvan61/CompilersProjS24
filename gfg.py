from expr_lexer import ExprLexer
from ab_lexer import ABLexer
from sppf import Sppf
import pydot
import queue
import random
from collections import deque

# models a single node if the grammar flow graph
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

# models a grammar flow graph
class GFG:
    def __init__(self, lexer):
        self.nodes = {}
        # self.lexer.tokens defines the set of terminals
        self.lexer = lexer
        self.lexer.build()

        # maps a production name to the start node label for that production
        self.map_prod_name_to_start = {}
        self.map_start_to_prod_name = {}
        self.map_start_to_end = {}
        self.map_end_to_start = {}
        self.map_call_to_return = {}
        self.map_return_to_call = {}
        # simply used for debugging to visualize the gfg
        self.graph = pydot.Dot("my_graph", graph_type="digraph", bgcolor="yellow")

    def add_node(self, label, long_name, type):
        self.nodes[label] = Node(label, long_name, type)
        # add node to pydot graph for visualization/debugging only
        self.graph.add_node(pydot.Node(long_name, shape="circle"))
        return self.nodes[label]
    
    # create the start and end nodes for a given production, curr_label is the next available
    # int label that can be used to represent a node
    def create_start_end_nodes_for_prod(self, prod_name, curr_label):
        self.add_node(curr_label, f"•{prod_name}", "start")
        self.add_node(curr_label + 1, f"{prod_name}•", "end")

        # update maps to keep track of relationship between production names and nodes
        self.map_prod_name_to_start[prod_name] = curr_label
        self.map_start_to_prod_name[curr_label] = prod_name

        self.map_start_to_end[curr_label] = curr_label + 1
        self.map_end_to_start[curr_label + 1] = curr_label
        return curr_label + 2

    # adds a direction edge from src to dest where the label is the terminal that must be consumed
    # to move from src to dest in the gfg (often the empty string)
    def add_edge(self, src, dest, label):
        src.outgoing_edges[dest.label] = label
        dest.incoming_edges[src.label] = label

        # optional edges in pydot for gfs visualization, scan edges are black, 
        # epsilon edges are red
        color = "red" if label == "" else "black"
        self.graph.add_edge(pydot.Edge(src.long_name, dest.long_name, label=label, color=color))
        # print(f"\t\t\tcreating edge from {src.long_name} to {dest.long_name} with LABEL: {label}")

    # productions is a map string : list(list(str))
    # value is list of possible productions for a given production name
    # each production is a list of token names or production names
    def build_gfg(self, productions, start_producition="S"):
        # each node in the graph is assigned an integer label
        curr_label = 0

        # create the start and end node for the start producition first
        # ensures that the start node for the gfg is node 0
        # ensures that the end node for the gfg is node 1
        curr_label = self.create_start_end_nodes_for_prod(start_producition, curr_label)

        # create start and end node for every other production
        for prod_name in productions:
            if prod_name is not start_producition:
                curr_label = self.create_start_end_nodes_for_prod(prod_name, curr_label)

        # for each production create necessary nodes
        for prod_name, prods in productions.items():
            for prod_rhs in prods:
                # print(f"\tCreating production: {prod_name}→{prod_rhs}")

                # previous node in the production (initially the start node of that production)
                prev_node = self.nodes[self.map_prod_name_to_start[prod_name]]
                # set if previous node is a call node
                end_node = None 
                edge_label = ""
                prefix_label = f"{prod_name}→"
                is_entry = True

                for term in prod_rhs:
                    new_node = self.add_node(curr_label, f"[{prefix_label}•{term}]", "production")
                    curr_label += 1
                    new_node.is_entry = is_entry
                    is_entry = False
                    if prev_node.is_call:
                        # if previous node is a call node to a production then this node is 
                        # the return node from the production
                        # Ex: prev_node: A→a•B, then new_node is A→aB•
                        new_node.is_return = True
                        self.map_call_to_return[prev_node.label] = new_node.label
                        self.map_return_to_call[new_node.label] = prev_node.label

                    # if previous node is a call node, Ex: prev_node: A→a•B then incoming edge to
                    # new node should be from the end node of the called production, in this case B•
                    # this node was stored in end_node during previous iteration
                    # otherwise if previous node is not a call node, then just set incoming edge
                    # from prev_node with the set edge label
                    src_node = end_node if prev_node.is_call else prev_node
                    self.add_edge(src_node, new_node, edge_label)

                    if term in self.lexer.tokens:
                        # term is a terminal, next edge should be a scan edge
                        new_node.is_scan = True
                        edge_label = f"{term}"
                        end_node = None
                    elif term in productions:
                        # term is a production, thus new_node is a call node
                        new_node.is_call = True
                        # get start and end node of called production
                        called_prod_start = self.map_prod_name_to_start[term]
                        called_prod_end = self.map_start_to_end[called_prod_start]
                        # add edge from call node to start node of production
                        self.add_edge(new_node, self.nodes[called_prod_start], "")
                        # set end_node to prod• so next edge source is correct
                        end_node = self.nodes[called_prod_end]
                        edge_label = ""
                    else:
                        print(f"\t\TODO RAISE ERROR unrecognized term: {term}") 
                        return
                    
                    # update prev_node and prefix_label
                    prev_node = new_node
                    prefix_label = prefix_label + f"{term},"

                # reached exit node for current production
                exit_node = self.add_node(curr_label, f"[{prefix_label}•]", "production")
                curr_label += 1

                exit_node.is_entry = is_entry # may also be entry node if production is A->epsilon
                exit_node.is_exit = True
                if prev_node.is_call:
                    exit_node.is_return = True
                    self.map_call_to_return[prev_node.label] = exit_node.label
                    self.map_return_to_call[exit_node.label] = prev_node.label

                
                src_node = end_node if prev_node.is_call else prev_node
                self.add_edge(src_node, exit_node, edge_label)

                # create edge from exit node to end node (Ex: A→aB• goes to A•)
                end_node = self.nodes[self.map_start_to_end[self.map_prod_name_to_start[prod_name]]]
                self.add_edge(exit_node, end_node, "")

        # print(self.nodes)
        # print(self.map_call_to_return)
        # print(self.map_return_to_call)        
                        
    
    # implements early recognizer inference rules on page 12 of gfg paper except for scan
    # inference rule which transitions between sigma sets
    def eclosuer(self, sigma_sets, call_sigma_sets, sigma_end_to_call, sigma_end_to_exit, sigma_return_to_end):
        label_queue = queue.Queue()

        # last sigma_set is set to expand
        sigma_num = len(sigma_sets) - 1
        curr_sigma_set = sigma_sets[sigma_num]

        # add all nodes initially in sigma set to queue to explore from
        for element in curr_sigma_set:
            label_queue.put(element)

        while not label_queue.empty():
            label, tag = label_queue.get()
            # print("label ", label, curr_sigma_set)

            node = self.nodes[label]

            if node.type == "end":
                # implements end inference rule
                # may not be any call node for production if the current end node is the end node
                # of the start production
                if label in sigma_end_to_call[tag]:
                    # get call nodes that called the production in the tag sigma set
                    for call_label, call_tag in sigma_end_to_call[tag][label]:
                        # get return node associated with the call node
                        return_label = self.map_call_to_return[call_label]
                        # if return node is not already in the sigma set, add it to the sigma
                        # set and the work queue
                        # tag of return node is set to tag of call node 
                        return_elem = (return_label, call_tag)

                        if return_elem in sigma_return_to_end[sigma_num]:
                            sigma_return_to_end[sigma_num][return_elem].add((label, tag))
                        else:
                            sigma_return_to_end[sigma_num][return_elem] = {(label, tag)}


                        if return_elem not in curr_sigma_set:
                            curr_sigma_set.add(return_elem)
                            label_queue.put(return_elem)

                            if self.nodes[return_elem[0]].is_call:
                                call_sigma_sets[sigma_num].add(return_elem)
            elif node.is_call:
                # implements the call inference rule
                # guaranteed to only be one outgoing edge with empty string edge label
                for dest_label, edge_label in node.outgoing_edges.items():
                        # map corresponding end node to call node for when reach end node later
                        end_label = self.map_start_to_end[dest_label]

                        # add end_label -> (label, tag) to current sigma_end_to_call_map if it
                        # not already in the map
                        if end_label in sigma_end_to_call[sigma_num] and (label, tag) not in sigma_end_to_call[sigma_num][end_label]:
                            # handles case where list of call nodes for end_label already exists
                            # since there may be multiple call nodes for the same production in the
                            # sigma set
                            sigma_end_to_call[sigma_num][end_label].add((label, tag))
                        elif end_label not in sigma_end_to_call[sigma_num]:
                            # hanldes case where this is the first call node for the production
                            sigma_end_to_call[sigma_num][end_label] = {(label, tag)}
                    
                        if (dest_label, sigma_num) not in curr_sigma_set:
                            # adding start node so set tag to current sigma number
                            curr_sigma_set.add((dest_label, sigma_num))
                            label_queue.put((dest_label, sigma_num))                                             
            else:                
                # implements start and exit inference rules as these just follow empty string edges
                # loop through outgoing edges with empty string label
                # add their dests to same sigma set with same tag
                for dest_label, edge_label in node.outgoing_edges.items():
                    if edge_label == "" and (dest_label, tag) not in curr_sigma_set:
                        # propagate the current tag
                        curr_sigma_set.add((dest_label, tag))
                        label_queue.put((dest_label, tag))

                        if self.nodes[dest_label].is_call:
                            call_sigma_sets[sigma_num].add((dest_label, tag))

                    if node.is_exit:
                        if (dest_label, tag) in sigma_end_to_exit[sigma_num]:
                            sigma_end_to_exit[sigma_num][(dest_label, tag)].add(label)
                        else:
                            sigma_end_to_exit[sigma_num][(dest_label, tag)] = {label}
        
        # print("curr sigma set", curr_sigma_set)
        # print("curr sigma end to call", sigma_end_to_call[-1])
        # print("------------------------")

    # returns True if string is language of grammar of gfg, False otherwise
    def recognize_string(self,data):
        self.lexer.input(data)

        sigma_sets = []
        call_sigma_sets = [set()]
        # zeroth sigma set initially contains <•S, 0>
        # implements the init inference rule
        sigma_sets.append(set([(0, 0)]))
        # maps an end node of production to all call nodes that invoked that production
        # in its corresponding sigma set, used from going from an end node to a return node
        # in the eclosuer function
        sigma_end_to_call = []
        sigma_end_to_call.append({})

        sigma_end_to_exit = []
        sigma_end_to_exit.append({})

        sigma_return_to_end = []
        sigma_return_to_end.append({})

        # find all nodes from S• that can be reached by taking empty string edges (essentially)
        self.eclosuer(sigma_sets, call_sigma_sets, sigma_end_to_call, sigma_end_to_exit, sigma_return_to_end)

        # loop until there are no more input tokens (there is probably a better way to write this)
        while True:
            # get next token in the input
            tok = self.lexer.token()
            # check if reached end of input
            if not tok:
                break

            # create next sigma set
            next_set = set()
            next_call_set = set()

            # loop through all elements in prev sigma set and see if there is an edge with label tok
            # this is the scan inference rule for the early recognizer on pg 12 of gfg paper
            for element in sigma_sets[-1]:
                node_label, tag = element
                node = self.nodes[node_label]

                if node.is_scan:
                    for dest_label, edge_label in node.outgoing_edges.items():
                        if (edge_label == tok.type):
                            # propagate current tag to next 
                            next_set.add((dest_label, tag))

                            if self.nodes[dest_label].is_call:
                                next_call_set.add((dest_label, tag))

            # append the next sigma set and map end to call
            sigma_sets.append(next_set)
            call_sigma_sets.append(next_call_set)
            sigma_end_to_call.append({})
            sigma_end_to_exit.append({})
            sigma_return_to_end.append({})
            # eclosuer updates both next_set and the last map in sigma_end_to_call
            self.eclosuer(sigma_sets, call_sigma_sets, sigma_end_to_call, sigma_end_to_exit, sigma_return_to_end)
        
        # return whether <S•, 0> is in last sigma set 
        return (1, 0) in sigma_sets[-1]

    def parse_string(self,data):
        self.lexer.input(data)

        sigma_sets = []
        call_sigma_sets = [set()]
        # zeroth sigma set initially contains <•S, 0>
        # implements the init inference rule
        sigma_sets.append(set([(0, 0)]))
        # maps an end node of production to all call nodes that invoked that production
        # in its corresponding sigma set, used from going from an end node to a return node
        # in the eclosuer function
        sigma_end_to_call = []
        sigma_end_to_call.append({})

        sigma_end_to_exit = []
        sigma_end_to_exit.append({})

        sigma_return_to_end = []
        sigma_return_to_end.append({})

        # find all nodes from S• that can be reached by taking empty string edges (essentially)
        self.eclosuer(sigma_sets, call_sigma_sets, sigma_end_to_call, sigma_end_to_exit, sigma_return_to_end)

        # loop until there are no more input tokens (there is probably a better way to write this)
        while True:
            # get next token in the input
            tok = self.lexer.token()
            # check if reached end of input
            if not tok:
                break

            # create next sigma set
            next_set = set()
            next_call_set = set()

            # loop through all elements in prev sigma set and see if there is an edge with label tok
            # this is the scan inference rule for the early recognizer on pg 12 of gfg paper
            for element in sigma_sets[-1]:
                node_label, tag = element
                node = self.nodes[node_label]

                if node.is_scan:
                    for dest_label, edge_label in node.outgoing_edges.items():
                        if (edge_label == tok.type):
                            # propagate current tag to next 
                            next_set.add((dest_label, tag))

                            if self.nodes[dest_label].is_call:
                                next_call_set.add((dest_label, tag))

            # append the next sigma set and map end to call
            sigma_sets.append(next_set)
            call_sigma_sets.append(next_call_set)
            sigma_end_to_call.append({})
            sigma_end_to_exit.append({})
            sigma_return_to_end.append({})
            # eclosuer updates both next_set and the last map in sigma_end_to_call
            self.eclosuer(sigma_sets, call_sigma_sets, sigma_end_to_call, sigma_end_to_exit, sigma_return_to_end)
        
        # return whether <S•, 0> is in last sigma set 
        if (1, 0) not in sigma_sets[-1]:
            return False
        
        # string is in grammar, traverse backwards through sigma sets to build a parse tree

        # start with <S•, 0> in last sigma set
        curr_elem = (1, 0)
        curr_sigma_num = len(sigma_sets) - 1
        stack = []

        output_stack = []

        processed = set()

        while (curr_elem != (0, 0)):
            label, tag = curr_elem

            node = self.nodes[label]
            # print(curr_sigma_num, f"Current elemn is ({self.nodes[label].long_name}, {tag}, {curr_sigma_num})")

            if node.type == "start":
                # implements CALL^-1 rule on pg 12
                curr_elem = stack.pop()
                output_stack.pop()
            elif node.type == "end":
                # print(f"({self.nodes[label].long_name}, {tag}, {curr_sigma_num})")
                # implements EXIT^-1 rule, has non determinism
                # At A•, go to A->something•, may be multiple possible values

                # OLD INEFFICIENT CODE
                # for src_label in node.incoming_edges:
                #     if (src_label, tag) in sigma_sets[curr_sigma_num]:
                #         curr_elem = (src_label, tag)

                #         prod_name = self.map_start_to_prod_name[self.map_end_to_start[label]]

                #         prod_children = []
                #         if len(output_stack) != 0:
                #             # add production as a child to current production
                #             output_stack[-1][1].insert(0, (prod_name, prod_children)) 
                #         # set this production to the current production
                #         output_stack.append((prod_name, prod_children))
                #         break

                if (label, tag, curr_sigma_num) in processed:
                    # already processed end label, randomize list of productions that produced end node
                    # to get out of cycle
                    sigma_end_to_exit[curr_sigma_num][(label, tag)] = list(sigma_end_to_exit[curr_sigma_num][(label, tag)])
                    random.shuffle(sigma_end_to_exit[curr_sigma_num][(label, tag)])
                else:
                    processed.add((label, tag, curr_sigma_num))

                for exit_label in sigma_end_to_exit[curr_sigma_num][(label, tag)]:
                    curr_elem = (exit_label, tag)

                    prod_name = self.map_start_to_prod_name[self.map_end_to_start[label]]

                    prod_children = deque([])
                    if len(output_stack) != 0:
                        # add production as a child to current production
                        output_stack[-1][1].appendleft((prod_name, prod_children))
                    # set this production to the current production
                    output_stack.append((prod_name, prod_children))
                    break

            elif node.is_entry:
                # implements START^-1 rule on pg 12
                # node is A->•something, go back to •A
                # keep same tag
                # there will only be one incoming edge
                for src_label in node.incoming_edges:
                    curr_elem = (src_label, tag)
            elif node.is_return:
                # implements END^-1 rule, has non determinism
                # at A->aB•g, go to B• and add A->a•Bg to stack
                

                call_label = self.map_return_to_call[label]

                # there will only be one incoming edge from B•
                # OLD inefficient code but pretty sure correct
                # for src_label in node.incoming_edges:
                #     # need to find <src_label, k> in current sigma set, need to find k
                #     for sigma_elem in sigma_sets[curr_sigma_num]:
                #         if src_label == sigma_elem[0]:
                #             src_tag = sigma_elem[1]
                #             if (call_label, tag) in sigma_sets[src_tag]:
                #                 stack.append((call_label, tag))
                #                 curr_elem = (src_label, src_tag)
                #                 break

                end_labels = sigma_return_to_end[curr_sigma_num][curr_elem]
                for src_label, src_tag in end_labels:
                    if (call_label, tag) in sigma_sets[src_tag]:
                        stack.append((call_label, tag))
                        curr_elem = (src_label, src_tag)
                        break
            else:
                # incoming edge is a scan edge
                # implements SCAN^-1 rule on pg 12
                # go to previous sigma set
                # there will only be one incoming edge
                for src_label, edge_label in node.incoming_edges.items():
                    if edge_label == "":
                        print ("ERROR EXPECTING SCAN EDGE, got empty edge")
                        return False
                    else:
                        output_stack[-1][1].appendleft(edge_label)
                        curr_elem = (src_label, tag)
                        curr_sigma_num -= 1

        return output_stack[0]


    def is_node_one_before_start(self, node):
        if node.is_entry:
            return False
        if node.is_return:
            return self.nodes[self.map_return_to_call[node.label]].is_entry
        else:
            for src_label in node.incoming_edges:
                return self.nodes[src_label].is_entry

    def get_sppf(self, sigma_sets, sigma_return_to_end, sigma_end_to_exit, curr_elem, curr_sigma_num, sppf):
        label, tag = curr_elem
        new_node = (label, tag, curr_sigma_num)

        if new_node not in sppf.nodes:
            # gfg node that corresponds to with the current label of the current sigma set element
            gfg_node = self.nodes[label]
            
            # case where at A•
            # implements EXIT^-1
            if gfg_node.type == "end":
                prod_name = self.map_start_to_prod_name[self.map_end_to_start[label]]
                print(f"({prod_name}, {tag}, {curr_sigma_num})")
                new_node = (label, tag, curr_sigma_num)
                sppf.add_node(new_node, prod_name, "symbol")

                # at <A•, tag> in E_curr_sigma_num, loop though all <A->something•, tag> in E_curr_sigma_num
                for exit_label in sigma_end_to_exit[curr_sigma_num][(label, tag)]:
                    next_node = self.get_sppf(sigma_sets, sigma_return_to_end, sigma_end_to_exit, (exit_label, tag), curr_sigma_num, sppf)
                    sppf.add_edge(new_node, next_node)  

            # empty production
            # Implements START^-1
            elif gfg_node.type == "production" and gfg_node.is_entry:
                assert tag == curr_sigma_num
                print(f"in empty string case {gfg_node.long_name}")

                sppf.add_node(new_node, gfg_node.long_name, "intermediate")

                epsilon_node = ("ϵ", 0, 0)
                sppf.add_node(epsilon_node, "ϵ", "symbol")

                sppf.add_edge(new_node, epsilon_node)

                return new_node


            # At A -> B•c
            # implements ENTRY_END^-1
            elif gfg_node.type == "production" and self.is_node_one_before_start(gfg_node) and gfg_node.is_return:
                print(f"({gfg_node.long_name}, {tag}, {curr_sigma_num})")

                sppf.add_node(new_node, gfg_node.long_name, "symbol")

                call_label = self.map_return_to_call[label]

                end_labels = sigma_return_to_end[curr_sigma_num][curr_elem]
                for src_label, src_tag in end_labels:
                    if (call_label, tag) in sigma_sets[src_tag]:
                        symbol_node = self.get_sppf(sigma_sets, sigma_return_to_end, sigma_end_to_exit, (src_label, src_tag), curr_sigma_num, sppf)
                        sppf.add_edge(new_node, symbol_node)

            # At A -> a•c
            # implements ENTRY_SCAN^-1
            elif gfg_node.type == "production" and self.is_node_one_before_start(gfg_node):
                # one terminal before start of produciton: EX A->a*B
                print(f" one terminal before start ({gfg_node.long_name}, {tag}, {curr_sigma_num})")

                sppf.add_node(new_node, gfg_node.long_name, "intermediate")

                # will only be one incoming edge
                for src_label, edge_label in gfg_node.incoming_edges.items():
                    terminal_node = (edge_label, curr_sigma_num - 1, curr_sigma_num)
                    sppf.add_node(terminal_node, edge_label, "symbol")

                    sppf.add_edge(new_node, terminal_node)

            # At A ->aB•c
            # implements END^-1
            elif gfg_node.type == "production" and gfg_node.is_return:
                print(f"({gfg_node.long_name}, {tag}, {curr_sigma_num})")

                sppf.add_node(new_node, gfg_node.long_name, "intermediate")

                call_label = self.map_return_to_call[label]

                end_labels = sigma_return_to_end[curr_sigma_num][curr_elem]
                for src_label, src_tag in end_labels:
                    if (call_label, tag) in sigma_sets[src_tag]:
                        production_node = self.get_sppf(sigma_sets, sigma_return_to_end, sigma_end_to_exit, (src_label, src_tag), curr_sigma_num, sppf)
                        prefix_node = self.get_sppf(sigma_sets, sigma_return_to_end, sigma_end_to_exit, (call_label, tag), src_tag, sppf)

                        sppf.add_family(new_node, prefix_node, production_node)
                

            # At A-> ab•c
            # implements SCAN^-1
            elif gfg_node.type == "production":
                print(f"({gfg_node.long_name}, {tag}, {curr_sigma_num})")

                sppf.add_node(new_node, gfg_node.long_name, "intermediate")

                # will only be one incoming edge
                for src_label, edge_label in gfg_node.incoming_edges.items():
                    terminal_node = (edge_label, curr_sigma_num - 1, curr_sigma_num)
                    sppf.add_node(terminal_node, edge_label, "symbol")


                    prefix_sigma_elem = (src_label, tag) 
                    prefix_node = self.get_sppf(sigma_sets, sigma_return_to_end, sigma_end_to_exit, prefix_sigma_elem, curr_sigma_num - 1, sppf)

                    sppf.add_family(new_node, prefix_node, terminal_node)
        else:
            print(f"already processed {new_node}, {self.nodes[label].long_name}")

        return new_node


                    

    def parse_all_trees(self,data):
        self.lexer.input(data)

        # zeroth sigma set initially contains <•S, 0>
        # implements the init inference rule
        sigma_sets = [set([(0, 0)])]
        call_sigma_sets = [set()]
        
        # maps an end node of production to all call nodes that invoked that production
        # in its corresponding sigma set, used from going from an end node to a return node
        # in the eclosuer function
        sigma_end_to_call = []
        sigma_end_to_call.append({})

        sigma_end_to_exit = []
        sigma_end_to_exit.append({})

        sigma_return_to_end = []
        sigma_return_to_end.append({})

        # find all nodes from S• that can be reached by taking empty string edges (essentially)
        self.eclosuer(sigma_sets, call_sigma_sets, sigma_end_to_call, sigma_end_to_exit, sigma_return_to_end)

        # loop until there are no more input tokens (there is probably a better way to write this)
        while True:
            # get next token in the input
            tok = self.lexer.token()
            # check if reached end of input
            if not tok:
                break

            # create next sigma set
            next_set = set()
            next_call_set = set()

            # loop through all elements in prev sigma set and see if there is an edge with label tok
            # this is the scan inference rule for the early recognizer on pg 12 of gfg paper
            for element in sigma_sets[-1]:
                node_label, tag = element
                node = self.nodes[node_label]

                if node.is_scan:
                    for dest_label, edge_label in node.outgoing_edges.items():
                        if (edge_label == tok.type):
                            # propagate current tag to next 
                            next_set.add((dest_label, tag))

                            if self.nodes[dest_label].is_call:
                                next_call_set.add((dest_label, tag))

            # append the next sigma set and map end to call
            sigma_sets.append(next_set)
            sigma_sets[-2] = []
            call_sigma_sets.append(next_call_set)
            sigma_end_to_call.append({})
            sigma_end_to_exit.append({})
            sigma_return_to_end.append({})
            # eclosuer updates both next_set and the last map in sigma_end_to_call
            self.eclosuer(sigma_sets, call_sigma_sets, sigma_end_to_call, sigma_end_to_exit, sigma_return_to_end)
        
        # return whether <S•, 0> is in last sigma set 
        if (1, 0) not in sigma_sets[-1]:
            return False
        
        # string is in grammar, traverse backwards through sigma sets to build a parse tree

        sppf = Sppf()
        self.get_sppf(call_sigma_sets, sigma_return_to_end, sigma_end_to_exit, (1, 0), len(sigma_sets) - 1, sppf)
        return sppf

def print_help(val, level):
    if level == 0:
        print(f" {val}")
    else:
        print("  " * (level - 1) + " |" + "-" + str(val))

def print_tree(node, level=0):
    
    if type(node) is tuple:
        print_help(node[0], level)
        for child in node[1]:
            print_tree(child, level + 1)
    else:
        print_help(node, level)

if __name__ == "__main__":
    # test_gfg = GFG(ExprLexer())
    test_gfg = GFG(ABLexer())

    # simple expression grammar used in gfg paper examples
    productions = {
        "S": [["E"]],
        "E": [["number"],
              ["E", "plus", "E"],
              ["lparen", "E", "plus", "E", "rparen"]
        ]
    }

    # example 2 grammar in Scott's paper
    # productions = {
    #     "S": [["L"]],
    #     "L": [["b"],
    #           ["L", "L"]
    #          ]
    # }

    # example 3 grammar in Scott's paper
    # productions = {
    #     "S": [["A", "T"],
    #           ["a", "T"]],
    #     "A": [["a"],
    #           ["B", "A"]],
    #     "B": [[]],
    #     "T": [["b", "b", "b"]]
    # }

    productions = {
        "S": [["A", "b"],
              ["b", "A"]],
        "A": [["b", "b"]]
    }

    # productions = {
    #     "S": [["S"],
    #           ["b"]]
    # }

    test_gfg.build_gfg(productions, "S")

    # must have graphvis installed for this to work
    # test_gfg.graph.write_png("output.png")

    #data = "7 + 8 + 9"
    # print(f"is {data} in language: {test_gfg.recognize_string(data)}")
    # print(f"{data} parse tree:")
    # print_tree(test_gfg.parse_string(data))


    # sppf = test_gfg.parse_all_trees(data)
    # sppf.graph.write_png("sppf.png")

    # data = "(7+9"
    # print(f"is {data} in language: {test_gfg.recognize_string(data)}")


    data = "bbb"
    print(f"is {data} in language: {test_gfg.recognize_string(data)}")
    print(f"{data} parse tree:")
    res = test_gfg.parse_string(data)
    # print(res)
    print_tree(res)

    # sppf = test_gfg.parse_all_trees(data)
    # if sppf is not False:
    #     sppf.graph.write_png("sppf.png")