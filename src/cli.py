from __future__ import annotations

import argparse
from pathlib import Path

from src.config import PATHS
from src.experiments.run_all import run_suite
from src.experiments.summarize import summarize_results
from src.experiments.plot import plot_runtime, plot_success_rate, plot_failure_threshold


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    # run
    runp = sub.add_parser("run")
    runp.add_argument("--ns", nargs="+", type=int, required=True)
    runp.add_argument("--out", type=str, default=str(PATHS.results / "results.csv"))

    # summarize
    sump = sub.add_parser("summarize")
    sump.add_argument("--in", dest="inp", type=str, default=str(PATHS.results / "results.csv"))
    sump.add_argument("--out", type=str, default=str(PATHS.results / "summary.csv"))

    # plot
    plotp = sub.add_parser("plot")
    plotp.add_argument("--summary", type=str, default=str(PATHS.results / "summary.csv"))
    plotp.add_argument("--outdir", type=str, default=str(PATHS.results))

    args = parser.parse_args()

    if args.cmd == "run":
        df = run_suite(args.ns, Path(args.out))
        print(df)

    elif args.cmd == "summarize":
        df = summarize_results(Path(args.inp), Path(args.out))
        print(df)

    elif args.cmd == "plot":
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        plot_runtime(Path(args.summary), outdir / "runtime_vs_n.png")
        plot_success_rate(Path(args.summary), outdir / "valid_rate_vs_n.png")
        plot_failure_threshold(Path(args.summary), outdir / "failure_threshold.png")
        print(f"Wrote plots to: {outdir}")

if __name__ == "__main__":
    main()
