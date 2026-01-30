from __future__ import annotations
import os
from typing import Any, Dict, Optional, List
from amplify import AmplifyAEClient, solve
from src.utils.timing import timer
from src.utils.validate import is_valid_board_x
from src.qubo.build_qubo import build_nqueens_qubo


def to_int_matrix(x_eval: Any) -> List[List[int]]:
    if hasattr(x_eval, "tolist"):
        return [[int(v) for v in row] for row in x_eval.tolist()]
    return [[int(v) for v in row] for row in x_eval]


def solve_with_amplify(
    n: int,
    num_reads: int = 100,
    timeout_s: Optional[float] = 1.0,
    w_row: float = 5.0,
    w_col: float = 5.0,
    w_diag: float = 1.0,
) -> Dict[str, Any]:
    """
    Solve the N-Queens QUBO with Amplify Annealing Engine

    Based on: https://amplify.fixstars.com/en/docs/amplify/v1/quickstart.html

    Export the API token as an environment variable: `export AMPLIFY_AE_TOKEN=<token>`
    """
    token = os.getenv("AMPLIFY_AE_TOKEN")
    if not token:
        return {
            "ok": False,
            "n": n,
            "time_s": 0.0,
            "note": "Missing AMPLIFY_AE_TOKEN env var. Set your Amplify AE API token.",
            "solution_x": None,
            "valid": False,
            "energy": None,
            "success_rate": None,
        }

    build = build_nqueens_qubo(n=n, w_row=w_row, w_col=w_col, w_diag=w_diag)

    client = AmplifyAEClient()
    client.token = token

    # Time limit in ms
    if timeout_s is not None:
        client.parameters.time_limit_ms = int(timeout_s * 1000)

    try:
        client.parameters.num_reads = int(num_reads)
    except Exception:
        pass

    with timer() as t:
        result = solve(build.objective, client)
        elapsed = t()

    # Best solution
    best = result.best
    energy = float(best.objective)

    # Decode
    x_eval = build.x.evaluate(best.values)
    x_mat = to_int_matrix(x_eval)
    valid = is_valid_board_x(x_mat)

    # Success rate across returned solutions
    try:
        sols = list(result)
        if len(sols) > 0:
            valid_ct = 0
            for sol in sols:
                x_i = to_int_matrix(build.x.evaluate(sol.values))
                if is_valid_board_x(x_i):
                    valid_ct += 1
            success_rate = valid_ct / len(sols)
        else:
            success_rate = None
    except Exception:
        success_rate = None

    return {
        "ok": True,
        "n": n,
        "time_s": elapsed,
        "solution_x": x_mat,
        "valid": valid,
        "energy": energy,
        "success_rate": success_rate,
        "weights": build.metadata,
        "num_reads": num_reads,
        "timeout_s": timeout_s,
    }
    