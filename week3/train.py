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

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parent.parent  # 조별 repo 최상위 폴더
DATA_PATH = ROOT / "WA_FnUseC_TelcoCustomerChurn.csv"
SPLIT_SEED = 42  # 데이터 분할 seed는 모든 실험에서 고정 (모델 seed와 분리)


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

    # 6. 학습 및 valid 평가
    model = build_model(args.model, params, args.seed, X_train)
    model.fit(X_train, y_train)

    valid_metrics = evaluate(model, X_valid, y_valid)
    print_metrics("valid", valid_metrics)


if __name__ == "__main__":
    main()
