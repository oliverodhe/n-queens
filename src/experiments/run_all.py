from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Optional

import pandas as pd

from src.config import PATHS
from src.cp.run_minizinc import run_minizinc, write_dzn
from src.cp.parse_minizinc import parse_q_from_stdout, parse_board_from_stdout
from src.cp.logging import write_run_logs
from src.utils.validate import board_from_q, is_valid_positions, is_valid_board_x
from src.qubo.solve_amplify import solve_with_amplify


def run_suite(
    ns: List[int],
    out_csv: Path,
    *,
    cp_timeout_s: int = 60,
    solver_cp: str = "gecode",
    # QUBO settings
    qubo_trials: int = 10,
    qubo_num_reads: int = 100,
    qubo_timeout_s: float = 1.0,
    w_row: float = 5.0,
    w_col: float = 5.0,
    w_diag: float = 1.0,
) -> pd.DataFrame:
    """
    Function to run all experiments until failure.
    
    A model fails at N if:
    - CP: no valid solution within time limit
    - QUBO: valid_rate < 1.0 over trials
    """
    PATHS.results.mkdir(parents=True, exist_ok=True)

    logs_dir = PATHS.results / "logs"
    dzn = PATHS.models / "nqueens.dzn"

    boolean_mzn = PATHS.models / "boolean_cp.mzn"
    int_mzn = PATHS.models / "integer_alldiff_cp.mzn"

    rows: List[Dict[str, Any]] = []
    
    # Track which models have failed
    failed = {
        "cp_boolean": False,
        "cp_integer": False,
        "qubo": False,
    }

    total_ns = len(ns)
    print(f"Starting experiment suite with {total_ns} N values: {ns[0]} to {ns[-1]}")
    print("-" * 60)

    for idx, n in enumerate(ns, start=1):
        progress_pct = (idx / total_ns) * 100
        print(f"\n[{progress_pct:.1f}%] Processing N={n} ({idx}/{total_ns})")
        write_dzn(dzn, n)

        # CP Boolean model
        if not failed["cp_boolean"]:
            print("  Running cp_boolean...", end=" ", flush=True)
            r1 = run_minizinc(boolean_mzn, dzn, solver=solver_cp, timeout_s=cp_timeout_s)
            x = parse_board_from_stdout(r1["stdout"], n=n) if r1["ok"] else None
            valid = is_valid_board_x(x) if x is not None else False

            parsed1 = {"solution_x": x, "valid": valid} if x is not None else {"solution_x": None, "valid": False}
            write_run_logs("cp_boolean", n, r1, parsed=parsed1, logs_directory=logs_dir)

            rows.append({
                "approach": "cp_boolean",
                "solver": solver_cp,
                "n": n,
                "trial": 0,
                "ok": bool(r1["ok"]),
                "valid": bool(valid),
                "time_s": float(r1["time_s"]),
                "returncode": r1["returncode"],
                # keep schema aligned across approaches
                "energy": None,
                "success_rate": None,
                "num_reads": None,
                "timeout_s": cp_timeout_s,
                "w_row": None,
                "w_col": None,
                "w_diag": None,
            })
            
            if not valid:
                failed["cp_boolean"] = True
                print("FAILED")
            else:
                print("OK")
        else:
            print("  cp_boolean: SKIPPED (already failed)")

        # CP Integer + alldifferent
        if not failed["cp_integer"]:
            print("  Running cp_integer...", end=" ", flush=True)
            r2 = run_minizinc(int_mzn, dzn, solver=solver_cp, timeout_s=cp_timeout_s)
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
                "solver": solver_cp,
                "n": n,
                "trial": 0,
                "ok": bool(r2["ok"]),
                "valid": bool(valid2),
                "time_s": float(r2["time_s"]),
                "returncode": r2["returncode"],
                "energy": None,
                "success_rate": None,
                "num_reads": None,
                "timeout_s": cp_timeout_s,
                "w_row": None,
                "w_col": None,
                "w_diag": None,
            })
            
            if not valid2:
                failed["cp_integer"] = True
                print("FAILED")
            else:
                print("OK")
        else:
            print("  cp_integer: SKIPPED (already failed)")

        # QUBO Amplify
        if not failed["qubo"]:
            print(f"  Running qubo ({qubo_trials} trials)...", end=" ", flush=True)
            qubo_valid_count = 0
            for trial in range(int(qubo_trials)):
                r3 = solve_with_amplify(
                    n=n,
                    num_reads=qubo_num_reads,
                    timeout_s=qubo_timeout_s,
                    w_row=w_row,
                    w_col=w_col,
                    w_diag=w_diag,
                )

                is_valid_trial = bool(r3.get("valid", False))
                if is_valid_trial:
                    qubo_valid_count += 1

                rows.append({
                    "approach": "qubo_amplify",
                    "solver": "amplify_ae",
                    "n": n,
                    "trial": trial,
                    "ok": bool(r3.get("ok", False)),
                    "valid": is_valid_trial,
                    "time_s": r3.get("time_s"),
                    "returncode": None,
                    "energy": r3.get("energy"),
                    "success_rate": r3.get("success_rate"),
                    "num_reads": r3.get("num_reads", qubo_num_reads),
                    "timeout_s": r3.get("timeout_s", qubo_timeout_s),
                    "w_row": (r3.get("weights") or {}).get("w_row", w_row),
                    "w_col": (r3.get("weights") or {}).get("w_col", w_col),
                    "w_diag": (r3.get("weights") or {}).get("w_diag", w_diag),
                })
            
            # Calculate valid_rate and check if QUBO failed
            valid_rate = qubo_valid_count / qubo_trials if qubo_trials > 0 else 0.0
            if valid_rate < 1.0:
                failed["qubo"] = True
                print(f"FAILED (valid_rate={valid_rate:.2%})")
            else:
                print(f"OK (valid_rate={valid_rate:.2%})")
        else:
            print("  qubo: SKIPPED (already failed)")

        # If all models have failed, break early
        if all(failed.values()):
            print(f"\nAll models have failed. Stopping at N={n} ({idx}/{total_ns})")
            break

    print("\n" + "=" * 60)
    print(f"Experiment suite completed!")
    print(f"  Processed {idx}/{total_ns} N values")
    print(f"  Results: {len(rows)} total rows")
    print(f"  Output: {out_csv}")
    print("=" * 60)

    df = pd.DataFrame(rows)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return df
