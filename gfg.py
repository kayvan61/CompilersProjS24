from expr_lexer import ExprLexer
from ab_lexer import ABLexer
from sppf import Sppf
import pydot
import queue
from pprint import pprint

# models a single node if the grammar flow graph
class Node:
    def __init__(self, label, long_name, type, non_term):
        self.label = label
        self.long_name = long_name
        self.type = type
        self.non_term = non_term
        self.is_call = False
        self.is_return = False
        self.is_entry = False
        self.is_exit = False
        self.is_scan = False
        self.is_remaining_sentinal = False # if the remainder of the production is in sentinal form. 
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

    def add_node(self, label, long_name, type, non_term):
        self.nodes[label] = Node(label, long_name, type, non_term)
        # add node to pydot graph for visualization/debugging only
        self.graph.add_node(pydot.Node(long_name, shape="circle"))
        return self.nodes[label]
    
    # create the start and end nodes for a given production, curr_label is the next available
    # int label that can be used to represent a node
    def create_start_end_nodes_for_prod(self, prod_name, curr_label):
        self.add_node(curr_label, f"•{prod_name}", "start", prod_name)
        self.add_node(curr_label + 1, f"{prod_name}•", "end", prod_name)

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

                for i, term in enumerate(prod_rhs):
                    new_node = self.add_node(curr_label, f"[{prefix_label}•{term}]", "production", prod_name)
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

                    if term in self.lexer.tokens or term == "empty":
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
                exit_node = self.add_node(curr_label, f"[{prefix_label}•]", "production", prod_name)
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

        for p in productions.keys():
            start = self.map_prod_name_to_start[p]
            end = self.map_start_to_end[start]
            for exit_node in self.nodes[end].incoming_edges.keys():
                # parent is the exit node
                self.nodes[exit_node].is_remaining_sentinal = True # remainder is eps which is sentinal
                for parent_node in self.nodes[exit_node].incoming_edges.keys():
                    cur_node = parent_node
                    while self.nodes[cur_node].is_scan:
                        self.nodes[cur_node].is_remaining_sentinal = True
                        if len(self.nodes[cur_node].incoming_edges) != 1:
                               break
                        cur_node = next(iter(self.nodes[cur_node].incoming_edges.keys()))
    
    # implements early recognizer inference rules on page 12 of gfg paper except for scan
    # inference rule which transitions between sigma sets
    def eclosuer(self, sigma_sets, sigma_end_to_call):
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
                        if return_elem not in curr_sigma_set:
                            curr_sigma_set.add(return_elem)
                            label_queue.put(return_elem)
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
                            sigma_end_to_call[sigma_num][end_label].append((label, tag))
                        elif end_label not in sigma_end_to_call[sigma_num]:
                            # hanldes case where this is the first call node for the production
                            sigma_end_to_call[sigma_num][end_label] = [(label, tag)] 
                    
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
        
        # print("curr sigma set", curr_sigma_set)
        # print("curr sigma end to call", sigma_end_to_call[-1])
        # print("------------------------")

    # returns True if string is language of grammar of gfg, False otherwise
    def recognize_string(self,data):
        self.lexer.input(data)

        sigma_sets = []
        # zeroth sigma set initially contains <•S, 0>
        # implements the init inference rule
        sigma_sets.append(set([(0, 0)]))
        # maps an end node of production to all call nodes that invoked that production
        # in its corresponding sigma set, used from going from an end node to a return node
        # in the eclosuer function
        sigma_end_to_call = []
        sigma_end_to_call.append({})

        # find all nodes from S• that can be reached by taking empty string edges (essentially)
        self.eclosuer(sigma_sets, sigma_end_to_call)

        # loop until there are no more input tokens (there is probably a better way to write this)
        while True:
            # get next token in the input
            tok = self.lexer.token()
            # check if reached end of input
            if not tok:
                break

            # create next sigma set
            next_set = set()

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

            # append the next sigma set and map end to call
            sigma_sets.append(next_set)
            sigma_end_to_call.append({})
            # eclosuer updates both next_set and the last map in sigma_end_to_call
            self.eclosuer(sigma_sets, sigma_end_to_call)
        
        # return whether <S•, 0> is in last sigma set 
        return (1, 0) in sigma_sets[-1]
    
    def sppf_forward_inference(self, data, start_prod="S"):
        self.lexer.input(data)
        sigma_sets = [set() for x in range(len(data) + 1)]
        self.family_map = {}
        sppf = Sppf() 

        Q_p = set()
        R = set()
        V = set()

        start_node = self.map_prod_name_to_start[start_prod]
        print(start_node)
        sigma_sets[0].add((start_node, 0, -1)) # just add the start node

        for i in range(len(data) + 1):
            R = sigma_sets[i].copy()
            H = {} # used for epsilon productions
            Q = Q_p
            Q_p = set()

            # start speculative phase
            while len(R) > 0:
                cur_node_idx, cur_node_tag, cur_node_sppf = R.pop()
                print(f"speculate on node: ({self.nodes[cur_node_idx]}, {cur_node_tag}, {cur_node_sppf})")

                # calls should goto their starts
                if self.nodes[cur_node_idx].is_call:
                    for target, token in self.nodes[cur_node_idx].outgoing_edges.items():
                        e_item = (target, i, -1)
                        if e_item not in sigma_sets[i]:
                            print(f"adding to sigma set: ({self.nodes[target]}, {i}, {-1})")
                            R.add(e_item)
                            sigma_sets[i].add(e_item)

                # scan nodes should be added to Q
                if self.nodes[cur_node_idx].is_scan and self.nodes[cur_node_idx].is_entry:
                    for target, token in self.nodes[cur_node_idx].outgoing_edges.items():
                        if self.nodes[cur_node_idx].is_entry:
                            print(f"adding to Q: ({self.nodes[cur_node_idx]}, {i}, {-1})")
                            Q.add((cur_node_idx, i, -1))
                
                # exit from an epsilon
                if self.nodes[cur_node_idx].is_exit and cur_node_sppf == -1:
                    sppf.add_node((cur_node_idx, i, i), str(self.nodes[cur_node_idx]), "")
                    sppf.add_node(("ϵ", i, i), "ϵ", "")
                    sppf.add_edge((cur_node_idx, i, i), ("ϵ", i, i))
                    cur_item = (cur_node_idx, cur_node_tag, cur_node_sppf)
                    sigma_sets[i].remove(cur_item)
                    sigma_sets[i].add((cur_node_idx, cur_node_tag, (cur_node_idx, i, i)))
                    R.add((cur_node_idx, cur_node_tag, (cur_node_idx, i, i)))

                #exits just add the end
                if self.nodes[cur_node_idx].is_exit and cur_node_sppf != -1:
                    print("found an exit node")
                    end_node = list(self.nodes[cur_node_idx].outgoing_edges)[0]
                    # create the end sppf node
                    new_sppf_node = self.make_forward_node_inference(end_node, cur_node_tag, i, cur_node_sppf, -1, sppf)
                    assert(new_sppf_node != -1)
                    e_item = (end_node, cur_node_tag, new_sppf_node)
                    assert(self.nodes[end_node].type == "end")
                    R.add(e_item)
                    sigma_sets[i].add(e_item)
                
                # start nodes should explore all the prods with tag i
                if self.nodes[cur_node_idx].type == "start":
                    for target, token in self.nodes[cur_node_idx].outgoing_edges.items():
                        e_item = (target, i, -1)
                        if e_item not in sigma_sets[i]:
                            print(f"adding to sigma set: ({self.nodes[target]}, {i}, {-1})")
                            R.add(e_item)
                            sigma_sets[i].add(e_item)                    

                # end nodes need to return properly
                if self.nodes[cur_node_idx].type == "end" and cur_node_sppf != -1:
                    print("found an end node")
                    # find the person that called the thing we ended
                    start_node = self.map_end_to_start[cur_node_idx]
                    new_sigma_items = set()
                    for caller_node_idx, caller_node_tag, caller_node_sppf in sigma_sets[cur_node_tag]:
                        print(f"candidate caller: {self.nodes[caller_node_idx]}, {caller_node_tag}, {caller_node_sppf}")
                        if self.nodes[caller_node_idx].is_call:
                            target_start = list(self.nodes[caller_node_idx].outgoing_edges)[0]
                            # this is maybe the item that called us
                            if target_start == start_node:
                                ret_node = self.map_call_to_return[caller_node_idx]
                                print(f"call to: {self.nodes[caller_node_idx]}")
                                print(f"ret to: {self.nodes[ret_node]}")
                                new_sppf_node = self.make_forward_node_inference(ret_node, caller_node_tag, i, caller_node_sppf, cur_node_sppf, sppf)
                                new_item = (ret_node, caller_node_tag, new_sppf_node)
                                if new_item not in sigma_sets[i]:
                                    print(f"adding to sigma set: ({self.nodes[ret_node]}, {caller_node_tag}, {-1})")
                                    if i != cur_node_tag:
                                        R.add(new_item)
                                        sigma_sets[i].add(new_item)
                                    else:
                                        R.add(new_item)
                                        new_sigma_items.add(new_item)
                                if self.nodes[ret_node].is_scan:
                                    print(f"adding to Q after ret: ({self.nodes[ret_node]}, {caller_node_tag}, {-1})")
                                    Q.add(new_item)
                    for x in new_sigma_items:
                        sigma_sets[i].add(x) 
            
            # make the token node
            in_tok = self.lexer.token() 
            in_tok = in_tok.type if in_tok is not None else None
            if in_tok is not None:
                sppf.add_node((in_tok, i, i+1), in_tok, "")
                v = (in_tok, i, i+1)
                print("creating token node:", (in_tok, i, i+1))
            

            # scanned forward. glue to created node, and put in next sigma set
            while len(Q) > 0:
                cur_node_idx, cur_node_tag, cur_node_sppf = Q.pop()
                print(f"scan on node: ({self.nodes[cur_node_idx]}, {cur_node_tag}, {cur_node_sppf})")
                for target, token in self.nodes[cur_node_idx].outgoing_edges.items():
                    if token != in_tok:
                        continue
                    y = self.make_forward_node_inference(target, cur_node_tag, i+1, cur_node_sppf, v, sppf)
                    e_item = (target, cur_node_tag, y)
                    
                    # scan through and add it to the next set
                    if self.nodes[target].is_remaining_sentinal or self.nodes[target].is_call:
                        print(f"adding to sigma': ({self.nodes[target]}, {cur_node_tag}, {y})")
                        sigma_sets[i+1].add(e_item)
            
                    # scan once again to keep Q' populated with ongoing terminal parses
                    for _, token in self.nodes[target].outgoing_edges.items():
                        if in_tok is not None and token == in_tok:
                            print(f"adding to Q': ({self.nodes[target]}, {cur_node_tag}, {y})")
                            Q_p.add(e_item)
        

        for sset in sigma_sets:
            for node, index, sppf_node in sset:
                print(f"({self.nodes[node]}, {index}, {sppf_node})", end=", ")
            print()
        
        for x in sigma_sets[-1]:
            if x[0] == 1 and x[1] == 0:
                print("tree root", x[2])
                sppf.rebuild_with_root(x[2])
                return sppf
        return False
                        
    def make_forward_node_inference(self, gfg_item, start_index, end_index, existing_node, new_node, sppf):
        if existing_node == -1 and new_node == -1:
            return -1
        # no existing tag node then we can just create the new node and make it a child
        if existing_node != -1 and new_node != -1:
            # this item
            sppf.add_node((gfg_item, start_index, end_index), str(self.nodes[gfg_item]), "")
            sppf.add_family((gfg_item, start_index, end_index), existing_node, new_node)
            return (gfg_item, start_index, end_index)
        elif existing_node == -1:
            sppf.add_node((gfg_item, start_index, end_index), str(self.nodes[gfg_item]), "")
            sppf.add_edge((gfg_item, start_index, end_index), new_node)
            return (gfg_item, start_index, end_index)
        elif new_node == -1:
            sppf.add_node((gfg_item, start_index, end_index), str(self.nodes[gfg_item]), "")
            sppf.add_edge((gfg_item, start_index, end_index), existing_node)
            return (gfg_item, start_index, end_index)

    def sppf_forward(self, data, start_producition="S"):
        self.lexer.input(data)
        sigma_sets = [set() for x in range(len(data) + 1)]
        self.family_map = {}
        sppf = Sppf()

        Q_p = set() # scan forward elements 
        R = set() # set of items that need to be processed to add to cur sigma
        V = set() # created sppf nodes

        # set of start nodes that are all terminals or start with a call
        in_tok = self.lexer.token().type

        # all productions out of the start of start symbol
        # first for all in paper
        # find all the things that we should explore, or that consume the first token
        START_PROD = self.map_prod_name_to_start[start_producition]
        for entry_child, _ in self.nodes[START_PROD].outgoing_edges.items():
            if self.nodes[entry_child].is_call or self.nodes[entry_child].is_remaining_sentinal:
                print(f"add {self.nodes[entry_child]} to initial sigma set")
                sigma_sets[0].add((entry_child, 0, -1))

            scan_child, scan_tok = next(iter(self.nodes[entry_child].outgoing_edges.items()))
            if self.nodes[entry_child].is_scan or (self.nodes[entry_child].is_entry and self.nodes[entry_child].is_exit):
                if scan_tok == in_tok or (self.nodes[entry_child].is_entry and self.nodes[entry_child].is_exit):
                    Q_p.add((entry_child, 0, -1))
        v = -1

        for i in range(len(data)+1): 
            R = sigma_sets[i].copy()
            H = {} # when we hit the end of a production, we need to backtrack to the caller. (Start node, sppf node)
            Q = Q_p
            Q_p = set()

            # current Earley set to explore. 
            while len(R) > 0:
                element = R.pop()
                ele_node = self.nodes[element[0]]
                h = element[1]
                w = element[2]

                print("processing", ele_node, h, w)
                
                # R and E can be thought of what we explore NOW
                # Q can be thought of what we should explore NEXT
                # we push things into the Q so we can have the token SPPF node created
                # we push things into R so we can check if it matches another node created
                
                # call to production should go explore the production
                if ele_node.is_call:
                    print(f"found call {ele_node}")
                    start_label = next(iter(ele_node.outgoing_edges.keys()))
                    start_node = self.nodes[start_label]
                    if start_label in H.keys():
                        print("in h!!!!!!")
                        exit()
                    for child, tok in start_node.outgoing_edges.items():
                        e_item = (child, i, -1)
                        if (self.nodes[child].is_entry and self.nodes[child].is_exit):
                            print(f"added Q {(child, i, -1)} epsilon")
                            Q.add((child, i, -1))
                            
                        if (self.nodes[child].is_call or self.nodes[child].is_remaining_sentinal) and e_item not in sigma_sets[i]:
                            print("added R")
                            R.add(e_item)
                            sigma_sets[i].add(e_item)
                        
                        scan_child, scan_tok = next(iter(self.nodes[child].outgoing_edges.items()))
                        if self.nodes[child].is_scan:
                            print("scan checking:", self.nodes[scan_child], scan_tok, in_tok)
                            if in_tok == scan_tok or (self.nodes[child].is_entry and self.nodes[child].is_exit):
                                print(f"added Q {(child, i, -1)} {self.nodes[child]}")
                                Q.add((child, i, -1))

                if ele_node.type == "end":
                    print(f"end {ele_node}")
                    
                # on the end of a parse we should go back to the caller. 
                # if the caller is done we should then add an sppf node which is under.
                if ele_node.is_exit:
                    print(f"found exit {ele_node}, {h}, {w}")
                    end_node = next(iter(ele_node.outgoing_edges.keys()))
                    start_node = self.map_end_to_start[end_node]
                    if w == -1:
                        attempted_node = (self.nodes[end_node], i, i)
                        sppf.add_node(attempted_node, str(self.nodes[end_node]), "")
                        epsilon_node = ("ϵ", 0, 0)
                        sppf.add_node(epsilon_node, "ϵ", "symbol")
                        sppf.add_edge(attempted_node, epsilon_node)
                        print(f"eps before {sigma_sets[i]}")
                        sigma_sets[i].remove(element)
                        sigma_sets[i].add((element[0], element[1], attempted_node))
                        w = attempted_node
                        print(f"eps after {sigma_sets[i]}")
                    if h == i:
                        print(f"add to H {self.nodes[start_node]}")
                        H[start_node] = w
                    again = True
                    while again:
                        temp_sigma = sigma_sets[h].copy()
                        again = False
                        for item, k, z in temp_sigma:
                            if not self.nodes[item].is_call:
                                continue
                            if not (next(iter(self.nodes[item].outgoing_edges.keys())) == start_node):
                                continue
                            return_node = self.map_call_to_return[item]
                            print("return checks", self.nodes[return_node])
                            # item is a call to the prod we just finished
                            y = self.make_forward_node(return_node, k, i, z, w, V, sppf)
                            e_item = (return_node, k, y)
                            if (self.nodes[return_node].is_call or self.nodes[return_node].is_remaining_sentinal) and e_item not in sigma_sets[i]:
                                again = True
                                sigma_sets[i].add(e_item)
                                R.add(e_item)
                                print("call back")
                                print("finished prod:", self.nodes[end_node], h, w)
                                print("return node:", self.nodes[return_node], k, z)
                            
                            # we can scan here. add to Q
                            scan_child, scan_tok = next(iter(self.nodes[return_node].outgoing_edges.items()))
                            if self.nodes[return_node].is_scan or (self.nodes[return_node].is_entry and self.nodes[return_node].is_exit):
                                print("scan checking:", self.nodes[scan_child], scan_tok, in_tok)
                                if in_tok == scan_tok or (self.nodes[return_node].is_entry and self.nodes[return_node].is_exit):
                                    print(f"added Q {e_item} {self.nodes[e_item[0]]}")
                                    Q.add(e_item)
                        
                    

            V = set()
            #create an SPPF node v labelled (a_i+1,i,i+1)
            if in_tok is not None:
                sppf.add_node((in_tok, i, i+1), in_tok, "")
                v = (in_tok, i, i+1)
                print("creating token node:", (in_tok, i, i+1))

            print("start scan")
            
            in_tok = self.lexer.token() 
            in_tok = in_tok.type if in_tok is not None else None
            while len(Q) > 0:
                element = Q.pop()
                node, h, w = element
                if self.nodes[node].is_scan or self.nodes[node].is_exit:
                    print("scan forward attempt:", self.nodes[node], h, w)
                    next_node = next(iter(self.nodes[node].outgoing_edges))
                    y = self.make_forward_node(next_node, h, i+1, w, v, V, sppf)
                    e_item = (next_node, h, y)
                    if self.nodes[next_node].is_call or self.nodes[next_node].is_remaining_sentinal:
                        print("sigma set advance", self.nodes[next_node])
                        sigma_sets[i+1].add(e_item)

                    if self.nodes[node].is_scan or (self.nodes[node].is_entry and self.nodes[node].is_exit):
                        # on return need to scan
                        for scan_child, scan_tok in self.nodes[next_node].outgoing_edges.items():
                            if (in_tok is not None and (in_tok == scan_tok or scan_tok == "empty")) or (self.nodes[node].is_entry and self.nodes[node].is_exit):
                                Q_p.add(e_item)
                                print(f"added Q {e_item}")
                                print("added scan Q_p", self.nodes[next_node])
            print("-"*10)

        print("working ssets:")
        for sset in sigma_sets:
            for node, index, sppf_node in sset:
                print(f"({self.nodes[node]}, {index}, {sppf_node})", end=", ")
            print()
        for x in sigma_sets[-1]:
            if self.nodes[x[0]].is_exit:
                end_node = next(iter(self.nodes[x[0]].outgoing_edges))
                #return x[2]
                if end_node == 1:
                    print("tree root", x[2])
                    sppf.rebuild_with_root(x[2])
                    return sppf
        print("no parse!")
        print()
        return False
            

    def make_forward_node(self, ret, j, i, w, other_sppf_node, all_sppf_nodes, sppf):
        # if done we should create the node that captures the whole production
        print(f"input to make node {self.nodes[ret]}, {j}, {i}")
        if self.nodes[ret].is_exit:
            s = next(iter(self.nodes[ret].outgoing_edges))
            s = self.map_end_to_start[s]
            s = self.nodes[s]
            print(f"change node to {s}")
            # s = self.map_start_to_prod_name[s]
        else:
            s = self.nodes[ret]
        
        # if we just started then we should set y to the node given to us
        if self.nodes[ret].is_entry:
            y = other_sppf_node
        else:
            attempted_node = (s, j, i)
            print("w node:", w)
            print("attempted node:", attempted_node)
            if attempted_node not in all_sppf_nodes:
                print("creating sppf node:", attempted_node)
                all_sppf_nodes.add(attempted_node)
                ln = s.long_name
                if s.is_call:
                    print("create call node")
                if s.type == "start":
                    ln = self.map_start_to_prod_name[s.label]
                sppf.add_node(attempted_node, ln, "")
            if w == -1:
                if other_sppf_node not in [x[0] for x in sppf.nodes[attempted_node].outgoing_edges.items()]:
                    print("add edge", attempted_node, other_sppf_node)
                    sppf.add_edge(attempted_node, other_sppf_node)
            if w != -1:
                family_def = (f"{w},{other_sppf_node}", w, other_sppf_node)
                if family_def not in [x[0] for x in sppf.nodes[attempted_node].outgoing_edges.items()]:
                    print("add family", attempted_node, w, other_sppf_node)
                    sppf.add_family(attempted_node, w, other_sppf_node)
            y = attempted_node
        return y


    def parse_string(self,data):
        self.lexer.input(data)

        sigma_sets = []
        # zeroth sigma set initially contains <•S, 0>
        # implements the init inference rule
        sigma_sets.append(set([(0, 0)]))
        # maps an end node of production to all call nodes that invoked that production
        # in its corresponding sigma set, used from going from an end node to a return node
        # in the eclosuer function
        sigma_end_to_call = []
        sigma_end_to_call.append({})

        # find all nodes from S• that can be reached by taking empty string edges (essentially)
        self.eclosuer(sigma_sets, sigma_end_to_call)

        # loop until there are no more input tokens (there is probably a better way to write this)
        while True:
            # get next token in the input
            tok = self.lexer.token()
            # check if reached end of input
            if not tok:
                break

            # create next sigma set
            next_set = set()

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

            # append the next sigma set and map end to call
            sigma_sets.append(next_set)
            sigma_end_to_call.append({})
            # eclosuer updates both next_set and the last map in sigma_end_to_call
            self.eclosuer(sigma_sets, sigma_end_to_call)
        
        # return whether <S•, 0> is in last sigma set 
        if (1, 0) not in sigma_sets[-1]:
            return False
        
        # string is in grammar, traverse backwards through sigma sets to build a parse tree

        # start with <S•, 0> in last sigma set
        curr_elem = (1, 0)
        curr_sigma_num = len(sigma_sets) - 1
        stack = []

        output_stack = []

        while (curr_elem != (0, 0)):
            label, tag = curr_elem

            node = self.nodes[label]
            # print(curr_sigma_num, f"Current elemn is ({label}, {tag})", f"\t\tstack is {stack}")

            if node.type == "start":
                # implements CALL^-1 rule on pg 12
                curr_elem = stack.pop()
                output_stack.pop()
            elif node.type == "end":
                print(f"({self.nodes[label].long_name}, {tag}, {curr_sigma_num})")
                # implements EXIT^-1 rule, has non determinism
                # At A•, go to A->something•, may be multiple possible values
                for src_label in node.incoming_edges:
                    if (src_label, tag) in sigma_sets[curr_sigma_num]:
                        curr_elem = (src_label, tag)
                        # output name of production, if at A• output A (#TODO CHECK NOT A->something•)
                        prod_name = self.map_start_to_prod_name[self.map_end_to_start[label]]
                        # output.append(self.nodes[src_label].long_name)

                        prod_children = []
                        if len(output_stack) != 0:
                            # add production as a child to current production
                            output_stack[-1][1].insert(0, (prod_name, prod_children))
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
                # there will only be one incoming edge from B•
                for src_label in node.incoming_edges:
                    call_label = self.map_return_to_call[label]
                    # need to find <src_label, k> in current sigma set, need to find k
                    for sigma_elem in sigma_sets[curr_sigma_num]:
                        if src_label == sigma_elem[0]:
                            src_tag = sigma_elem[1]
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
                        output_stack[-1][1].insert(0, edge_label)
                        curr_elem = (src_label, tag)
                        curr_sigma_num -= 1

    def get_sppf(self, sigma_sets, curr_elem, curr_sigma_num, sppf):
        label, tag = curr_elem
        new_node = (label, tag, curr_sigma_num)
        
        if new_node not in sppf.nodes:
            # gfg node that corresponds to with the current label of the current sigma set element
            gfg_node = self.nodes[label]        
        
            # case where at A•
            if gfg_node.type == "end":
                prod_name = self.map_start_to_prod_name[self.map_end_to_start[label]]
                print(f"({prod_name}, {tag}, {curr_sigma_num})")
                sppf.add_node(new_node, prod_name, "symbol")

                # implements EXIT^-1 rule, has non determinism
                # At A•, go to A->something•, may be multiple possible values
                for src_label in gfg_node.incoming_edges:
                    next_elem = (src_label, tag)
                    if next_elem in sigma_sets[curr_sigma_num]:
                        next_node = self.get_sppf(sigma_sets, next_elem, curr_sigma_num, sppf)
                        sppf.add_edge(new_node, next_node)

            elif gfg_node.type == "production" and gfg_node.is_entry:
                assert tag == curr_sigma_num
                print(f"in empty string case {gfg_node.long_name}")

                sppf.add_node(new_node, gfg_node.long_name, "intermediate")

                epsilon_node = ("ϵ", 0, 0)
                sppf.add_node(epsilon_node, "ϵ", "symbol")

                sppf.add_edge(new_node, epsilon_node)


            elif gfg_node.type == "production" and gfg_node.is_return:
                print(f"({gfg_node.long_name}, {tag}, {curr_sigma_num})")

                sppf.add_node(new_node, gfg_node.long_name, "intermediate")

                # at A->aB•g, go to B• and add A->a•Bg to stack
                # there will only be one incoming edge from B•
                for src_label in gfg_node.incoming_edges:
                    call_label = self.map_return_to_call[label]
                    # need to find <src_label, k> in current sigma set, need to find k
                    for sigma_elem in sigma_sets[curr_sigma_num]:
                        if src_label == sigma_elem[0]:
                            src_tag = sigma_elem[1]
                            if (call_label, tag) in sigma_sets[src_tag]:
                                production_node = self.get_sppf(sigma_sets, sigma_elem, curr_sigma_num, sppf)
                                prefix_node = self.get_sppf(sigma_sets, (call_label, tag), src_tag, sppf)

                                sppf.add_family(new_node, prefix_node, production_node)



            elif gfg_node.type == "production":
                print(f"({gfg_node.long_name}, {tag}, {curr_sigma_num})")

                sppf.add_node(new_node, gfg_node.long_name, "intermediate")

                
                # will only be one incoming edge
                for src_label, edge_label in gfg_node.incoming_edges.items():
                    terminal_node = (edge_label, curr_sigma_num - 1, curr_sigma_num)
                    sppf.add_node(terminal_node, edge_label, "symbol")

                    prefix_sigma_elem = (src_label, tag) 
                    prefix_node = self.get_sppf(sigma_sets, prefix_sigma_elem, curr_sigma_num - 1, sppf)

                    sppf.add_family(new_node, prefix_node, terminal_node)

        return new_node


                    

    def parse_all_trees(self,data):
        self.lexer.input(data)

        sigma_sets = []
        # zeroth sigma set initially contains <•S, 0>
        # implements the init inference rule
        sigma_sets.append(set([(0, 0)]))
        # maps an end node of production to all call nodes that invoked that production
        # in its corresponding sigma set, used from going from an end node to a return node
        # in the eclosuer function
        sigma_end_to_call = []
        sigma_end_to_call.append({})

        # find all nodes from S• that can be reached by taking empty string edges (essentially)
        self.eclosuer(sigma_sets, sigma_end_to_call)

        # loop until there are no more input tokens (there is probably a better way to write this)
        while True:
            # get next token in the input
            tok = self.lexer.token()
            # check if reached end of input
            if not tok:
                break

            # create next sigma set
            next_set = set()

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

            # append the next sigma set and map end to call
            sigma_sets.append(next_set)
            sigma_end_to_call.append({})
            # eclosuer updates both next_set and the last map in sigma_end_to_call
            self.eclosuer(sigma_sets, sigma_end_to_call)
        
        # return whether <S•, 0> is in last sigma set 
        if (1, 0) not in sigma_sets[-1]:
            return False
        
        # string is in grammar, traverse backwards through sigma sets to build a parse tree

        sppf = Sppf()
        self.get_sppf(sigma_sets, (1, 0), len(sigma_sets) - 1, sppf)
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
    #test_gfg = GFG(ExprLexer())
    test_gfg = GFG(ABLexer())

    productions = {
        "S": [["A", "b"], ["b", "A"]],
        "A": [["b", "b", "b"]],
    }

    productions = {
        "S": [["S"], ["b"], ["A", "b"]],
        "A": [["b"], []],
    }
    
    # simple expression grammar used in gfg paper examples
    # productions = {
    #     "S": [["E"]],
    #     "E": [["number"],
    #           ["E", "plus", "E"],
    #           ["lparen", "E", "plus", "E", "rparen"]
    #     ]
    # }

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

    test_gfg.build_gfg(productions, "S")

    # must have graphvis installed for this to work
    test_gfg.graph.write_png("output.png")

    #data = "7 + 8 + 9"
    # print(f"is {data} in language: {test_gfg.recognize_string(data)}")
    # print(f"{data} parse tree:")
    # print_tree(test_gfg.parse_string(data))


    # sppf = test_gfg.parse_all_trees(data)
    # sppf.graph.write_png("sppf.png")

    # data = "(7+9"
    # print(f"is {data} in language: {test_gfg.recognize_string(data)}")

    data = "b"
    print(f"is {data} in language: {test_gfg.recognize_string(data)}")
    # print(f"{data} parse tree:")
    # print_tree(test_gfg.parse_string(data))

    # sppf = test_gfg.parse_all_trees(data)
    # sppf.graph.write_png("sppf.png")
    ret = test_gfg.parse_all_trees(data)
    ret.graph.write_png("sppf.png")
    f_sppf = test_gfg.sppf_forward_inference(data)
    #f_sppf = test_gfg.sppf_forward(data)
    f_sppf.graph.write_png("sppf_forward.png")
