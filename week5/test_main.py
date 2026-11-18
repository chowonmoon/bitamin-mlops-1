"""STEP 1: 가이드에 따라 세 개의 테스트를 완성하세요."""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from week4.main import app

client = TestClient(app)
SAMPLE = json.loads(Path(__file__).with_name("sample_request.json").read_text())


def test_root():
    pytest.fail("TODO: GET /의 상태 코드와 응답을 검증하세요 (week5/README.md STEP 1)")


def test_predict():
    pytest.fail("TODO: SAMPLE로 POST /predict를 요청하고 응답을 검증하세요")


def test_missing_required_field():
    pytest.fail("TODO: 필수값 tenure가 없는 요청이 422인지 검증하세요")
