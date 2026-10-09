"""
3주차 W&B 실습 출발 코드 (아직 W&B 기록 없음)

2주차에 완성한 app.py(전처리 Pipeline + Logistic Regression + Random Forest + 평가 지표)를
"모델 1개를 원하는 조건으로 학습하는 스크립트"로 정리했습니다.
3주차 실습에서는 이 파일에 W&B 코드를 직접 추가합니다.

실행 (저장소 최상위 폴더에서):
    python week3/train.py                                  # 기본: Random Forest
    python week3/train.py --model logreg --C 0.1
    python week3/train.py --model rf --max_depth 6
    python week3/train.py --model gb --learning_rate 0.05 --n_estimators 300
"""
import argparse
from pathlib import Path

import joblib  # [STEP 4]
import pandas as pd
import wandb  # [STEP 1]
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, log_loss, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent.parent  # 조별 repo 최상위 폴더
DATA_PATH = ROOT / "WA_FnUseC_TelcoCustomerChurn.csv"
MODEL_PATH = ROOT / "models" / "churn_model.joblib"  # [STEP 4] models/는 .gitignore 대상
SPLIT_SEED = 42  # 데이터 분할 seed는 모든 실험에서 고정 (모델 seed와 분리)

# [STEP 1] W&B 기록 위치 — 조원 모두 같은 값을 사용
ENTITY = None  # 조별 W&B Team 이름 (예: "bitamin17-mlops-3"), Team이 없으면 None → 개인 계정
PROJECT = "bitamin17-week3-churn"


# 1. 실행 인자: 코드를 고치지 않고 실험 조건만 바꿔서 실행
def parse_args():
    p = argparse.ArgumentParser(description="Telco churn 모델 1개 학습")
    p.add_argument("--model", choices=["logreg", "rf", "gb"], default="rf")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--class_weight", choices=["none", "balanced"], default="balanced")  # logreg, rf
    p.add_argument("--C", type=float, default=1.0)                    # logreg: 규제 강도의 역수
    p.add_argument("--n_estimators", type=int, default=200)           # rf, gb: 트리 개수
    p.add_argument("--max_depth", type=int, default=None)             # rf: 기본 제한 없음 / gb: 기본 3
    p.add_argument("--min_samples_leaf", type=int, default=1)         # rf: 잎 노드 최소 샘플 수
    p.add_argument("--learning_rate", type=float, default=0.1)        # gb: 학습률
    p.add_argument("--save", action="store_true")                     # [STEP 4] 최종 모델 저장
    return p.parse_args()


# 2. 데이터 로드 + train / valid / test = 60 / 20 / 20 분할
#    test는 2주차와 같은 분할(test_size=0.2, random_state=42)
#    valid: 실험끼리 비교할 때 사용 / test: 최종 모델 1개만 마지막에 평가
def load_splits():
    df = pd.read_csv(DATA_PATH)
    df = df.drop(columns=["customerID"])
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")  # 공백 → NaN
    X = df.drop(columns=["Churn"])
    y = (df["Churn"] == "Yes").astype(int)  # 1 = 이탈(churn), 0 = 유지

    X_trval, X_test, y_trval, y_test = train_test_split(X, y, test_size=0.2, random_state=SPLIT_SEED)
    X_train, X_valid, y_train, y_valid = train_test_split(
        X_trval, y_trval, test_size=0.25, stratify=y_trval, random_state=SPLIT_SEED
    )
    return X_train, X_valid, X_test, y_train, y_valid, y_test


