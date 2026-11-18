"""실행 중인 API에 실제 HTTP 요청을 보내 모델 추론을 확인합니다."""
import json
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


def main():
    base = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000").rstrip("/")
    for attempt in range(60):
        try:
            with urlopen(base + "/", timeout=3) as response:
                assert json.load(response) == {"message": "ok"}
            break
        except (URLError, TimeoutError, ConnectionError):
            if attempt == 59:
                raise
            time.sleep(1)
    payload = Path(__file__).with_name("sample_request.json").read_bytes()
    request = Request(base + "/predict", data=payload, headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=15) as response:
        result = json.load(response)
    assert set(result) == {"churn", "churn_probability"}, result
    assert type(result["churn"]) is int and result["churn"] in (0, 1), result
    assert 0 <= result["churn_probability"] <= 1, result
    print("PASS: / and /predict (real model inference)", json.dumps(result))


if __name__ == "__main__":
    main()
