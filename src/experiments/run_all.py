from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

from src.config import PATHS
from src.cp.run_minizinc import run_minizinc, write_dzn
from src.qubo.solve_amplify import solve_with_amplify

def run_suite(ns: List[int], out_csv: Path) -> pd.DataFrame:
    PATHS.results.mkdir(parents=True, exist_ok=True)

    rows: List[Dict[str, Any]] = []
    dzn = PATHS.models / "nqueens.dzn"

    boolean_mzn = PATHS.models / "boolean_cp.mzn"
    int_mzn = PATHS.models / "integer_alldiff_cp.mzn"

    for n in ns:
        write_dzn(dzn, n)

        # CP Boolean model
        r1 = run_minizinc(boolean_mzn, dzn, solver=None, timeout_s=60)
        rows.append({"approach": "cp_boolean", "n": n, **{k: r1[k] for k in ["ok","time_s","returncode"]}})

        # CP Integer baseline
        r2 = run_minizinc(int_mzn, dzn, solver=None, timeout_s=60)
        rows.append({"approach": "cp_integer_alldiff", "n": n, **{k: r2[k] for k in ["ok","time_s","returncode"]}})

        # QUBO Amplify
        r3 = solve_with_amplify(n=n, num_reads=50, timeout_s=5.0)
        rows.append({"approach": "qubo_amplify", "n": n, **{k: r3.get(k) for k in ["ok","time_s"]}})

    df = pd.DataFrame(rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df