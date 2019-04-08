import argparse

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def transform_xlabs(labs):
    return [str(e[0]) + "-" + str(e[1]) for e in labs]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Plot data")
    parser.add_argument("file", type=str, help="Path to the file with correlations")
    parser.add_argument("--pdf", action="store_true", default=False, help="Output pdf file instead of png")
    parser.add_argument("--out", type=str, default="out.png", help="Filename output")
    args = parser.parse_args()

    ext = ".png"
    if args.pdf:
        ext = ".pdf"

    f = Path(args.file)

    df = pd.read_csv(f)

    ylabs = df.columns[2:]
    xlabs = transform_xlabs(df[df.columns[:2]].values)

    plt.figure(figsize=(6, 20))
    sns.heatmap(df[df.columns[2:]].transpose(), xticklabels=xlabs, yticklabels=ylabs, linewidths=.5, cmap=sns.diverging_palette(220, 20, sep=20, as_cmap=True), square=True, cbar_kws={"shrink": 1, "aspect": 100})
    plt.title(f.with_suffix("").name + "\nPearson Correlation Coefficients", loc="right")
    plt.tight_layout()
    plt.savefig(Path(args.out).with_suffix(ext))