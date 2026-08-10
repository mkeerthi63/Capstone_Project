# Analytics Pipeline (`/analytics`) — Titanic Dataset

An end-to-end data science and machine learning pipeline built on the Titanic dataset. This module covers data profiling, missing-value handling, exploratory data analysis (EDA), feature preprocessing, classification modeling, class-imbalance benchmarking, hyperparameter tuning, regression analysis, model comparison, and model serialization.

---

## 1. Executive Summary

The analytics pipeline analyzes the Titanic passenger dataset to understand the factors associated with passenger survival and to build machine learning models capable of predicting survival.

The pipeline includes:

* Dataset profiling
* Missing-value analysis
* Data cleaning and imputation
* Univariate and bivariate analysis
* Outlier detection
* Correlation analysis
* Feature preprocessing
* Stratified train/test splitting
* Classification modeling
* Class-imbalance benchmarking
* Hyperparameter tuning
* ROC-AUC evaluation
* Fare regression side-task
* Residual analysis
* Model comparison
* End-to-end pipeline serialization using `joblib`

---

## 2. Project Structure

```text
/analytics
│
├── titanic.csv
├── 01_eda.py
├── 02_modeling.py
├── full_pipeline.joblib
│
├── univariate_analysis.png
├── correlation_matrix.png
├── decision_tree.png
├── roc_curves.png
├── residual_plot.png
│
├── README.md
└── requirements.txt
```

### File Description

| File                      | Purpose                                                              |
| ------------------------- | -------------------------------------------------------------------- |
| `titanic.csv`             | Offline fallback copy of the Titanic dataset                         |
| `01_eda.py`               | Dataset profiling, cleaning, EDA, and visualization                  |
| `02_modeling.py`          | Preprocessing, model training, tuning, evaluation, and serialization |
| `full_pipeline.joblib`    | Fully fitted end-to-end scikit-learn pipeline                        |
| `univariate_analysis.png` | Age and Fare distribution plots                                      |
| `correlation_matrix.png`  | Numeric feature correlation heatmap                                  |
| `decision_tree.png`       | Decision Tree visualization                                          |
| `roc_curves.png`          | ROC curve comparison                                                 |
| `residual_plot.png`       | Fare regression residual analysis                                    |
| `README.md`               | Documentation and analytical conclusions                             |
| `requirements.txt`        | Python dependencies                                                  |

---

# 3. Setup & Installation

## Requirements

* Python 3.8+
* pandas
* numpy
* scikit-learn
* matplotlib
* seaborn
* joblib

Install dependencies using:

```bash
pip install -r requirements.txt
```

---

## Running the Analytics Pipeline

Run the EDA script:

```bash
python 01_eda.py
```

Then run the modeling pipeline:

```bash
python 02_modeling.py
```

The scripts generate the cleaned dataset, analytical visualizations, model evaluation results, and serialized machine-learning pipeline.

---

# 4. Part A — Dataset Profiling

The Titanic dataset contains:

* **891 rows**
* **15 columns**

The target variable is:

```text
survived
```

where:

```text
0 = Did not survive
1 = Survived
```

The dataset contains both numerical and categorical variables, including:

* `pclass`
* `sex`
* `age`
* `sibsp`
* `parch`
* `fare`
* `embarked`
* `class`
* `who`
* `adult_male`
* `deck`
* `embark_town`
* `alive`
* `alone`

---

# 5. Missing-Value Analysis

The following missing-value strategy was applied.

| Column        | Missing Count | Missing % | Strategy             | Reason                               |
| ------------- | ------------: | --------: | -------------------- | ------------------------------------ |
| `embarked`    |             2 |     0.22% | Drop rows            | Negligible amount of missing data    |
| `embark_town` |             2 |     0.22% | Drop rows            | Same rows are missing as `embarked`  |
| `age`         |           177 |    19.87% | Median imputation    | Robust to skew and outliers          |
| `deck`        |           688 |    77.22% | `"Unknown"` category | Preserves missingness as information |

### Age

The `age` column has approximately 19.87% missing values.

Median imputation is used because the median is less sensitive to extreme values than the mean.

The median age used is:

```text
28.0 years
```

### Deck

Approximately 77.22% of the `deck` values are missing.

Instead of attempting numerical or statistical imputation, missing values are represented as:

```text
Unknown
```

This preserves the information that cabin/deck information was unavailable.

---

# 6. Data Cleaning Decisions

## Numerical Variables

Numerical columns are converted to appropriate numeric types.

Missing `age` values are filled using the median.

---

## Categorical Variables

Categorical missing values are handled according to the missing-value strategy described above.

Categorical features are encoded using a scikit-learn preprocessing pipeline.

---

## Target Variable

