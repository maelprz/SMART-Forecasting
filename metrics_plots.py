import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from sklearn.metrics import mean_squared_error, r2_score

from models.forecast import train_evaluation_models


def load_data():
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / "data" / "dataset.csv"

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

    df["Prev_Unemployment"] = df["Unemployment Rate"].shift(1)

    df_ml = df.dropna(
        subset=[
            "Prev_Unemployment",
            "GDP",
            "Inflation Rate",
            "Labor Force Participation",
            "Population",
        ]
    ).copy()
    return df_ml


def save_rmse_bar(baseline_value, model_value, filename):
    labels = ["Linear Regression\n(Baseline)", "XGBoost\n(Smart Forecast)"]
    values = [baseline_value, model_value]
    colors = ["#7f7f7f", "#0072B2"]

    plt.figure(figsize=(8, 5), dpi=150)
    bars = plt.bar(labels, values, color=colors, edgecolor="black")
    plt.title("Root Mean Squared Error (RMSE)", fontsize=14, fontweight="bold")
    plt.ylabel("Error Rate (Lower is Better)", fontsize=11, fontweight="bold")
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for bar, val in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{val:.4%}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.subplots_adjust(bottom=0.2, top=0.88)
    plt.savefig(filename, transparent=False)
    plt.close()


def save_r2_bar(baseline_value, model_value, filename):
    labels = ["Linear Regression", "XGBoost"]
    values = [float(baseline_value), float(model_value)]
    colors = ["#7f7f7f", "#0072B2"]

    plt.figure(figsize=(6, 4), dpi=150)
    bars = plt.bar(labels, values, color=colors, edgecolor="black")
    plt.title("R2 Score", fontsize=14, fontweight="bold")
    plt.ylabel("Score (Higher is Better)", fontsize=11, fontweight="bold")
    plt.grid(axis="y", linestyle="--", alpha=0.6)

    for bar, val in zip(bars, values):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            val + 0.02,
            f"{val:.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
        )

    plt.subplots_adjust(bottom=0.2, top=0.88)
    plt.savefig(filename, transparent=False)
    plt.close()


def main():
    df_ml = load_data()

    features = [
        "Prev_Unemployment",
        "Labor Force Participation",
        "Inflation Rate",
        "Population",
        "GDP",
    ]
    X = df_ml[features]
    y = df_ml["Unemployment Rate"]

    split_index = int(len(X) * 0.8)
    train_X, test_X = X.iloc[:split_index], X.iloc[split_index:]
    train_y, test_y = y.iloc[:split_index], y.iloc[split_index:]

    lr_model, xgb_model = train_evaluation_models(train_X, train_y)

    lr_preds = lr_model.predict(test_X)
    xgb_preds = xgb_model.predict(test_X)

    rmse_lr = np.sqrt(mean_squared_error(test_y, lr_preds))
    rmse_xgb = np.sqrt(mean_squared_error(test_y, xgb_preds))

    r2_lr = r2_score(test_y, lr_preds)
    r2_xgb = r2_score(test_y, xgb_preds)

    out_dir = Path(__file__).resolve().parent / "assets"
    out_dir.mkdir(parents=True, exist_ok=True)

    save_rmse_bar(rmse_lr, rmse_xgb, out_dir / "rmse_comparison.png")
    save_r2_bar(r2_lr, r2_xgb, out_dir / "r2_comparison.png")


if __name__ == "__main__":
    main()
