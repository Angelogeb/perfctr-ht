import os
import numpy as np
from scipy.stats import pearsonr

from functools import reduce
from pathlib import Path


def get_metrics_idxs(lines):
    res = []
    for i, line in enumerate(lines):
        if line.startswith("TABLE,Group") and "Metric," in line:
            how_many = int(line.strip(",\n").split(",")[-1])
            res.append((i + 2, i + 2 + how_many))
    return res


def get_running_time(file):
    with open(file) as f:
        for line in f:
            if line.startswith("Time"):
                return eval(line.split("\t")[-1].split(" ")[0])
    return 0

def get_first_metric(line):
    line = line.strip(",\n").split(",")
    return line[0], float(line[1] if line[1] != "-" else 0)

def get_metrics(f_name):
    with open(f_name) as f:
        lines = f.readlines()

    metrics_lines = map(
        get_first_metric,
        reduce(
            lambda a,b: a + b, 
            map(
                lambda e: lines[e[0]: e[1]],
                get_metrics_idxs(lines)
            )
        )
    )
    res = []
    distinct_metrics = set()
    metrics = []
    for metric, value in metrics_lines:
        if metric in distinct_metrics: continue
        metrics.append(metric)
        res.append(value)
        distinct_metrics.add(metric)

    run_time = get_running_time(f_name.with_suffix(".stdout"))
    return [run_time] + res, ["Run time"] + metrics

def build_name(pref, thread, ht, freq):
    ht = "-HT" if ht else ""
    return pref + str(thread) + ht + "-" + str(freq) + ".csv"


if __name__ == "__main__":
    res, met = get_metrics(Path("data_aggregated/FPU-core-1-HT-1.2.csv"))

    print(len(met))

    DIR = Path("data_aggregated/")
    OUT_DIR = Path("correlations/")

    benchs = [
        "ALU-mem-",
        "ALU-core-",
        "AVX-cache-",
        "Copy-mem-",
        "Copy-cache-",
        "FPU-mem-",
        "FPU-core-",
        "Scattered-mem-",
    ]

    thread_values = [1, 3, 6]
    freq_values = [1.2, 1.7, 2.2]

    for bench in benchs:
        # Pearson correlation wrt freq
        header = ",".join(["#Threads", "HT"] + met)
        out = open(OUT_DIR / (bench + "freq.csv"), "w")
        print(header, file=out)
        for ht in [False, True]:
            for thread in thread_values:
                vals = []
                for freq in freq_values:
                    f = DIR / build_name(bench, thread, ht, freq)
                    val, _ = get_metrics(f)
                    vals.append(val)

                vals = np.array(vals)
                corrs = []
                for metric in range(vals.shape[1]):
                    corrs.append(str(pearsonr(freq_values, vals[:, metric])[0]))
                line = ",".join([str(thread), str(ht)] + corrs)

                print(line, file=out)
        out.close()


        # Pearson correlation wrt thread
        header = ",".join(["Freq", "HT"] + met)
        out = open(OUT_DIR / (bench + "threads.csv"), "w")
        print(header, file=out)
        for ht in [False, True]:
            for freq in freq_values:
                vals = []
                for thread in thread_values:
                    f = DIR / build_name(bench, thread, ht, freq)
                    val, _ = get_metrics(f)
                    vals.append(val)

                vals = np.array(vals)
                corrs = []
                for metric in range(vals.shape[1]):
                    corrs.append(str(pearsonr(thread_values, vals[:, metric])[0]))
                line = ",".join([str(freq), str(ht)] + corrs)

                print(line, file=out)
        out.close()


        # Pearson correlation wrt HT
        header = ",".join(["Freq", "#Threads"] + met)
        out = open(OUT_DIR / (bench + "HT.csv"), "w")
        print(header, file=out)
        for thread in thread_values:
            for freq in freq_values:
                vals = []
                for ht in [False, True]:
                    f = DIR / build_name(bench, thread, ht, freq)
                    val, _ = get_metrics(f)
                    vals.append(val)

                vals = np.array(vals)
                corrs = []
                for metric in range(vals.shape[1]):
                    corrs.append(str(pearsonr([0, 1], vals[:, metric])[0]))
                line = ",".join([str(freq), str(thread)] + corrs)

                print(line, file=out)
        out.close()