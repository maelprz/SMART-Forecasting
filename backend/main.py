from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.forecasting import (
    build_evaluation_payload,
    build_feature_importance_payload,
    build_forecast_payload,
    build_official_forecast_payload,
    build_overview_payload,
)

app = FastAPI(title="SMART Forecasting API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SimulatorInput(BaseModel):
    gdp_delta: float = Field(..., description="Delta applied to latest GDP growth")
    inflation_delta: float = Field(..., description="Delta applied to latest inflation rate")
    lfpr_delta: float = Field(..., description="Delta applied to latest labor force participation")
    population_delta: float = Field(..., description="Delta applied to latest population per quarter")
    prev_unemployment_delta: float = Field(
        ..., description="Delta applied to latest unemployment rate seed"
    )


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/overview")
def get_overview():
    try:
        return build_overview_payload()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/api/evaluation")
def get_evaluation():
    return build_evaluation_payload().__dict__


@app.get("/api/feature-importance")
def get_feature_importance():
    return build_feature_importance_payload()


@app.get("/api/forecast")
def get_forecast():
    return build_official_forecast_payload().__dict__


@app.post("/api/simulate")
def simulate_forecast(payload: SimulatorInput):
    return build_forecast_payload(
        gdp_delta=payload.gdp_delta,
        inflation_delta=payload.inflation_delta,
        lfpr_delta=payload.lfpr_delta,
        population_delta=payload.population_delta,
        prev_unemployment_delta=payload.prev_unemployment_delta,
    ).__dict__
