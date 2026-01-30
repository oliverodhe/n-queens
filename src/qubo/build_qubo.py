from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
from amplify import VariableGenerator, sum as a_sum


@dataclass
class QuboBuildResult:
    n: int
    x: Any  # PolyArray[Dim2] of binary variables
    objective: Any  # the quadratic objective
    metadata: Dict[str, Any]

def diag_cells_main(n: int, d: int) -> List[Tuple[int, int]]:
    # main diagonal: d = r - c
    cells = []
    for r in range(n):
        c = r - d
        if 0 <= c < n:
            cells.append((r, c))
    return cells

def diag_cells_anti(n: int, s: int) -> List[Tuple[int, int]]:
    # anti diagonal: s = r + c
    out = []
    for r in range(n):
        c = s - r
        if 0 <= c < n:
            out.append((r, c))
    return out

def pairwise_collision_penalty(x, cells: List[Tuple[int, int]]):
    """at most one queen on this line -> sum of x_i*x_j for i<j"""
    pen = 0
    for i in range(len(cells)):
        r1, c1 = cells[i]
        for j in range(i + 1, len(cells)):
            r2, c2 = cells[j]
            pen += x[r1, c1] * x[r2, c2]
    return pen

def build_nqueens_qubo(
    n: int,
    w_row: float = 5.0,
    w_col: float = 5.0,
    w_diag: float = 1.0,
) -> QuboBuildResult:
    """Build QUBO for n-queens (binary matrix x, row/col/diag constraints)."""
    gen = VariableGenerator()
    x = gen.array("Binary", (n, n), name="x")

    # rows: exactly one per row -> (sum - 1)^2
    row_pen = 0
    for r in range(n):
        s = a_sum(x[r, :])
        row_pen += (s - 1) * (s - 1)

    # same for columns
    col_pen = 0
    for c in range(n):
        s = a_sum(x[:, c])
        col_pen += (s - 1) * (s - 1)

    # diagonals: at most one per diagonal (pairwise penalties)
    diag_pen = 0
    for d in range(-(n - 1), n):
        cells = diag_cells_main(n, d)
        diag_pen += pairwise_collision_penalty(x, cells)
    for s in range(0, 2 * n - 1):
        cells = diag_cells_anti(n, s)
        diag_pen += pairwise_collision_penalty(x, cells)

    objective = w_row * row_pen + w_col * col_pen + w_diag * diag_pen

    return QuboBuildResult(
        n=n,
        x=x,
        objective=objective,
        metadata={"w_row": w_row, "w_col": w_col, "w_diag": w_diag},
    )
