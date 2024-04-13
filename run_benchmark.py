
import tracemalloc
import psutil
import time
from gfg import GFG
from expr_lexer import ExprLexer
from ab_lexer import ABLexer
from lark import Lark
import os

import argparse


def run_benchmark(parser, string, num_repeat):
    times = []

    for _ in range(0, num_repeat):
        start_time = time.time()
        res = parser(string)
        end_time = time.time()
        
        times.append(end_time - start_time)

    avg_time = sum(times) / num_repeat


    peak_mems = []

    for _ in range(0, num_repeat):
        tracemalloc.start()

        res = parser(string)
        if res is None:
            raise Exception("Result from parser must not be None")
                
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        

        peak_mems.append(peak)
        # print(peak)

    avg_mem_usage = sum(peak_mems) / num_repeat

    

    return (avg_time, avg_mem_usage)


def generate_b_strings():
    count = 1
    while True:
        yield 'b' * count
        count += 1


def run_benchmarks(parser, generator, max_str_len, num_repeat):
    input_len = []
    avg_times = []
    avg_mems = []

    string = next(generator)

    while len(string) <= max_str_len:
        time, mem = run_benchmark(parser, string, num_repeat)

        input_len.append(len(string))
        avg_times.append(time)
        avg_mems.append(mem)

        string = next(generator)

    return (input_len, avg_times, avg_mems)

def get_b_grammar_parsers():
    res = []

    grammar = {
        "S": [["L"]],
        "L": [["b"],
              ["L", "L"]
             ]
    }

    gfg = GFG(ABLexer(), use_pydot=False)
    gfg.build_gfg(grammar, "S")

    res.append((gfg.parse_all_trees, "gfg_top_down_sppf"))
    res.append((gfg.parse_string, "gfg_single_tree"))

    grammar = '''
    start: s
    s: l
    l: l l | B

    B: "b"
    '''

    lark_earley_sppf = Lark(grammar, parser='earley', ambiguity="forest", ordered_sets=False)
    res.append((lark_earley_sppf.parse, "lark_earley_sppf"))
    
    lark_cyk_single = Lark(grammar, parser='cyk', ordered_sets=False)
    res.append((lark_cyk_single.parse, "lark_cyk_single"))


    return res


def write_benchmark_results_to_file(input_len, times, memory_usages, output_file):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        for i in range(min(len(input_len), len(times), len(memory_usages))):
            f.write(f"{input_len[i]},{times[i]},{memory_usages[i]}\n")

def run_benchmarks_all_algorithms(grammar_name, parser_list, generator, max_str_len, num_repeat):

    for parser, parser_name in parser_list:
        input_len, times, mems = run_benchmarks(parser, generator(), max_str_len, num_repeat)

        write_benchmark_results_to_file(input_len, times, mems, f"./{grammar_name}/{parser_name}.csv")
        
        # print(f"PARSER: {parser_name}")
        # print(f"\taverage time in seconds {times}\n\taverage mem usage in mb {[mem / 10**6 for mem in mems]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get num times to repeat each algorithm for each input size and max size of input')

    parser.add_argument('--repeat', type=int, default=10, help='Number of times to repeat each algorithm for a given input size')
    parser.add_argument('--maxSize', type=int, default=30, help='Maximum input size')

    args = parser.parse_args()

    num_repeats = args.repeat
    max_size = args.maxSize


    run_benchmarks_all_algorithms("b_grammar", get_b_grammar_parsers(), generate_b_strings, max_size, num_repeats)
