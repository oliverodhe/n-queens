from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Paths:
    root: Path = Path(__file__).resolve().parents[1]
    models: Path = root / "models"
    data: Path = root / "data"
    instances: Path = data / "instances"
    results: Path = data / "results"

PATHS = Paths()