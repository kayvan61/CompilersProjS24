import argparse
import time
from lark import Lark

grammars = {
    "b_grammar": '''
                 start: l
                 l: l l | B

                 B: "b"
                 ''',
    "a_grammar": '''
                 start: a
                 a : a A | A

                 A: "a"
                 '''
}

# @profile
def main(input_string, grammar, args):    
    parser = None

    start_time = time.time()

    if args.cyk:
        parser = Lark(grammar, parser='cyk', ordered_sets=False)
    elif args.earley:
        parser = Lark(grammar, parser='earley', ambiguity="forest", ordered_sets=False)

    parser.parse(input_string)

    end_time = time.time()

    print(end_time-start_time)





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse the given input string with the specified grammar')
    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument('--cyk', action='store_true', help='Process using cyk')
    group.add_argument('--earley', action='store_true', help='Process using earley')

    parser.add_argument('--grammar', type=str, default="b_grammar", help='grammar to use')
    parser.add_argument('--input', type=str, required=True, help='input string to parse')

    args = parser.parse_args()

    main(args.input, grammars[args.grammar], args)
