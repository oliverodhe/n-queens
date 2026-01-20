from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from src.config import PATHS
from src.cp.run_minizinc import run_minizinc, write_dzn
from src.cp.parse_minizinc import parse_q_from_stdout, parse_board_from_stdout
from src.cp.logging import write_run_logs
from src.utils.validate import board_from_q, is_valid_positions, is_valid_board_x
from src.qubo.solve_amplify import solve_with_amplify

def run_suite(ns: List[int], out_csv: Path) -> pd.DataFrame:
    """Function to run experiments including parsing, validation, and logging"""
    PATHS.results.mkdir(parents=True, exist_ok=True)

    logs_dir = PATHS.results / "logs"
    dzn = PATHS.models / "nqueens.dzn"

    boolean_mzn = PATHS.models / "boolean_cp.mzn"
    int_mzn = PATHS.models / "integer_alldiff_cp.mzn"

    rows: List[Dict[str, Any]] = []

    for n in ns:
        write_dzn(dzn, n)

        # CP Boolean model (MiniZinc)
        r1 = run_minizinc(boolean_mzn, dzn, solver="gecode", timeout_s=60)
        x = parse_board_from_stdout(r1["stdout"], n=n) if r1["ok"] else None
        valid = is_valid_board_x(x) if x is not None else False

        parsed1 = {"solution_x": x, "valid": valid} if x is not None else {"solution_x": None, "valid": False}
        write_run_logs("cp_boolean", n, r1, parsed=parsed1, logs_directory=logs_dir)

        rows.append({
            "approach": "cp_boolean",
            "solver": "gecode",
            "n": n,
            "ok": r1["ok"],
            "valid": valid,
            "time_s": r1["time_s"],
            "returncode": r1["returncode"],
        })

        # CP Integer + alldifferent (MiniZinc)
        r2 = run_minizinc(int_mzn, dzn, solver="gecode", timeout_s=60)
        q = parse_q_from_stdout(r2["stdout"]) if r2["ok"] else None

        if q is not None:
            pos = board_from_q(q)
            valid2 = is_valid_positions(pos)
        else:
            valid2 = False

        parsed2 = {"q": q, "valid": valid2}
        write_run_logs("cp_integer_alldiff", n, r2, parsed=parsed2, logs_directory=logs_dir)

        rows.append({
            "approach": "cp_integer_alldiff",
            "solver": "gecode",
            "n": n,
            "ok": r2["ok"],
            "valid": valid2,
            "time_s": r2["time_s"],
            "returncode": r2["returncode"],
        })

        # QUBO Amplify (TODO: placeholder)
        r3 = solve_with_amplify(n=n, num_reads=50, timeout_s=5.0)
        rows.append({
            "approach": "qubo_amplify",
            "n": n,
            "ok": r3.get("ok", False),
            "valid": False,  # TODO: will update when decoding is implemented
            "time_s": r3.get("time_s"),
            "returncode": None,
        })

    df = pd.DataFrame(rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df
