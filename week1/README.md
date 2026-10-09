# 1주차 — 재현 가능한 ML 개발환경 구축

WSL · Conda · Docker로 누구의 PC에서도 같은 결과가 나오는 개발환경을 구성합니다.

## 실행 방법

```bash
# 1. 가상환경 생성 및 activate
conda create -n bitamin-mlops-1 python=3.10 -y
conda activate bitamin-mlops-1

# 2. 패키지 설치
pip install -r requirements.txt

# 3. baseline 모델 실행
python app.py

# 4. Docker 이미지 빌드 및 실행
docker build -t bitamin-mlops-1 .
docker run bitamin-mlops-1
```

## 체크포인트별 결과

| 번호 | 내용 | 명령어 | 결과 |
|---|---|---|---|
| 1 | conda 가상환경 생성 및 activate | `conda create -n bitamin-mlops-1 python=3.10 -y` | 프롬프트에 `(bitamin-mlops-1)` 표시 |
| 2 | requirements.txt 작성 후 설치 | `pip install -r requirements.txt` | pandas, scikit-learn, joblib 정상 설치 (`pip list`) |
| 3 | baseline 모델 실행 | `python app.py` | `Accuracy: 0.7854` |
| 4 | Dockerfile 작성 및 이미지 빌드 | `docker build -t bitamin-mlops-1 .` | `bitamin-mlops-1:latest` (642MB) 생성 |
| 5 | 컨테이너에서 baseline 실행 | `docker run bitamin-mlops-1` | `Accuracy: 0.7854` — conda 환경과 동일 (재현성 확인) |

## 심화

| 번호 | 내용 | 결과 |
|---|---|---|
| 1 | Docker Hub에 이미지 push | `moonchowon/bitamin-mlops-1` 업로드 완료 (`docker pull moonchowon/bitamin-mlops-1`) |
| 2 | `.dockerignore` 적용 | 캐시·git 관련 파일 제외 후 `bitamin-mlops-1-v2` 빌드 |
