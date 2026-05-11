from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd

FEATURES = [
    "Prev_Unemployment",
    "Labor Force Participation",
    "Inflation Rate",
    "Population",
    "GDP",
]
TARGET = "Unemployment Rate"


@lru_cache
def load_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    base_dir = Path(__file__).resolve().parent.parent
    data_candidates = [
        base_dir / "data" / "dataset.csv",
        base_dir / "dataset.csv",
        base_dir / "dataset.xlsx - NCR.csv",
    ]

    data_path = next((path for path in data_candidates if path.exists()), None)
    if data_path is None:
        raise FileNotFoundError(
            "Could not find dataset. Expected data/dataset.csv, dataset.csv, or dataset.xlsx - NCR.csv"
        )

    df = pd.read_csv(data_path)

    df["Population"] = (
        df["Population"]
        .astype(str)
        .replace([",", " "], "", regex=True)
        .replace("nan", np.nan)
    )
    df["Population"] = pd.to_numeric(df["Population"], errors="coerce").ffill()
    df["Labor Force Participation"] = pd.to_numeric(
        df["Labor Force Participation"], errors="coerce"
    ).ffill()

    df["Prev_Unemployment"] = df[TARGET].shift(1)

    df_ml = df.dropna(
        subset=["Prev_Unemployment", "GDP", "Inflation Rate", "Labor Force Participation", "Population"]
    ).copy()
    return df, df_ml


def get_feature_matrix() -> tuple[pd.DataFrame, pd.Series]:
    _, df_ml = load_data()
    X = df_ml[FEATURES]
    y = df_ml[TARGET]
    return X, y
