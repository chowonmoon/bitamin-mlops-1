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


---

## 복습과제 — 문초원 (C: Gradient Boosting)

- 브랜치: `feature/wandb-cw` (코드: `solution-final` 기준)
- W&B 프로젝트: [chowonmoon-dongduk-women-s-university / bitamin17-week3-churn](https://wandb.ai/chowonmoon-dongduk-women-s-university/bitamin17-week3-churn)
  - 조 W&B Team 초대 전이라 개인 계정에 기록 (`ENTITY = None`)
- 체크포인트 캡처 (CP2~CP5): [week3/images/review_moonchowon.pdf](week3/images/review_moonchowon.pdf)

### 실험 결과 (valid 기준)

| Run | valid ROC-AUC | valid Recall | gap (train−valid AUC) |
| --- | --- | --- | --- |
| RF 기본 (깊이 제한 없음) | 0.8374 | 0.4947 | **0.1624** (과적합) |
| GB lr 0.1 · 200 trees · depth 3 | 0.8576 | 0.5455 | 0.0474 |
| GB lr 0.05 · 300 trees · depth 3 | 0.8615 | 0.5508 | 0.0319 |
| GB lr 0.05 · 200 trees · depth 2 | 0.8694 | 0.5588 | −0.0123 |
| **GB lr 0.1 · 100 trees · depth 2** (GB 최고) | **0.8696** | 0.5561 | −0.0124 |
| RF depth 10 · leaf 10 (조 최종 모델) | 0.8702 | **0.8075** | 0.0200 |

### 해석

- GB는 트리 깊이를 3 → 2로 줄이자 과적합(gap)이 사라지고 valid AUC가 0.870까지 올랐다.
- 하지만 GB 최고 조건도 valid 이탈 고객 374명 중 **166명을 놓친다** (Recall 0.56). 같은 374명에서 조 최종 RF는 72명만 놓친다 (Recall 0.81).
- AUC는 비슷하지만 이탈 고객을 놓치지 않는 것이 더 중요하므로, **조 최종 모델(RF depth 10 · leaf 10) 선택이 타당하다.**

### 최종 모델 저장

- `python week3/train.py --model rf --max_depth 10 --min_samples_leaf 10 --save`
- test: ROC-AUC **0.8647** · Recall **0.8204** · Accuracy 0.7722
- `models/churn_model.joblib` (5.2MB) + W&B Artifact `churn-model:v0`
- Artifact digest `c1d607e58094a3751ff7c1bda22ba688`가 조원이 당일 저장한 모델과 **동일** → 다른 PC에서 재학습해도 같은 모델이 나옴을 확인 (재현성)
