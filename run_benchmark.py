import psutil
from parse_programs.SparkParsers.sparkparser import BParser
import os
import subprocess
import argparse

def run_benchmark(parser, string, num_repeat):
    parser[-1] = string

    times = []
    
    for _ in range(0, num_repeat):

        # Run the command as a subprocess
        process = subprocess.Popen(parser, cwd='.', stdout=subprocess.PIPE)

        # Wait for the process to finish and get the output
        stdout, _ = process.communicate()
        out = stdout.decode().split()[-1]
        times.append(float(out))

    avg_time = sum(times) / num_repeat

    mems = []

    for _ in range(0, num_repeat):

        max_mem = 0

        process = subprocess.Popen(parser, cwd='.', stdout=subprocess.PIPE)

        info = psutil.Process(process.pid)
        while process.poll() == None:
            try:
                mem = info.memory_info().rss
            except psutil.NoSuchProcess as e:
                print("EXCEPTION getting memory")
                pass
            max_mem = max(max_mem, mem)

        mems.append(max_mem)

    avg_mem_usage = sum(mems) / num_repeat

    return (avg_time, avg_mem_usage)

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

def generate_b_strings():
    count = 10
    while True:
        print(count)
        yield 'b' * count
        count += 10
        

def old_get_b_grammar_parsers():
    res = []

    grammar = {
        "S": [["L"]],
        "L": [["b"],
              ["L", "L"]
             ]
    }

    gfg = GFG(ABLexer(), use_pydot=False)
    gfg.build_gfg(grammar, "S")

    res.append((gfg.parse_top_down, "gfg_top_down_sppf"))
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

    res.append((BParser().scan_and_parse, "spark_earley_single"))

    return res

def get_b_grammar_parsers():
    res = []

    res.append((['python3', './parse_programs/gfg_parse.py', '--topdown', '--input', ''], "gfg_offline_sppf"))
    res.append((['python3', './parse_programs/gfg_parse.py', '--bottomup', '--input', ''], "gfg_online_sppf"))
    res.append((['python3', './parse_programs/gfg_parse.py', '--single', '--input', ''], "gfg_single_tree"))
    res.append((['python3', './parse_programs/lark_parse.py', '--earley', '--input', ''], "lark_online_sppf"))
    res.append((['python3', './parse_programs/lark_parse.py', '--cyk', '--input', ''], "lark_cyk_single"))
    res.append((['python3', './parse_programs/spark_parse.py', '--input', ''], "spark_earley_single"))

    return res

def generate_a_strings():
    count = 20
    while True:
        print(count)
        yield 'a' * count
        count += 20


def get_a_grammar_parsers():
    res = []

    # res.append((['python3', './parse_programs/gfg_parse.py', '--grammar', 'a_grammar', '--topdown', '--input', ''], "gfg_offline_sppf"))
    # res.append((['python3', './parse_programs/gfg_parse.py', '--grammar', 'a_grammar', '--bottomup', '--input', ''], "gfg_online_sppf"))
    # res.append((['python3', './parse_programs/gfg_parse.py', '--grammar', 'a_grammar', '--single', '--input', ''], "gfg_single_tree"))
    # res.append((['python3', './parse_programs/lark_parse.py', '--grammar', 'a_grammar', '--earley', '--input', ''], "lark_online_sppf"))
    # res.append((['python3', './parse_programs/lark_parse.py', '--grammar', 'a_grammar', '--cyk', '--input', ''], "lark_cyk_single"))
    res.append((['python3', './parse_programs/spark_parse.py', '--grammar', 'a_grammar', '--input', ''], "spark_earley_single"))

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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get num times to repeat each algorithm for each input size and max size of input')

    parser.add_argument('--repeat', type=int, default=10, help='Number of times to repeat each algorithm for a given input size')
    parser.add_argument('--maxSize', type=int, default=30, help='Maximum input size')

    args = parser.parse_args()

    num_repeats = args.repeat
    max_size = args.maxSize


    # run_benchmarks_all_algorithms("b_grammar", get_b_grammar_parsers(), generate_b_strings, max_size, num_repeats)
    run_benchmarks_all_algorithms("a_grammar", get_a_grammar_parsers(), generate_a_strings, max_size, num_repeats)