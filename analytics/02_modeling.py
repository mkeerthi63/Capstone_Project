import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from imblearn.over_sampling import SMOTE
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    auc,
    classification_report,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier, plot_tree
df = pd.read_csv("titanic.csv")
X = df.drop(columns=["survived"])
y = df["survived"]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
num_features = ["age", "fare", "sibsp", "parch"]
cat_features = ["sex", "embarked", "pclass"]
num_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)
cat_transformer = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ]
)
preprocessor = ColumnTransformer(
    transformers=[
        ("num", num_transformer, num_features),
        ("cat", cat_transformer, cat_features),
    ]
)
X_train_prep = preprocessor.fit_transform(X_train)
X_test_prep = preprocessor.transform(X_test)
ohe_cols = (
    preprocessor.named_transformers_["cat"]
    .named_steps["encoder"]
    .get_feature_names_out(cat_features)
)
all_feature_names = num_features + list(ohe_cols)
models = {
    "Logistic Regression": LogisticRegression(random_state=42),
    "Decision Tree": DecisionTreeClassifier(max_depth=4, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42),
}
results = {}
plt.figure(figsize=(8, 6))
for name, clf in models.items():
    clf.fit(X_train_prep, y_train)
    y_pred = clf.predict(X_test_prep)
    y_proba = (
        clf.predict_proba(X_test_prep)[:, 1]
        if hasattr(clf, "predict_proba")
        else y_pred
    )
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    roc_auc = auc(fpr, tpr)
    results[name] = {
        "Accuracy": acc,
        "Precision": prec,
        "Recall": rec,
        "F1 Score": f1,
        "ROC AUC": roc_auc,
        "CM": confusion_matrix(y_test, y_pred),
    }
    plt.plot(fpr, tpr, label=f"{name} (AUC = {roc_auc:.2f})")
plt.plot([0, 1], [0, 1], "k--")
plt.title("ROC Curves Comparison")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.legend()
plt.tight_layout()
plt.savefig("roc_curves.png")
plt.close()
plt.figure(figsize=(16, 8))
plot_tree(
    models["Decision Tree"],
    feature_names=all_feature_names,
    class_names=["Died", "Survived"],
    filled=True,
    fontsize=8,
)
plt.title("Decision Tree Visualization")
plt.tight_layout()
plt.savefig("decision_tree.png")
plt.close()
print("=== CLASS IMBALANCE COMPARISON (Random Forest) ===")
rf_base = RandomForestClassifier(random_state=42).fit(X_train_prep, y_train)
y_pred_base = rf_base.predict(X_test_prep)
rf_bal = RandomForestClassifier(class_weight="balanced", random_state=42).fit(
    X_train_prep, y_train
)
y_pred_bal = rf_bal.predict(X_test_prep)
smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train_prep, y_train)
rf_smote = RandomForestClassifier(random_state=42).fit(
    X_train_smote, y_train_smote
)
y_pred_smote = rf_smote.predict(X_test_prep)
imbalance_summary = pd.DataFrame(
    [
        {
            "Variant": "Baseline",
            "Precision": precision_score(y_test, y_pred_base),
            "Recall": recall_score(y_test, y_pred_base),
            "F1 Score": f1_score(y_test, y_pred_base),
        },
        {
            "Variant": "Class Weight Balanced",
            "Precision": precision_score(y_test, y_pred_bal),
            "Recall": recall_score(y_test, y_pred_bal),
            "F1 Score": f1_score(y_test, y_pred_bal),
        },
        {
            "Variant": "SMOTE (Train Fold Only)",
            "Precision": precision_score(y_test, y_pred_smote),
            "Recall": recall_score(y_test, y_pred_smote),
            "F1 Score": f1_score(y_test, y_pred_smote),
        },
    ]
)
print(imbalance_summary.to_string(index=False))
# TASK 10: Hyperparameter Tuning (GridSearchCV) & OOB Score
rf_oob = RandomForestClassifier(oob_score=True, random_state=42)
param_grid = {
    "n_estimators": [50, 100, 150],
    "max_depth": [4, 6, 8, None],
    "max_features": ["sqrt", "log2"],
}
grid_search = GridSearchCV(
    estimator=rf_oob, param_grid=param_grid, cv=5, scoring="f1", n_jobs=-1
)
grid_search.fit(X_train_prep, y_train)
best_rf = grid_search.best_estimator_
print("\n=== GRIDSEARCHCV RANDOM FOREST RESULTS ===")
print("Best Parameters:", grid_search.best_params_)
print(f"OOB Score (Out-Of-Bag): {best_rf.oob_score_:.4f}")
# TASK 11: Multivariate Linear Regression Side-Task (Predicting Fare)
X_reg = df.drop(columns=["fare", "pclass_facing", "deck"], errors="ignore")
y_reg = df["fare"]
num_reg = ["age", "sibsp", "parch"]
cat_reg = ["sex", "embarked", "class"]
reg_preprocessor = ColumnTransformer(
    transformers=[
        (
            "num",
            Pipeline(
                [
                    ("imp", SimpleImputer(strategy="median")),
                    ("scl", StandardScaler()),
                ]
            ),
            num_reg,
        ),
        (
            "cat",
            Pipeline(
                [
                    ("imp", SimpleImputer(strategy="most_frequent")),
                    ("enc", OneHotEncoder(drop="first")),
                ]
            ),
            cat_reg,
        ),
    ]
)
X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
    X_reg, y_reg, test_size=0.20, random_state=42
)
X_reg_tr_prep = reg_preprocessor.fit_transform(X_reg_train)
X_reg_te_prep = reg_preprocessor.transform(X_reg_test)
lin_reg = LinearRegression()
lin_reg.fit(X_reg_tr_prep, y_reg_train)
y_reg_pred = lin_reg.predict(X_reg_te_prep)

mae = mean_absolute_error(y_reg_test, y_reg_pred)
rmse = np.sqrt(mean_squared_error(y_reg_test, y_reg_pred))
r2 = r2_score(y_reg_test, y_reg_pred)
n = len(y_reg_test)
p = X_reg_tr_prep.shape[1]
adj_r2 = 1 - (1 - r2) * (n - 1) / (n - p - 1)
print("=== MULTIVARIATE LINEAR REGRESSION METRICS (Target: Fare) ===")
print(f"MAE: {mae:.2f} | RMSE: {rmse:.2f} | R²: {r2:.4f} | Adjusted R²: {adj_r2:.4f}")
residuals = y_reg_test - y_reg_pred
plt.figure(figsize=(7, 5))
plt.scatter(y_reg_pred, residuals, alpha=0.5, color="purple")
plt.axhline(0, color="red", linestyle="--")
plt.title("Regression Residual Plot (Target: Fare)")
plt.xlabel("Predicted Fare")
plt.ylabel("Residuals (Actual - Predicted)")
plt.tight_layout()
plt.savefig("residual_plot.png")
plt.close()
# TASK 12 & 13: Export Full End-to-End Pipeline & Verification
full_pipeline = Pipeline(
    steps=[("preprocessor", preprocessor), ("classifier", best_rf)]
)
full_pipeline.fit(X_train, y_train)
joblib.dump(full_pipeline, "full_pipeline.joblib")
print("Full end-to-end pipeline saved successfully to 'full_pipeline.joblib'.")
loaded_pipeline = joblib.load("full_pipeline.joblib")
raw_sample = X_test.iloc[:3]
predictions = loaded_pipeline.predict(raw_sample)
print("Reloaded Pipeline Verification on Raw Input Samples:")
print("Predicted Classes:", predictions)
