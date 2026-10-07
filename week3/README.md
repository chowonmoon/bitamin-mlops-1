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