The target variable is:

```text
survived
```

It is separated from the input features before model training.

---

# 7. Univariate Analysis

Univariate analysis was performed on important numerical variables such as:

* `age`
* `fare`

The generated visualization is:

```text
univariate_analysis.png
```

---

## Age Outliers

Using the IQR method:

```text
Lower Bound = Q1 - 1.5 × IQR
Upper Bound = Q3 + 1.5 × IQR
```

the calculated bounds were approximately:

```text
[-6.5, 64.5]
```

There were approximately:

```text
9 age outliers
```

The negative lower bound is a mathematical result of the IQR method; actual ages cannot be negative.

---

## Fare Outliers

The calculated Fare IQR bounds were approximately:

```text
[-26.76, 66.30]
```

There were approximately:

```text
116 fare outliers
```

These observations are retained because they represent legitimate passengers with unusually expensive tickets rather than obvious data-entry errors.

---

# 8. Fare Distribution and Skewness

The `fare` variable is strongly right-skewed.

The central tendencies demonstrate this:

```text
Mean   = 32.20
Median = 14.45
Mode   = 8.05
```

Therefore:

```text
Mean > Median > Mode
```

This indicates a long right tail caused by a smaller number of passengers paying substantially higher fares.

---

# 9. Bivariate Analysis

## Survival by Sex

| Sex    | Survival Rate |
| ------ | ------------: |
| Female |        74.20% |
| Male   |        18.89% |

Female passengers had substantially higher observed survival rates than male passengers.

---

## Survival by Passenger Class

| Passenger Class | Survival Rate |
| --------------- | ------------: |
| 1st Class       |        62.96% |
| 2nd Class       |        47.28% |
| 3rd Class       |        24.24% |

Survival rate decreased as passenger class increased numerically from 1st to 3rd class.

---

## Survival by Sex and Passenger Class

| Class     | Female |   Male |
| --------- | -----: | -----: |
| 1st Class | 96.81% | 36.89% |
| 2nd Class | 92.11% | 15.74% |
| 3rd Class | 50.00% | 13.54% |

The interaction between sex and passenger class is substantial. Female passengers had higher observed survival rates within every passenger class.

---

# 10. Correlation Analysis

A restricted 6×6 numeric correlation matrix was generated using:

* `survived`
* `pclass`
* `age`
* `sibsp`
* `parch`
* `fare`

The derived Boolean variables `adult_male` and `alone` were excluded from this matrix to keep the correlation analysis focused on the selected core numerical variables.

The visualization is saved as:

```text
correlation_matrix.png
```

---

## Strongest Correlations

### 1. `pclass` and `fare`

```text
r = -0.5491
```

This is the strongest absolute correlation in the selected matrix.

Because lower numerical `pclass` values represent higher passenger classes, the negative correlation indicates that higher-class passengers generally paid higher fares.

---

### 2. `sibsp` and `parch`

```text
r = +0.4148
```

This moderate positive correlation indicates that passengers traveling with siblings/spouses were also more likely to travel with parents/children.

---

# 11. Multivariate Data Story

Several patterns emerge from the exploratory analysis:

### Gender and Survival

Female passengers had substantially higher observed survival rates than male passengers across all passenger classes.

A historical explanation is consistent with the well-known evacuation practices of the Titanic era, although the dataset itself does not directly establish the causal mechanism.

### Passenger Class

Passenger class is strongly associated with survival. First-class passengers had considerably higher survival rates than third-class passengers.

### Age

Younger passengers, particularly children, showed different survival patterns from older passengers. Age therefore provides useful predictive information.

### Fare

Fare is strongly right-skewed and is also associated with passenger class. Higher fares generally correspond to higher passenger classes.

### Family Variables

`SibSp` and `Parch` contain information about family relationships and may provide predictive information beyond individual passenger characteristics.

---

# 12. Z-Score Standardization Sanity Check

A standalone standardization check was performed using:

```text
z = (x - μ) / σ
```

### Age

Original:

```text
Mean = 29.36
Std  = 13.01
```

After standardization:

```text
Mean ≈ 0.0000
Std  ≈ 1.0000
```

### Fare

Original:

```text
Mean = 32.20
Std  = 49.69
```

After standardization:

```text
Mean ≈ 0.0000
Std  ≈ 1.0000
```

This confirms that the standardization transformation behaves as expected.

---

# 13. Part B — Predictive Modeling

## Target

The classification target is:

```text
survived
```

---

# 14. Train/Test Split

The dataset is divided using:

```text
80% Training
20% Testing
```

Stratification is applied:

```python
train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)
```

### Why Stratification?

The target contains an imbalanced distribution, with approximately:

```text
38% positive class
62% negative class
```

