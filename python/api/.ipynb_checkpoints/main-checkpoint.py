import os
import dagshub
import mlflow
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

dagshub.init(repo_owner='sfisher2277', repo_name='Intelligent-Demand-Forecasting', mlflow=True)

app = FastAPI(title="Rossmann Demand Forecasting API")

RUN_ID = os.getenv("MLFLOW_RUN_ID")
model = None


class PredictionRequest(BaseModel):
    Store: int
    DayOfWeek: int
    Open: int
    Promo: int
    SchoolHoliday: int
    CompetitionDistance: float
    CompetitionOpenSinceMonth: float
    CompetitionOpenSinceYear: float
    Promo2: int
    Promo2SinceWeek: float
    Promo2SinceYear: float
    Sales_lag_1: float
    Sales_lag_7: float
    StoreType: str    # one of "a", "b", "c", "d"
    Assortment: str   # one of "a", "b", "c"
    IsHoliday: int


def load_model():
    """
    Load a trained model from MLflow using the run_id set in MLFLOW_RUN_ID.
    """
    if RUN_ID is None:
        raise RuntimeError("MLFLOW_RUN_ID environment variable is not set.")
    return mlflow.sklearn.load_model(f"runs:/{RUN_ID}/model")


def encode_request(request: PredictionRequest) -> pd.DataFrame:
    """
    Turn a single PredictionRequest into a one-row DataFrame matching
    the model's training feature layout.
    """
    data = request.dict()
    store_type = data.pop("StoreType")
    assortment = data.pop("Assortment")

    for cat in ["a", "b", "c", "d"]:
        data[f"StoreType_{cat}"] = int(store_type == cat)

    for cat in ["a", "b", "c"]:
        data[f"Assortment_{cat}"] = int(assortment == cat)

    return pd.DataFrame([data])


@app.on_event("startup")
def startup_event():
    global model
    model = load_model()


@app.post("/predict")
def predict(request: PredictionRequest):
    X = encode_request(request)
    X = X[model.feature_names_in_]  # match training column order exactly
    prediction = model.predict(X)[0]
    return {"predicted_sales": float(prediction)}