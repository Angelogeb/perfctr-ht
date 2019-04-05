import argparse

import matplotlib.pyplot as plt

from pathlib import Path


def get_group_name_and_id(line):
    l = line.split(",")
    return l[2], int(l[1].split()[1])

def get_groups(file):
    with open(file) as f:
        lines = f.readlines()
        table_lines = get_line_indices_starting_with(lines, "TABLE")
        return sorted(set([get_group_name_and_id(lines[i]) for i in table_lines]), key=lambda t: t[1])

def get_line_indices_starting_with(lines, string):
    indices = []
    for i, l in enumerate(lines):
        l = l.strip()
        if l.startswith(string):
            indices.append(i)
    return indices

def get_group_lines(file, group):
    with open(file) as f:
        lines = f.readlines()
        groups_indices = get_line_indices_starting_with(lines, "STRUCT")
        
        if group == len(groups_indices) - 1:
            return lines[groups_indices[group] + 1:]
        else:
            return lines[groups_indices[group] + 1 : groups_indices[group + 1]]

def get_table_lines(group_lines):
    table_indices = get_line_indices_starting_with(group_lines, "TABLE")
    index = 2 if len(table_indices) == 4 else 1
    if index == len(table_indices) - 1:
        return group_lines[table_indices[index] + 1 : ]
    else:
        return group_lines[table_indices[index] + 1 : table_indices[index + 1]]

aggregations = {
    "sum": sum,
    "min": min,
    "max": max,
    "avg": lambda a: sum(a) / len(a),
    "any": lambda a: a[0]
}

def get_field(table_lines, field, type):
    fields = table_lines[0].strip(",\n").split(",")
    core_idxs = get_line_indices_starting_with(fields, "Core")
    line = table_lines[get_line_indices_starting_with(table_lines, field)[0]]
    line = line.strip(",\n").split(",")
    vals = [float(line[i]) for i in core_idxs]
    return aggregations[type](vals)

def get_running_time(file):
    with open(file) as f:
        for line in f:
            if line.startswith("Time"):
                return eval(line.split("\t")[-1].split(" ")[0])
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot data")
    parser.add_argument("file", type=str, nargs='+', help="Path to the file without extension")
    parser.add_argument("-g", "--group", type=int, default=1)
    parser.add_argument("-m", "--metric", type=str)
    parser.add_argument("-t", "--type", type=str, default=None)
    parser.add_argument("-p", "--print-groups", action="store_true")
    parser.add_argument("-c", "--core", default=0)
    args = parser.parse_args()

    if args.print_groups:
        groups = get_groups(args.file[0])
        for g in groups:
            print(str(g[1]) + ":" + g[0])
        exit(0)

    if args.group and not args.type:
        print("".join(get_group_lines(args.file[0], args.group - 1)))
        exit(0)

    fields = []
    for file in args.file:
        table = get_table_lines(get_group_lines(file, args.group - 1))
        field = get_field(table, args.metric, args.type)
        fields.append(field)


    x = list(range(len(args.file)))
    
    fig, ax1 = plt.subplots()
    plt.sca(ax1)
    plt.bar(x, height=fields, color=[plt.get_cmap("tab20")((i*2 if i
        < 10 else i*2 + 1) % 20 ) for i in range(len(args.file))])
    plt.xticks(x,[Path(file).with_suffix("").name for file in args.file],
            rotation=70)
    plt.ylabel(args.metric)

    times = []
    for f in args.file:
        times.append(get_running_time(Path(f).with_suffix(".stdout")))

    ax1.set_ylim(ymin=0)
    ax2 = ax1.twinx()
    ax2.scatter(x, times, marker='x', color="#000000")
    ax2.set_ylabel("x Running time [s]")
    ax2.set_ylim(ymin=0)
    plt.show()
