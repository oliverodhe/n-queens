from __future__ import annotations
from typing import List, Tuple, Optional

def board_from_q(q: List[int]) -> List[Tuple[int,int]]:
    # q[r] = col (1-indexed), r is 1-indexed
    return [(r+1, q[r]) for r in range(len(q))]

def is_valid_positions(pos: List[Tuple[int,int]]) -> bool:
    rows = [r for r, _ in pos]
    cols = [c for _, c in pos]
    if len(set(rows)) != len(rows): return False
    if len(set(cols)) != len(cols): return False

    diag1 = [r - c for r, c in pos]
    diag2 = [r + c for r, c in pos]
    if len(set(diag1)) != len(diag1): return False
    if len(set(diag2)) != len(diag2): return False
    return True

def is_valid_board_x(x: List[List[int]]) -> bool:
    n = len(x)
    pos = []
    for r in range(n):
        for c in range(n):
            if x[r][c] == 1:
                pos.append((r+1, c+1))
    return len(pos) == n and is_valid_positions(pos)