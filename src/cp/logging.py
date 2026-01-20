from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, Optional
import json
from src.config import PATHS

def write_run_logs(
    approach: str,
    n: int,
    run: Dict[str, Any],
    logs_directory: Path = PATHS.results / "logs",
    parsed: Optional[Dict[str, Any]] = None,
) -> None:
    """Logging helper function for MiniZinc runs"""

    logs_directory.mkdir(parents=True, exist_ok=True)

    log_file = logs_directory / f"{approach}_{n}"
    (log_file.with_suffix(".out")).write_text(run.get("stdout", ""), encoding="utf-8")
    (log_file.with_suffix(".err")).write_text(run.get("stderr", ""), encoding="utf-8")

    # Meta data + parsed solution
    meta = {
        "approach": approach,
        "n": n,
        "ok": run.get("ok"),
        "returncode": run.get("returncode"),
        "time_s": run.get("time_s"),
        "cmd": run.get("cmd"),
        "parsed": parsed,
    }
    (log_file.with_suffix(".json")).write_text(json.dumps(meta, indent=2), encoding="utf-8")
