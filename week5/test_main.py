"""STEP 1: 가이드에 따라 세 개의 테스트를 완성하세요."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from week4.main import app

client = TestClient(app)
SAMPLE = json.loads(Path(__file__).with_name("sample_request.json").read_text())


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


def test_predict():
    response = client.post("/predict", json=SAMPLE)
    assert response.status_code == 200
    result = response.json()
    assert set(result) == {"churn", "churn_probability"}
    assert type(result["churn"]) is int
    assert result["churn"] in (0, 1)
    assert 0 <= result["churn_probability"] <= 1


def test_missing_required_field():
    payload = SAMPLE.copy()
    payload.pop("tenure")
    response = client.post("/predict", json=payload)
    assert response.status_code == 422
    assert any(
        e["loc"] == ["body", "tenure"]
        for e in response.json()["detail"]
    )
