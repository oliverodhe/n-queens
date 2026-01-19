from __future__ import annotations
import argparse
from pathlib import Path

from src.experiments.run_all import run_suite
from src.config import PATHS

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    runp = sub.add_parser("run")
    runp.add_argument("--ns", nargs="+", type=int, required=True)
    runp.add_argument("--out", type=str, default=str(PATHS.results / "results.csv"))

    args = parser.parse_args()

    if args.cmd == "run":
        df = run_suite(args.ns, Path(args.out))
        print(df)

if __name__ == "__main__":
    main()