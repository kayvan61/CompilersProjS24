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

from parse_programs.SparkParsers.sparkparser import BParser, AParser

parsers = {
    "b_grammar": BParser(),
    "a_grammar": AParser()
}

def main(input_string, parser):    
    start_time = time.time()

    parser.scan_and_parse(input_string)

    end_time = time.time()

    print(end_time-start_time)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Parse the given input string with the specified grammar')

    parser.add_argument('--grammar', type=str, default="b_grammar", help='grammar to use')
    parser.add_argument('--input', type=str, required=True, help='input string to parse')

    args = parser.parse_args()

    main(args.input, parsers[args.grammar])
