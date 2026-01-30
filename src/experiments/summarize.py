from __future__ import annotations

from pathlib import Path
import pandas as pd


def _to_numeric_safe(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def summarize_results(raw_csv: Path, out_csv: Path) -> pd.DataFrame:
    """Reads raw results (long format) and outputs grouped summary by (approach, n)"""
    df = pd.read_csv(raw_csv)

    # Normalize dtypes
    if df["ok"].dtype == object:
        df["ok"] = df["ok"].astype(str).str.lower().isin(["true", "1", "yes"])
    if df["valid"].dtype == object:
        df["valid"] = df["valid"].astype(str).str.lower().isin(["true", "1", "yes"])

    df["time_s"] = _to_numeric_safe(df["time_s"])
    if "energy" in df.columns:
        df["energy"] = _to_numeric_safe(df["energy"])

    def p90(x: pd.Series) -> float:
        x = x.dropna()
        if len(x) == 0:
            return float("nan")
        return float(x.quantile(0.90))

    summary = (
        df.groupby(["approach", "solver", "n"], dropna=False)
          .agg(
              runs=("valid", "count"),
              ok_rate=("ok", "mean"),
              valid_rate=("valid", "mean"),
              time_mean=("time_s", "mean"),
              time_median=("time_s", "median"),
              time_p90=("time_s", p90),
              energy_min=("energy", "min") if "energy" in df.columns else ("time_s", "size"),
              energy_median=("energy", "median") if "energy" in df.columns else ("time_s", "size"),
          )
          .reset_index()
    )

    # If energy columns were faked when missing, remove them
    if "energy" not in df.columns:
        summary = summary.drop(columns=["energy_min", "energy_median"], errors="ignore")

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_csv, index=False)
    return summary
