import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 1. 데이터 로드
df = pd.read_csv("WA_FnUseC_TelcoCustomerChurn.csv")

# 2. 학습에 쓰지 않을 컬럼 제거
df = df.drop(columns=["customerID"])

# 3. TotalCharges 결측치 처리 (공백 문자를 숫자로 변환)
df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
df = df.dropna()

# 4. 범주형 변수 인코딩
categorical_cols = df.select_dtypes(include="object").columns
for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])

# 5. 입력(X)과 타깃(y) 분리
X = df.drop(columns=["Churn"])
y = df["Churn"]

# 6. 학습/테스트 데이터 분리
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 7. 모델 학습
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 8. 평가하기
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"Accuracy:  {acc:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1-score:  {f1:.4f}")
