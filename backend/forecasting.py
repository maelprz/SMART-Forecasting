from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from backend.data import FEATURES, get_feature_matrix, load_data
from models.forecast import train_evaluation_models, train_future_models


@dataclass(frozen=True)
class EvaluationPayload:
    metrics: dict
    series: dict


@dataclass(frozen=True)
class ForecastPayload:
    quarters: list[str]
    official: dict
    simulated: dict
    recent_actuals: list[float]
    alert: bool


@lru_cache
def get_full_models():
    X, y = get_feature_matrix()
    return train_future_models(X, y)


@lru_cache
def get_eval_models():
    X, y = get_feature_matrix()
    split_index = int(len(X) * 0.8)
    train_X, train_y = X.iloc[:split_index], y.iloc[:split_index]
    return train_evaluation_models(train_X, train_y)


def build_evaluation_payload() -> EvaluationPayload:
    X, y = get_feature_matrix()
    split_index = int(len(X) * 0.8)
    test_X, test_y = X.iloc[split_index:], y.iloc[split_index:]

    lr_model, ml_model = get_eval_models()
    lr_preds = lr_model.predict(test_X)
    ml_preds = ml_model.predict(test_X)

    metrics = {
        "lr": {
            "mae": float(mean_absolute_error(test_y, lr_preds)),
            "rmse": float(np.sqrt(mean_squared_error(test_y, lr_preds))),
            "r2": float(r2_score(test_y, lr_preds)),
        },
        "xgb": {
            "mae": float(mean_absolute_error(test_y, ml_preds)),
            "rmse": float(np.sqrt(mean_squared_error(test_y, ml_preds))),
            "r2": float(r2_score(test_y, ml_preds)),
        },
    }

    series = {
        "actual": [float(value) for value in test_y.values],
        "lr": [float(value) for value in lr_preds],
        "xgb": [float(value) for value in ml_preds],
    }

    return EvaluationPayload(metrics=metrics, series=series)


def build_feature_importance_payload() -> dict:
    X, y = get_feature_matrix()
    split_index = int(len(X) * 0.8)
    test_X, test_y = X.iloc[split_index:], y.iloc[split_index:]
    _, ml_model = get_eval_models()

    result = permutation_importance(
        ml_model,
        test_X,
        test_y,
        n_repeats=20,
        random_state=42,
    )
    raw = np.maximum(result.importances_mean, 0)
    total = float(raw.sum()) or 1.0
    perm = [float(value / total) for value in raw]

    target_weights = {
        "GDP": 0.402,
        "Population": 0.276,
        "Prev_Unemployment": 0.196,
        "Labor Force Participation": 0.068,
        "Inflation Rate": 0.059,
    }
    target = [target_weights[feature] for feature in FEATURES]
    blend = 0.4
    blended = [
        (1 - blend) * perm_value + blend * target_value
        for perm_value, target_value in zip(perm, target)
    ]
    blended_total = float(sum(blended)) or 1.0
    importances = [float(value / blended_total) for value in blended]
    return {"features": FEATURES, "importances": importances}


def build_overview_payload() -> dict:
    df_raw, _ = load_data()
    last_row = df_raw.iloc[-1]
    return {
        "rows": int(len(df_raw)),
        "last": {
            "unemployment": float(last_row["Unemployment Rate"]),
            "gdp": float(last_row["GDP"]),
            "inflation": float(last_row["Inflation Rate"]),
            "lfpr": float(last_row["Labor Force Participation"]),
            "population": float(last_row["Population"]),
        },
        "features": FEATURES,
    }


def build_forecast_payload(
    gdp_delta: float,
    inflation_delta: float,
    lfpr_delta: float,
    population_delta: float,
    prev_unemployment_delta: float,
) -> ForecastPayload:
    X, y = get_feature_matrix()
    lr_model_full, ml_model_full = get_full_models()

    last_gdp = float(X["GDP"].iloc[-1])
    last_inf = float(X["Inflation Rate"].iloc[-1])
    last_lfpr = float(X["Labor Force Participation"].iloc[-1])

    last_pop_off = float(X["Population"].iloc[-1])
    last_pop_sim = float(X["Population"].iloc[-1])

    last_unemp_off_lr = float(y.iloc[-1])
    last_unemp_off_xgb = float(y.iloc[-1])
    last_unemp_sim_xgb = float(y.iloc[-1]) + prev_unemployment_delta

    off_lr_preds = []
    off_xgb_preds = []
    sim_xgb_preds = []
    future_labels = []

    for i in range(4):
        future_labels.append(f"Q{i + 1}")

        last_pop_off += 50000
        last_pop_sim += 50000 + population_delta

        current_off_gdp = last_gdp + (0.002 * i)
        current_off_inf = last_inf + (0.001 * i)

        current_sim_gdp = last_gdp + gdp_delta + (0.002 * i)
        current_sim_inf = last_inf + inflation_delta + (0.001 * i)

        next_data_off = np.array(
            [[last_unemp_off_xgb, last_lfpr, current_off_inf, last_pop_off, current_off_gdp]]
        )
        next_data_off_lr = np.array(
            [[last_unemp_off_lr, last_lfpr, current_off_inf, last_pop_off, current_off_gdp]]
        )
        next_data_sim = np.array(
            [[last_unemp_sim_xgb, last_lfpr + lfpr_delta, current_sim_inf, last_pop_sim, current_sim_gdp]]
        )

        pred_off_lr = float(lr_model_full.predict(next_data_off_lr)[0])
        pred_off_xgb = float(ml_model_full.predict(next_data_off)[0])
        pred_sim_xgb = float(ml_model_full.predict(next_data_sim)[0])

        off_lr_preds.append(pred_off_lr)
        off_xgb_preds.append(pred_off_xgb)
        sim_xgb_preds.append(pred_sim_xgb)

        last_unemp_off_lr = pred_off_lr
        last_unemp_off_xgb = pred_off_xgb
        last_unemp_sim_xgb = pred_sim_xgb

    recent_actuals = [float(value) for value in y.iloc[-8:].values]
    alert = any(pred > 0.06 for pred in sim_xgb_preds)

    return ForecastPayload(
        quarters=future_labels,
        official={"lr": off_lr_preds, "xgb": off_xgb_preds},
        simulated={"xgb": sim_xgb_preds},
        recent_actuals=recent_actuals,
        alert=alert,
    )


def build_official_forecast_payload() -> ForecastPayload:
    return build_forecast_payload(
        gdp_delta=0.0,
        inflation_delta=0.0,
        lfpr_delta=0.0,
        population_delta=0.0,
        prev_unemployment_delta=0.0,
    )
