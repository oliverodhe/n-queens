from __future__ import annotations
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from src.utils.timing import timer
from src.utils.io import write_text

def write_dzn(dzn_path: Path, n: int) -> None:
    write_text(dzn_path, f"n = {n};\n")

def run_minizinc(
    model_path: Path,
    dzn_path: Path,
    solver: Optional[str] = "gecode",
    timeout_s: Optional[int] = None,
) -> Dict[str, Any]:
    cmd = ["minizinc"]
    if solver:
        cmd += ["--solver", solver]
    if timeout_s is not None:
        cmd += ["--time-limit", str(int(timeout_s * 1000))]  # ms
    cmd += [str(model_path), str(dzn_path)]

    with timer() as t:
        proc = subprocess.run(cmd, capture_output=True, text=True)
        elapsed = t()

    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "time_s": elapsed,
        "cmd": " ".join(cmd),
    }