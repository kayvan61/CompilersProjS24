import argparse
import time

import sys
import os
 
# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))
 
# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)
 
# adding the parent directory to 
# the sys.path.
sys.path.append(parent)

from gfg import GFG
from ab_lexer import ABLexer

grammars = {
    "b_grammar": {
        "S": [["L"]],
        "L": [["b"],
              ["L", "L"]
             ]
    }
}

lexers = {
    "b_grammar": ABLexer()
}

# @profile
def main(input_string, grammar, lexer, args):
    start_time = time.time()
    
    gfg = GFG(lexer, use_pydot=False)
    gfg.build_gfg(grammar, "S")

    if args.single:
        gfg.parse_string(input_string)
    elif args.topdown:
        res = gfg.parse_top_down(input_string)
        del res
    elif args.bottomup:
        gfg.sppf_forward_inference(input_string)

    end_time = time.time()

    print(end_time-start_time)





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse the given input string with the specified grammar')
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--single', action='store_true', help='Process using single method')
    group.add_argument('--topdown', action='store_true', help='Process using top-down method')
    group.add_argument('--bottomup', action='store_true', help='Process using bottom-up method')

    parser.add_argument('--grammar', type=str, default="b_grammar", help='grammar to use')
    parser.add_argument('--input', type=str, required=True, help='input string to parse')

    args = parser.parse_args()

    main(args.input, grammars[args.grammar], lexers[args.grammar], args)