# 3. 전처리 (2주차와 동일): 수치형 = 중앙값 대체 + 스케일링 / 범주형 = 최빈값 대체 + 원-핫
def build_preprocessor(X):
    numeric_cols = X.select_dtypes(include=["int64", "float64"]).columns
    categorical_cols = X.select_dtypes(include=["object"]).columns
    numeric_transformer = Pipeline(
        steps=[("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]
    )
    categorical_transformer = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )


# 4. 모델별로 실제 사용하는 하이퍼파라미터만 골라냄 (W&B config에 기록할 값)
def get_params(args):
    class_weight = None if args.class_weight == "none" else args.class_weight
    if args.model == "logreg":
        return {"C": args.C, "class_weight": class_weight}
    if args.model == "rf":
        return {
            "n_estimators": args.n_estimators,
            "max_depth": args.max_depth,  # None = 제한 없음
            "min_samples_leaf": args.min_samples_leaf,
            "class_weight": class_weight,
        }
    return {  # gb
        "n_estimators": args.n_estimators,
        "learning_rate": args.learning_rate,
        "max_depth": args.max_depth or 3,
    }


def build_model(model_name, params, seed, X):
    if model_name == "logreg":
        classifier = LogisticRegression(max_iter=1000, random_state=seed, **params)
    elif model_name == "rf":
        classifier = RandomForestClassifier(random_state=seed, n_jobs=-1, **params)
    else:
        classifier = GradientBoostingClassifier(random_state=seed, **params)
    return Pipeline(steps=[("preprocessor", build_preprocessor(X)), ("classifier", classifier)])


# 5. 평가 지표 (2주차 evaluation-metrics)
def evaluate(model, X, y):
    pred = model.predict(X)
    proba = model.predict_proba(X)[:, 1]
    return {
        "accuracy": accuracy_score(y, pred),
        "precision": precision_score(y, pred, zero_division=0),
        "recall": recall_score(y, pred),
        "f1": f1_score(y, pred),
        "roc_auc": roc_auc_score(y, proba),
    }


def make_run_name(model_name, params):
    """실험 이름 예: rf-n_estimators200-max_depth6-min_samples_leaf1-class_weightbalanced"""
    return model_name + "-" + "-".join(f"{k}{v}" for k, v in params.items())


def print_metrics(title, metrics):
    print(f"[{title}] " + "  ".join(f"{k}={v:.4f}" for k, v in metrics.items()))


def main():
    args = parse_args()
    X_train, X_valid, X_test, y_train, y_valid, y_test = load_splits()
    params = get_params(args)
    print(f"model={args.model} seed={args.seed} params={params}")

    # [STEP 1] run 시작: 어떤 조건으로 실험했는지(config) 기록
    run = wandb.init(
        entity=ENTITY,
        project=PROJECT,
        name=make_run_name(args.model, params),
        group=args.model,  # [STEP 2] 모델 종류별로 묶어 보기
        config={"model": args.model, "seed": args.seed, **params},
    )

    # 6. 학습 및 valid 평가
    model = build_model(args.model, params, args.seed, X_train)
    model.fit(X_train, y_train)

    train_metrics = evaluate(model, X_train, y_train)  # [STEP 2] 과적합 확인용
    valid_metrics = evaluate(model, X_valid, y_valid)
    print_metrics("train", train_metrics)
    print_metrics("valid", valid_metrics)

    # [STEP 1] 결과 기록 후 run 종료
    # [STEP 2] train 지표와 과적합 정도(gap = train AUC - valid AUC)도 함께 기록
    run.log({
        **{f"train/{k}": v for k, v in train_metrics.items()},
        **{f"valid/{k}": v for k, v in valid_metrics.items()},
        "gap/roc_auc": train_metrics["roc_auc"] - valid_metrics["roc_auc"],
    })

    # [STEP 3] 평가 그래프 기록: 혼동행렬 + ROC 곡선 (valid 기준)
    valid_pred = model.predict(X_valid)
    valid_proba = model.predict_proba(X_valid)
    run.log({
        "plots/confusion_matrix": wandb.plot.confusion_matrix(
            y_true=y_valid.tolist(), preds=valid_pred.tolist(), class_names=["stay", "churn"]
        ),
        "plots/roc_curve": wandb.plot.roc_curve(
            y_valid.tolist(), valid_proba.tolist(), labels=["stay", "churn"], classes_to_plot=[1]
        ),
    })

    # [심화] GB 학습 곡선: 트리를 하나씩 더할 때마다 valid log-loss 기록 → 과적합 시작 지점 확인
    if args.model == "gb":
        run.define_metric("curve/*", step_metric="n_trees")
        Xt = model.named_steps["preprocessor"].transform(X_train)
        Xv = model.named_steps["preprocessor"].transform(X_valid)
        gb = model.named_steps["classifier"]
        for n_trees, (pt, pv) in enumerate(zip(gb.staged_predict_proba(Xt), gb.staged_predict_proba(Xv)), start=1):
            if n_trees % 5 == 0:
                run.log({
                    "n_trees": n_trees,
                    "curve/train_logloss": log_loss(y_train, pt[:, 1]),
                    "curve/valid_logloss": log_loss(y_valid, pv[:, 1]),
                })

    # [STEP 4] 최종 모델 저장: train+valid 전체로 다시 학습 → test로 한 번만 평가 → 파일 저장 + W&B Artifact
    if args.save:
        final_model = build_model(args.model, params, args.seed, X_train)
        final_model.fit(pd.concat([X_train, X_valid]), pd.concat([y_train, y_valid]))
        test_metrics = evaluate(final_model, X_test, y_test)
        print_metrics("test", test_metrics)
        run.log({f"test/{k}": v for k, v in test_metrics.items()})

        MODEL_PATH.parent.mkdir(exist_ok=True)
        joblib.dump(final_model, MODEL_PATH)
        print(f"saved: {MODEL_PATH.relative_to(ROOT)}")

        artifact = wandb.Artifact("churn-model", type="model", metadata={"model": args.model, **params})
        artifact.add_file(str(MODEL_PATH))
        run.log_artifact(artifact)

    run.finish()


if __name__ == "__main__":
    main()
