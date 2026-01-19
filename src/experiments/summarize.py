from __future__ import annotations
import pandas as pd

def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["approach","n"])
          .agg(time_s_mean=("time_s","mean"), ok_rate=("ok","mean"))
          .reset_index()
    )