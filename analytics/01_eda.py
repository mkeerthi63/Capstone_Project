import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
# TASK 1: Load Dataset & Save Offline Fallback
try:
    df = sns.load_dataset("titanic")
    print("Successfully loaded dataset via sns.load_dataset()")
except Exception as e:
    print(f"Network/Cache load failed ({e}). Loading offline titanic.csv fallback...")
    df = pd.read_csv("titanic.csv")
df.to_csv("titanic.csv", index=False)
print("Shape:", df.shape)
df.info()
print(df.describe(include="all"))
missing_pct = (df.isnull().sum() / len(df)) * 100
missing_affected = missing_pct[missing_pct > 0]
print("\n--- Missing Value Percentages (Affected Columns) ---")
print(missing_affected.apply(lambda x: f"{x:.2f}%"))
# TASK 2: Missing Value Handling Strategy
df_clean = df.copy()
df_clean = df_clean.dropna(subset=["embarked", "embark_town"])
median_age = df_clean["age"].median()
df_clean["age"] = df_clean["age"].fillna(median_age)
df_clean["deck"] = df_clean["deck"].astype(str).replace("nan", "Unknown")
print(f"\nCleaned Dataset Shape after dropping <5% missing rows: {df_clean.shape}")
# TASK 3: Univariate Analysis (Age & Fare)
def check_outliers_iqr(series, name):
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = series[(series < lower_bound) | (series > upper_bound)]
    print(f"{name} Outliers (IQR Rule): {len(outliers)} rows outside [{lower_bound:.2f}, {upper_bound:.2f}]")
    return outliers
print("=== UNIVARIATE ANALYSIS ===")
check_outliers_iqr(df_clean["age"], "Age")
check_outliers_iqr(df_clean["fare"], "Fare")
fare_mean = df_clean["fare"].mean()
fare_median = df_clean["fare"].median()
fare_mode = df_clean["fare"].mode()[0]
print(f"\nFare Central Tendency: Mean={fare_mean:.2f}, Median={fare_median:.2f}, Mode={fare_mode:.2f}")
print("Conclusion: Fare distribution is RIGHT-SKEWED (Mean > Median > Mode).")
fig, axes = plt.subplots(2, 2, figsize=(12, 8))
sns.histplot(df_clean["age"], kde=True, ax=axes[0, 0]).set_title("Age Histogram")
sns.boxplot(x=df_clean["age"], ax=axes[0, 1]).set_title("Age Boxplot")
sns.histplot(df_clean["fare"], kde=True, ax=axes[1, 0]).set_title(
    "Fare Histogram"
)
sns.boxplot(x=df_clean["fare"], ax=axes[1, 1]).set_title("Fare Boxplot")
plt.tight_layout()
plt.savefig("univariate_analysis.png")
plt.close()
# TASK 4: Bivariate Analysis & Correlation Matrix
print("=== BIVARIATE SURVIVAL RATES ===")
print(f"(a) Sex:\n{df_clean.groupby('sex')['survived'].mean().apply(lambda x: f'{x:.2%}')}\n")
print(f"(b) Pclass:\n{df_clean.groupby('pclass')['survived'].mean().apply(lambda x: f'{x:.2%}')}\n")
print(f"(c) Sex & Pclass:\n{df_clean.groupby(['sex', 'pclass'])['survived'].mean().apply(lambda x: f'{x:.2%}')}\n")
corr_cols = ["survived", "pclass", "age", "sibsp", "parch", "fare"]
corr_matrix = df_clean[corr_cols].corr()
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("6x6 Numeric Feature Correlation Matrix")
plt.tight_layout()
plt.savefig("correlation_matrix.png")
plt.close()
abs_corr = corr_matrix.abs()
np.fill_diagonal(abs_corr.values, 0)
top_pairs = abs_corr.unstack().sort_values(ascending=False).drop_duplicates()
print("Top 2 Strongest Off-Diagonal Correlations:")
for idx, val in top_pairs.head(2).items():
    actual_val = corr_matrix.loc[idx[0], idx[1]]
    print(f"  - {idx[0]} & {idx[1]}: {actual_val:.4f}")
# TASK 5: Exploratory Z-Score Standardization Check
df_zcheck = df_clean.copy()
df_zcheck["age_z"] = (
    df_zcheck["age"] - df_zcheck["age"].mean()
) / df_zcheck["age"].std()
df_zcheck["fare_z"] = (
    df_zcheck["fare"] - df_zcheck["fare"].mean()
) / df_zcheck["fare"].std()
print("=== EXPLORATORY STANDARDIZATION SANITY CHECK ===")
print(f"Age Original    -> Mean: {df_clean['age'].mean():.2f}, Std: {df_clean['age'].std():.2f}")
print(f"Age Z-Standard  -> Mean: {df_zcheck['age_z'].mean():.4f}, Std: {df_zcheck['age_z'].std():.4f}")
print(f"Fare Original   -> Mean: {df_clean['fare'].mean():.2f}, Std: {df_clean['fare'].std():.2f}")
print(f"Fare Z-Standard -> Mean: {df_zcheck['fare_z'].mean():.4f}, Std: {df_zcheck['fare_z'].std():.4f}")
