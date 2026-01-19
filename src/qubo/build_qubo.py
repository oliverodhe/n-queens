from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class QuboBuildResult:
    n: int
    # store amplify model objects here later (BinaryPoly, etc.)
    model: Any = None
    metadata: Dict[str, Any] = None

def build_nqueens_qubo(n: int, w_row: float = 1.0, w_col: float = 1.0, w_diag: float = 1.0) -> QuboBuildResult:
    """
    TODO:
    - Create binary variables x[r,c] in Amplify
    - Add penalties:
        row: sum_r (sum_c x[r,c] - 1)^2
        col: sum_c (sum_r x[r,c] - 1)^2
        diag constraints (choose squared sums or pairwise collisions)
    - Return Amplify model ready for solve
    """
    return QuboBuildResult(n=n, model=None, metadata={"w_row": w_row, "w_col": w_col, "w_diag": w_diag})