Stratification maintains approximately the same class proportions in both training and testing datasets.

---

# 15. Data Leakage Prevention

All preprocessing operations are placed inside a scikit-learn preprocessing pipeline.

The pipeline contains:

* Numerical imputation
* Categorical imputation
* Categorical encoding
* Feature scaling where required
* Final machine-learning estimator

The preprocessing components are fitted only on the training data.

The test data is transformed using the already-fitted preprocessing components.

This prevents information from the test set from leaking into model training.

---

# 16. Classification Models

The following classification models were evaluated:

1. Logistic Regression
2. Decision Tree
3. Random Forest

Evaluation metrics include:

* Accuracy
* Precision
* Recall
* F1 Score
* ROC AUC

---

# 17. Class Imbalance Benchmark

Random Forest models were evaluated under three imbalance strategies.

| Imbalance Strategy             |  Precision |     Recall |   F1 Score |
| ------------------------------ | ---------: | ---------: | ---------: |
| **Baseline — No Handling**     | **0.8136** |     0.6957 |     0.7500 |
| **Class Weight — `balanced`**  |     0.8033 |     0.7101 |     0.7538 |
| **SMOTE — Training Data Only** |     0.7727 | **0.7391** | **0.7556** |

### Interpretation

The baseline model achieved the highest precision:

```text
81.36%
```

The SMOTE model achieved the highest recall:

```text
73.91%
```

and the highest F1 score among the three imbalance strategies:

```text
75.56%
```

This demonstrates the trade-off between precision and recall when addressing class imbalance.

SMOTE was applied only to the training data to prevent synthetic samples from influencing the test set.

---

# 18. Hyperparameter Tuning

Random Forest hyperparameters were optimized using `GridSearchCV`.

The estimator was:

```python
RandomForestClassifier(
    oob_score=True,
    random_state=42
)
```

### Parameter Grid

```text
n_estimators:
[50, 100, 150]

max_depth:
[4, 6, 8, None]

max_features:
['sqrt', 'log2']
```

### Best Parameters

```python
{
    'max_depth': 6,
    'max_features': 'sqrt',
    'n_estimators': 100
}
```

---

## Out-of-Bag Score

The tuned Random Forest achieved:

```text
OOB Score = 0.8214
```

The OOB score provides an internal estimate of generalization performance using samples not included in individual bootstrap training samples.

---

# 19. Classification Model Comparison

| Model                       |   Accuracy |  Precision | Recall |   F1 Score |    ROC AUC |
| --------------------------- | ---------: | ---------: | -----: | ---------: | ---------: |
| **Logistic Regression**     |     0.8034 |     0.7692 | 0.7246 |     0.7463 |     0.8521 |
| **Decision Tree (depth=4)** |     0.7921 |     0.7818 | 0.6232 |     0.6935 |     0.8143 |
| **Random Forest (Tuned)**   | **0.8258** | **0.8033** | 0.7101 | **0.7538** | **0.8680** |

---

# 20. Model Comparison Interpretation

## Logistic Regression

Logistic Regression provides a strong baseline and achieves:

```text
ROC AUC = 0.8521
```

Its performance indicates that the selected features contain useful approximately linear predictive relationships.

---

## Decision Tree

The Decision Tree achieves lower overall performance:

```text
Accuracy = 0.7921
ROC AUC  = 0.8143
```

The constrained depth of 4 helps control model complexity but limits the ability to represent more complicated relationships.

---

## Tuned Random Forest

The tuned Random Forest provides the strongest overall classification performance:

```text
Accuracy = 82.58%
Precision = 80.33%
Recall = 71.01%
F1 Score = 75.38%
ROC AUC = 0.8680
```

It achieves the highest accuracy, F1 score, and ROC AUC among the evaluated classification models.

---

# 21. ROC Curve Analysis

ROC curves were generated for the evaluated classification models.

The visualization is saved as:

```text
roc_curves.png
```

The Random Forest achieves the highest ROC AUC:

```text
0.8680
```

indicating the strongest ability among the evaluated models to distinguish survivors from non-survivors across classification thresholds.

---

# 22. Decision Tree Visualization

The trained Decision Tree is visualized using `plot_tree`.

The resulting visualization is saved as:

```text
decision_tree.png
```

This provides an interpretable view of the decision rules learned by the tree.

---

# 23. Regression Side Task — Fare Prediction

A separate regression task was performed to predict:

```text
fare
```

using other numerical and categorical passenger attributes.

A multivariate Linear Regression model was evaluated using:

* MAE
* RMSE
* R²
* Adjusted R²

---

## Regression Results

