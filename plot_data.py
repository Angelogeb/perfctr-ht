import argparse

import matplotlib.pyplot as plt

from pathlib import Path

GROUP_STRINGS = [
    "UOPS_RETIRE",
    "L3",
    "DATA",
    "FLOPS_AVX",
    "L2CACHE",
    "CYCLE_ACTIVITY",
    "TLB_INSTR",
    "MEM",
    "MEM_DP",
    "FLOPS_DP",
    "UOPS",
    "TLB_DATA",
    "CLOCK",
    "L2",
    "MEM_SP",
    "ENERGY",
    "ICACHE",
    "BRANCH",
    "RECOVERY",
    "DIVIDE",
    "UOPS_EXEC",
    "L3CACHE",
    "FLOPS_SP",
    "FALSE_SHARE",
    "TMA",
    "UOPS_ISSUE",
    "CYCLE_STALLS"
]


START_HEADER = 46


def get_values(file_name, group, index):
    res = []
    with open(file_name) as f:
        for line in f:
            line = line.strip().split(" ")
            if line[0] != str(group): continue
            n_cores = int(line[2])
            vals = []
            for i in range(1):
                val = line[4 + n_cores * index + i]
                if val == '-': val = 0
                vals.append(float(val))
            res.append(sum(vals) / len(vals))
    return res


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Plot data")
    parser.add_argument("file", type=str, nargs='+', help="Path to the file without extension")
    parser.add_argument("-g", "--group", type=int, default=0)
    parser.add_argument("-m", "--metric", type=str)
    parser.add_argument("-p", "--print-groups", action="store_true")
    args = parser.parse_args()

    if args.print_groups:
        print("\n".join([str(i+1) + ":" + s for i,s in enumerate(GROUP_STRINGS)]))
        exit(0)

    with open(args.file[0] + ".header") as f:
        header = f.readlines()

    group_metrics = header[args.group].strip()[START_HEADER:]

    if not args.metric:
        print(group_metrics.replace("|", "\n"))
        exit(0)

    group_metrics = group_metrics.split("|")
    
    metric_index = group_metrics.index(args.metric)

    timelines = [
        get_values(f + ".stderr", args.group, metric_index)
        for f in args.file
    ]

    for t, f in zip(timelines, args.file):
        plt.plot(t, label=Path(f).name)

    plt.ylabel(args.metric)
    plt.legend()
    plt.show()