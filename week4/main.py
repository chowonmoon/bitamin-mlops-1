import joblib
import pandas as pd
from fastapi import FastAPI

from schema import CustomerInput

# 서버 시작 시 1번만 로드 (요청마다 로드하지 않음)
model = joblib.load("churn_model.joblib")
print("model loaded:", type(model))

app = FastAPI(title="Telco Churn Prediction API")


@app.get("/")
def root():
    return {"message": "ok"}


@app.post("/predict")
def predict(data: CustomerInput):
    # 입력을 학습 때와 같은 컬럼 구조의 1행 DataFrame으로 변환
    X = pd.DataFrame([data.model_dump()])
    label = int(model.predict(X)[0])
    proba = float(model.predict_proba(X)[0][1])
    return {"churn": label, "churn_probability": round(proba, 4)}