| Model                              |   MAE |  RMSE |     R² | Adjusted R² |
| ---------------------------------- | ----: | ----: | -----: | ----------: |
| **Multivariate Linear Regression** | 25.41 | 39.82 | 0.3812 |      0.3541 |

---

# 24. Regression Interpretation

The model achieved:

```text
MAE = 25.41
RMSE = 39.82
R² = 0.3812
Adjusted R² = 0.3541
```

The R² value indicates that approximately 38.12% of the variance in fare is explained by the predictors included in the regression model.

The remaining variation suggests that additional information not represented in the selected features may influence ticket prices.

---

# 25. Residual Analysis

The regression residual plot is saved as:

```text
residual_plot.png
```

The residual plot shows evidence of **heteroscedasticity**.

The spread of residuals increases for higher predicted fare values.

This is consistent with the strong right-skewness of the `fare` variable and the presence of expensive first-class tickets.

Therefore, the linear regression model does not perfectly satisfy the constant-variance assumption.

---

# 26. Model Selection

Based on the classification model comparison:

```text
Random Forest ROC AUC = 0.8680
Random Forest Accuracy = 0.8258
Random Forest F1 = 0.7538
```

The tuned Random Forest provides the strongest overall classification performance among the evaluated models.

---

# 27. Deployment Recommendation

I recommend deploying the **Tuned Random Forest Classifier**.

It provides the strongest overall performance among the evaluated classification models, achieving:

* **82.58% Accuracy**
* **80.33% Precision**
* **71.01% Recall**
* **75.38% F1 Score**
* **0.8680 ROC AUC**

Although the baseline Random Forest achieved slightly higher precision in the separate class-imbalance benchmark, the tuned Random Forest provides the strongest overall balance in the final model comparison.

Its ensemble structure can capture non-linear relationships and interactions between passenger characteristics such as:

* Passenger class
* Age
* Sex
* Fare
* Family-related variables

The model is therefore selected as the final deployment candidate.

---

# 28. End-to-End Saved Pipeline

The complete preprocessing and modeling pipeline is serialized using `joblib`.

The saved file is:

```text
full_pipeline.joblib
```

The pipeline includes the preprocessing transformations and final tuned estimator.

This allows raw, unprocessed input data to be supplied directly during inference.

---

## Loading the Saved Model

```python
import joblib
import pandas as pd

pipeline = joblib.load(
    "full_pipeline.joblib"
)
```

---

## Example Raw Input

```python
raw_data = pd.DataFrame(
    {
        "pclass": [3, 1],
        "sex": ["male", "female"],
        "age": [22.0, 38.0],
        "sibsp": [1, 1],
        "parch": [0, 0],
        "fare": [7.25, 71.2833],
        "embarked": ["S", "C"],
    }
)
```

The raw data can be passed directly to the serialized pipeline:

```python
predictions = pipeline.predict(
    raw_data
)

print(
    "Survival Predictions:",
    predictions
)
```

No manual preprocessing is required before calling `predict()`.

---

# 29. Reproducibility

Random seeds are fixed where appropriate:

```text
random_state = 42
```

This ensures that train/test splitting, model training, and other stochastic operations produce reproducible results.

The preprocessing and model training steps are contained within scikit-learn pipelines to minimize data leakage and maintain consistent transformations between training and inference.

---

# 30. Generated Visualizations

The analytics pipeline produces the following figures:

### Univariate Analysis

```text
univariate_analysis.png
```

Shows the distributions of important numerical variables such as Age and Fare.

### Correlation Matrix

```text
correlation_matrix.png
```

Shows correlations among the selected numerical features.

### Decision Tree

```text
decision_tree.png
```

Visualizes the learned Decision Tree structure.

### ROC Curves

```text
roc_curves.png
```

Compares classification model discrimination performance.

### Residual Plot

```text
residual_plot.png
```

Evaluates residual behavior for the Fare regression task.

---

# 31. Final Results Summary

## Classification

The tuned Random Forest is the strongest evaluated classifier:

```text
Accuracy  = 0.8258
Precision = 0.8033
Recall    = 0.7101
F1 Score  = 0.7538
ROC AUC   = 0.8680
```

## Class Imbalance

SMOTE provides the highest recall and F1 score in the imbalance benchmark:

```text
Recall = 0.7391
F1     = 0.7556
```

The baseline provides the highest precision:

```text
Precision = 0.8136
```

## Regression

The Linear Regression Fare model achieves:

```text
MAE          = 25.41
RMSE         = 39.82
R²           = 0.3812
Adjusted R²  = 0.3541
```


# 34. Author

**Keerthi**

**B.Tech – Computer Science & Engineering**

**Skills:** Python, SQL, Pandas, NumPy, Scikit-learn, SQLite, Data Analysis, Machine Learning, ETL Pipelines
