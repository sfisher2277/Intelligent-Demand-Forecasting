import os
import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Rossmann Demand Forecasting API")

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "model.pkl")
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
    StoreType: str
    Assortment: str
    IsHoliday: int


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise RuntimeError(
            f"No model found at {MODEL_PATH}. Run train.py first to create one."
        )
    return joblib.load(MODEL_PATH)


def encode_request(request: PredictionRequest) -> pd.DataFrame:
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
    X = X[model.feature_names_in_]
    prediction = model.predict(X)[0]
    return {"predicted_sales": float(prediction)}