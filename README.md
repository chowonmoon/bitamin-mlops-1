# bitamin-mlops-1

비타민 26-2학기 MLOps 세션 1조 repository

| 주차 | 주제 | 기록 |
|---|---|---|
| 1주차 | 재현 가능한 ML 개발환경 | 아래 README |
| 2주차 | Git / GitHub 기반 협업 | [week2/README.md](week2/README.md) |

---

# 1조 - 1주차 스냅샷 repository

재현 가능한 ML 개발환경 구축 (WSL/Conda/Docker)

## 실행 방법

### 1. 가상환경 생성 및 activate
conda create -n bitamin-mlops-1 python=3.10 -y
conda activate bitamin-mlops-1

### 2. 패키지 설치
pip install -r requirements.txt

### 3. baseline 모델 실행
python app.py

### 4. Docker 이미지 빌드 및 실행
docker build -t bitamin-mlops-1 .
docker run bitamin-mlops-1

---

## 체크포인트별 결과

### 체크포인트 1: conda 가상환경 생성 및 activate
**명령어**: `conda create -n bitamin-mlops-1 python=3.10 -y` / `conda activate bitamin-mlops-1`
**결과**: 프롬프트에 `(bitamin-mlops-1)` 환경명 표시 확인

### 체크포인트 2: requirements.txt 작성 후 설치
**명령어**: `pip install -r requirements.txt`
**결과**: pandas, scikit-learn, joblib 및 의존 패키지 정상 설치 확인 (`pip list`)

### 체크포인트 3: baseline 모델 실행
**명령어**: `python app.py`
**결과**: `Accuracy: 0.7854`

### 체크포인트 4: Dockerfile 작성 및 이미지 빌드
**명령어**: `docker build -t bitamin-mlops-1 .`
**결과**: `docker images`에 `bitamin-mlops-1:latest` (642MB) 표시 확인

### 체크포인트 5: 컨테이너에서 baseline 모델 실행
**명령어**: `docker run bitamin-mlops-1`
**결과**: `Accuracy: 0.7854` (conda 환경과 동일한 결과, 컨테이너 재현성 확인)

---

## 데이터셋
Telco Customer Churn (`WA_FnUseC_TelcoCustomerChurn.csv`)
- 7,043행 21열, 타깃 컬럼: `Churn`
- `TotalCharges` 컬럼에 공백 문자로 된 결측치가 있어 전처리 시 숫자 변환 및 결측치 제거 필요

---

## 심화 체크포인트

### 심화 1: 빌드한 이미지를 Docker Hub에 push
**명령어**: `docker tag bitamin-mlops-1 moonchowon/bitamin-mlops-1` / `docker push moonchowon/bitamin-mlops-1`
**결과**: Docker Hub에 `moonchowon/bitamin-mlops-1` 이미지 업로드 완료
**pull 방법**: `docker pull moonchowon/bitamin-mlops-1`

### 심화 2: .dockerignore 적용으로 이미지 용량 축소
**명령어**: `.dockerignore` 작성 후 `docker build -t bitamin-mlops-1-v2 .`
**결과**: 불필요 파일(캐시, git 관련 등) 제외 설정 반영
