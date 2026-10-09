# 3주차 — W&B 실험 관리 실습

2주차까지 만든 고객 이탈(churn) 예측 코드에 W&B 기록을 직접 추가하고, 조원 4명이 한 W&B 프로젝트에 실험을 모아 비교한 뒤 최종 모델을 `churn_model.joblib`과 W&B Artifact로 남깁니다.

## 출발 코드

| 파일 | 내용 |
| --- | --- |
| `week3/train.py` | 2주차 app.py를 정리한 학습 스크립트. 모델 1개를 원하는 조건으로 학습하고 valid 지표를 출력 (W&B 코드 없음) |
| `week3/requirements.txt` | 3주차 패키지 버전 (사전 세팅에서 설치한 `wandb==0.30.0` 포함) |

```bash
python week3/train.py                                   # Random Forest (2주차 설정)
python week3/train.py --model logreg --C 0.1
python week3/train.py --model rf --max_depth 6
python week3/train.py --model gb --learning_rate 0.05 --n_estimators 300
```

## 역할

| 담당 | 실험 모델 | 주로 바꿔 볼 하이퍼파라미터 |
| --- | --- | --- |
| A | Logistic Regression (`--model logreg`) | `--C`, `--class_weight` |
| B | Random Forest (`--model rf`) | `--max_depth`, `--min_samples_leaf` |
| C | Gradient Boosting (`--model gb`) | `--learning_rate`, `--n_estimators`, `--max_depth` |
| D | 평가·비교 (모델 자유) | 선택 기준(지표) 정리, 최종 모델 결정 |

## 체크포인트 (필수)

| 번호 | 내용 | 통과 확인 화면 |
| --- | --- | --- |
| 1 | 조별 W&B Team 생성 및 조원 초대 | Team 멤버 목록에 조원 전원 |
| 2 | 조원 전원이 첫 W&B run 기록 | 조 프로젝트 Runs 목록에 조원 수만큼 run |
| 3 | 조 전체 6개 이상 실험 비교 | 지표로 정렬한 Runs 표 + 비교 차트 |
| 4 | 평가 그래프 기록 | 혼동행렬 · ROC 곡선 패널 |
| 5 | 최종 모델 저장 | `models/churn_model.joblib` 저장 + `churn-model` Artifact 화면 |

## 막혔을 때

정답 코드는 `solution` 브랜치에 단계별 태그(`solution-step1` ~ `solution-step4`, `solution-final`)로 있습니다.

```bash
git remote add week3 https://github.com/0jin03/bitamin-mlops-week3-snapshot.git   # 한 번만 (대표자는 이미 추가됨)
git fetch week3 --tags
git restore --source solution-step2 week3/train.py   # 예: STEP 2까지 끝난 코드로 바꾸기 (바꾼 뒤 ENTITY 다시 수정)
git diff solution-step1 solution-step2               # STEP 1 → 2에서 바뀐 부분 보기
```

API Key는 코드·README·커밋에 넣지 않습니다. `wandb login`으로만 인증합니다.


---

## 복습과제 — 문초원 (C: Gradient Boosting)

- 브랜치: `feature/wandb-cw` (코드: `solution-final` 기준)
- W&B 프로젝트: [chowonmoon-dongduk-women-s-university / bitamin17-week3-churn](https://wandb.ai/chowonmoon-dongduk-women-s-university/bitamin17-week3-churn)
  - 조 W&B Team 초대 전이라 개인 계정에 기록 (`ENTITY = None`)
- 체크포인트 캡처 (CP2~CP5): [images/review_moonchowon.pdf](images/review_moonchowon.pdf)

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
