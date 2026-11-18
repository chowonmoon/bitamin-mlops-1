from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI

if __package__:
    from .schema import CustomerInput
else:
    # cd week4 후 uvicorn main:app으로 실행하는 기존 실습 방식도 지원
    from schema import CustomerInput

MODEL_PATH = Path(__file__).resolve().with_name("churn_model.joblib")
model = joblib.load(MODEL_PATH)
app = FastAPI(title="BITAmin Week 5 — Churn API", version="1.0.0")


@app.get("/")
def root():
    return {"message": "ok"}


@app.post("/predict")
def predict(data: CustomerInput):
    features = pd.DataFrame([data.model_dump()])
    label = int(model.predict(features)[0])
    probability = float(model.predict_proba(features)[0][1])
    return {"churn": label, "churn_probability": probability}
