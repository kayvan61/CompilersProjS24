import matplotlib.pyplot as plt

gfg_single_tree = "gfg_single_tree"
gfg_top_down_sppf = "gfg_top_down_sppf"
lark_earley_sppf = "lark_earley_sppf"
lark_cyk_single = "lark_cyk_single"
spark_earley_single = "spark_earley_single"
gfg_bottom_up_sppf = "gfg_bottom_up_sppf"

line_colors =['red', 'blue', 'green', 'orange', "purple", 'yellow']

map_alg_to_color = {
    gfg_single_tree: line_colors[0],
    gfg_top_down_sppf: line_colors[1],
    lark_earley_sppf: line_colors[2],
    lark_cyk_single: line_colors[3],
    spark_earley_single: line_colors[4],
    gfg_bottom_up_sppf: line_colors[5],
}

def read_benchmark_results_from_file(input_file):
    input_len = []
    times = []
    mem_usgaes = []

    with open(input_file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            if len(parts) == 3:
                input_len.append(int(parts[0]))
                times.append(float(parts[1]))
                mem_usgaes.append(float(parts[2]))

    return input_len, times, mem_usgaes

def generate_mem_usage_plot(grammar_name, parser_algorithms):

    for parser in parser_algorithms:
        data_file = f"./{grammar_name}/{parser}.csv"

        input_len, _, mem_usages = read_benchmark_results_from_file(data_file)

        plt.plot(input_len, [mem / 10**6 for mem in mem_usages], label=parser, color=map_alg_to_color[parser])

    plt.xlabel("Length of input string")
    plt.ylabel("Memory utilization in MBs")
    plt.title(f"Parse memory utilization for {grammar_name}")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"./plots/mem-{grammar_name}-{'-'.join(parser_algorithms)}.png")
    plt.clf()

def generate_time_plot(grammar_name, parser_algorithms):

    for parser in parser_algorithms:
        data_file = f"./{grammar_name}/{parser}.csv"

        input_len, times, _ = read_benchmark_results_from_file(data_file)

        plt.plot(input_len, times, label=parser, color=map_alg_to_color[parser])

    plt.xlabel("Length of input string")
    plt.ylabel("Parse time in seconds")
    plt.title(f"Parse times for {grammar_name}")
    plt.legend()
    plt.grid(True)

    plt.savefig(f"./plots/time-{grammar_name}-{'-'.join(parser_algorithms)}.png")
    plt.clf()



if __name__ == "__main__":
    

    generate_time_plot("b_grammar", [gfg_single_tree, gfg_top_down_sppf, lark_earley_sppf, lark_cyk_single, spark_earley_single])
    generate_mem_usage_plot("b_grammar", [gfg_single_tree, gfg_top_down_sppf, lark_earley_sppf, lark_cyk_single, spark_earley_single])