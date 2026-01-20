from __future__ import annotations

import re
from typing import List, Optional

_Q_RE = re.compile(r"\bq\s*=\s*\[(.*?)\]", re.DOTALL)

def parse_q_from_stdout(stdout: str) -> Optional[List[int]]:
    """Function to parse queen columns (q=[1,3,4,...]) from MiniZinc stdout"""
    m = _Q_RE.search(stdout)
    if not m:
        return None
    inner = m.group(1).strip()
    if not inner:
        return None
    parts = [p.strip() for p in inner.split(",")]

    try:
        return [int(p) for p in parts if p != ""]
    except ValueError:
        return None

def parse_board_from_stdout(stdout: str, n: int):
    """Function to parse the 'board=' section from boolean_cp.mzn stdout"""
    idx = stdout.find("board=")
    if idx == -1:
        return None

    after = stdout[idx:]
    lines = after.splitlines()
    start = None

    for i, line in enumerate(lines):
        if "board=" in line:
            start = i + 1
            break

    if start is None:
        return None

    board_lines = [ln.strip() for ln in lines[start:] if ln.strip() != ""]
    if len(board_lines) < n:
        return None

    board_lines = board_lines[:n]
    x: List[List[int]] = []

    for ln in board_lines:
        tokens = [t for t in ln.split() if t]
        if len(tokens) != n:
            return None
        row = [1 if t.upper() == "Q" else 0 for t in tokens]
        x.append(row)

    return x
