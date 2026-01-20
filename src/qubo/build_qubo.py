from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
from amplify import VariableGenerator, sum as a_sum

@dataclass
class QuboBuildResult:
    n: int
    x: Any                 # PolyArray[Dim2] of binary variables
    objective: Any         # Poly (quadratic)
    metadata: Dict[str, Any]


def _diag_cells_main(n: int, d: int) -> List[Tuple[int, int]]:
    """Main diagonal index by d = r - c (0-indexed r,c)"""
    cells = []
    for r in range(n):
        c = r - d
        if 0 <= c < n:
            cells.append((r, c))
    return cells


def _diag_cells_anti(n: int, s: int) -> List[Tuple[int, int]]:
    """Anti-diagonal index by s = r + c (0-indexed r,c)"""
    cells = []
    for r in range(n):
        c = s - r
        if 0 <= c < n:
            cells.append((r, c))
    return cells


def _pairwise_collision_penalty(x, cells: List[Tuple[int, int]]):
    """Sum_{i<j} x_i * x_j over the given set of cells (correctly encodes 'at most one' on that line)"""
    pen = 0
    L = len(cells)
    for i in range(L):
        r1, c1 = cells[i]
        for j in range(i + 1, L):
            r2, c2 = cells[j]
            pen += x[r1, c1] * x[r2, c2]
    return pen


def build_nqueens_qubo(
    n: int,
    w_row: float = 5.0,
    w_col: float = 5.0,
    w_diag: float = 1.0,
) -> QuboBuildResult:
    """Build a QUBO objective for N-Queens"""
    gen = VariableGenerator()
    x = gen.array("Binary", (n, n), name="x")

    # Row/col squared penalties (exactly 1)
    row_pen = 0
    for r in range(n):
        s = a_sum(x[r, :])
        row_pen += (s - 1) * (s - 1)

    col_pen = 0
    for c in range(n):
        s = a_sum(x[:, c])
        col_pen += (s - 1) * (s - 1)

    # Diagonal collision penalties (<= 1)
    diag_pen = 0

    # main diagonals: d = r - c ranges [-(n-1), +(n-1)]
    for d in range(-(n - 1), n):
        cells = _diag_cells_main(n, d)
        diag_pen += _pairwise_collision_penalty(x, cells)

    # anti diagonals: s = r + c ranges [0, 2n-2]
    for s in range(0, 2 * n - 1):
        cells = _diag_cells_anti(n, s)
        diag_pen += _pairwise_collision_penalty(x, cells)

    objective = w_row * row_pen + w_col * col_pen + w_diag * diag_pen

    return QuboBuildResult(
        n=n,
        x=x,
        objective=objective,
        metadata={"w_row": w_row, "w_col": w_col, "w_diag": w_diag},
    )