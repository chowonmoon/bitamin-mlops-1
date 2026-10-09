# bitamin-mlops-1

비타민 26-2학기 MLOps 세션 1조 repository

고객 이탈(Telco Customer Churn) 예측 모델을 공통 프로젝트로, 개발환경 구축부터 협업, 실험 관리까지 주차별로 진행합니다.

| 주차 | 주제 | 기록 |
|---|---|---|
| 1주차 | 재현 가능한 ML 개발환경 (WSL · Conda · Docker) | [week1/README.md](week1/README.md) |
| 2주차 | Git / GitHub 기반 협업 | [week2/README.md](week2/README.md) |
| 3주차 | W&B 실험 관리 | [week3/README.md](week3/README.md) |

## 구조

```
├── app.py                  # 1~2주차 baseline 모델
├── week3/train.py          # 3주차 학습 스크립트 (W&B 기록)
├── requirements.txt
├── Dockerfile
├── WA_FnUseC_TelcoCustomerChurn.csv
└── week1/ · week2/ · week3/  # 주차별 기록
```

## 데이터셋

Telco Customer Churn (`WA_FnUseC_TelcoCustomerChurn.csv`)
- 7,043행 21열, 타깃 컬럼: `Churn`
- `TotalCharges` 컬럼의 공백 문자 결측치는 숫자 변환 후 처리
