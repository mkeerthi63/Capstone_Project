# End-to-End Data & AI Engineering Project

A three-module project demonstrating an end-to-end workflow across **data engineering, data analytics & machine learning, and Generative AI/RAG application development**.

The repository contains three independent but complementary projects:

1. **Data Pipeline** — Web scraping, data cleaning, ETL, SQLite, SQL analysis, and Pandas validation.
2. **Analytics Pipeline** — Titanic EDA, preprocessing, machine learning, model evaluation, hyperparameter tuning, regression, and model serialization.
3. **Zepto Support Assistant** — Offline-first RAG application using ChromaDB, LangGraph, Pydantic, Sentence Transformers, and FastAPI.

---

# 1. Repository Structure

```text
project/
│
├── README.md
├── requirements.txt
│
├── data_pipeline/
│   ├── README.md
│   ├── requirements.txt
│   ├── pipeline.py
│   ├── cleaned_books.csv
│   └── books_catalog.db
│
├── analytics/
│   ├── README.md
│   ├── requirements.txt
│   ├── 01_eda.py
│   ├── 02_modeling.py
│   ├── titanic.csv
│   ├── full_pipeline.joblib
│   ├── univariate_analysis.png
│   ├── correlation_matrix.png
│   ├── decision_tree.png
│   ├── roc_curves.png
│   └── residual_plot.png
│
└── support_assistant/
    ├── README.md
    ├── requirements.txt
    ├── main.py
    ├── Dockerfile
    ├── docs/
    │   ├── doc_01.txt
    │   ├── doc_02.txt
    │   ├── doc_03.txt
    │   ├── doc_04.txt
    │   ├── doc_05.txt
    │   ├── doc_06.txt
    │   ├── doc_07.txt
    │   └── doc_08.txt
    └── db/
        └── chroma.sqlite3
```

---

# 2. Projects Overview

| Project             | Main Technology                       | Purpose                       |
| ------------------- | ------------------------------------- | ----------------------------- |
| `data_pipeline`     | Python, BeautifulSoup, Pandas, SQLite | Web scraping and ETL          |
| `analytics`         | Pandas, Scikit-learn, Matplotlib      | EDA and Machine Learning      |
| `support_assistant` | FastAPI, LangGraph, ChromaDB, RAG     | AI customer-support assistant |

---

# 3. Project 1 — Data Pipeline

## Overview

The Data Pipeline project implements an end-to-end ETL workflow using the **Books to Scrape** website.

The pipeline:

```text
Books to Scrape
       ↓
     Extract
       ↓
     Clean
       ↓
   Transform
       ↓
   GBP → INR
       ↓
      Load
       ↓
 SQLite Database
       ↓
 SQL Analysis
       ↓
 Pandas Validation
```

## Key Features

* Automated web scraping
* Multiple book categories
* Data cleaning
* Price parsing
* Rating conversion
* Stock-status conversion
* GBP-to-INR conversion
* SQLite database creation
* Primary Key / Foreign Key relationships
* SQL analytical queries
* Pandas `pd.read_sql()` validation
* Pandas `merge()` verification

## Fixed Exchange Rate

The project uses the required fixed conversion rate:

```text
1 GBP = 105.50 INR
```

Formula:

```text
price_inr = price_gbp × 105.50
```

No external exchange-rate API is used.

## Database

The project uses two normalized tables:

```text
categories
    │
    │ category_id
    │
    ▼
books
```

### Categories

```sql
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
);
```

### Books

```sql
CREATE TABLE books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL NOT NULL,
    price_inr REAL NOT NULL,
    rating INTEGER NOT NULL,
    in_stock INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id)
        REFERENCES categories(category_id)
);
```

## SQL Analysis

The project demonstrates:

* `SELECT`
* `WHERE`
* `BETWEEN`
* `DISTINCT`
* `IN`
* `ORDER BY`
* `LIMIT`
* `GROUP BY`
* `INNER JOIN`

The JOIN result is independently reproduced using:

```python
pd.merge()
```

and compared against:

```python
pd.read_sql()
```

---

# 4. Project 2 — Analytics Pipeline

## Overview

The Analytics project uses the Titanic dataset to perform exploratory data analysis and predictive modeling.

The workflow is:

```text
Titanic Dataset
       ↓
Data Profiling
       ↓
Missing Value Analysis
       ↓
Data Cleaning
       ↓
EDA
       ↓
Feature Preprocessing
       ↓
Train/Test Split
       ↓
Classification
       ↓
Hyperparameter Tuning
       ↓
Model Evaluation
       ↓
Model Serialization
```

## Key Features

* Dataset profiling
* Missing-value analysis
* Median imputation
* Categorical handling
* Outlier analysis
* Univariate analysis
* Bivariate analysis
* Correlation analysis
* Z-score standardization
* Stratified train/test split
* Data leakage prevention
* Logistic Regression
* Decision Tree
* Random Forest
* Class imbalance analysis
* SMOTE
* GridSearchCV
* ROC-AUC evaluation
* Regression side-task
* Residual analysis
* Joblib model serialization

## Classification Results

| Model               |   Accuracy |  Precision |     Recall |         F1 |    ROC AUC |
| ------------------- | ---------: | ---------: | ---------: | ---------: | ---------: |
| Logistic Regression |     0.8034 |     0.7692 |     0.7246 |     0.7463 |     0.8521 |
| Decision Tree       |     0.7921 |     0.7818 |     0.6232 |     0.6935 |     0.8143 |
| **Random Forest**   | **0.8258** | **0.8033** | **0.7101** | **0.7538** | **0.8680** |

The **Tuned Random Forest** is selected as the final classification model.

## Regression Results

The regression side-task predicts `fare`.

| Model             |   MAE |  RMSE |     R² | Adjusted R² |
| ----------------- | ----: | ----: | -----: | ----------: |
| Linear Regression | 25.41 | 39.82 | 0.3812 |      0.3541 |

## Saved Model

The complete preprocessing and modeling pipeline is saved as:

```text
analytics/full_pipeline.joblib
```

This allows raw input data to be passed directly into the trained pipeline.

---

# 5. Project 3 — Zepto Support Assistant

## Overview

The Support Assistant is an offline-first **Retrieval-Augmented Generation (RAG)** application designed to answer customer-support questions using a local Zepto policy corpus.

Architecture:

```text
User Query
    ↓
FastAPI
    ↓
Intent Classification
    ↓
Policy Question?
   /       \
 Yes       No
  ↓         ↓
ChromaDB   Direct Answer
  ↓
Top 3 Documents
  ↓
Response Generation
  ↓
Pydantic Validation
  ↓
JSON Response
```

## Technologies

* Python
* FastAPI
* Uvicorn
* LangGraph
* ChromaDB
* Sentence Transformers
* Pydantic
* Optional Groq LLM
* Docker

## Document Corpus

The application reads eight policy documents:

```text
doc_01.txt
doc_02.txt
doc_03.txt
doc_04.txt
doc_05.txt
doc_06.txt
doc_07.txt
doc_08.txt
```

Embeddings are generated using:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The vectors are stored in a local ChromaDB collection:

```text
zepto_policies
```

---

# 6. MOCK_LLM Mode

The default mode is:

```text
MOCK_LLM=1
```

This mode is designed for reproducible and offline execution.

It requires:

* No API key
* No external LLM
* No external generation service

Policy questions use retrieved context to generate a deterministic response.

General questions receive:

```text
I can only answer questions about Zepto policies right now.
```

---

# 7. Real LLM Mode

Optional real-LLM mode can be enabled using:

```text
MOCK_LLM=0
```

A Groq API key is required:

```text
GROQ_API_KEY
```

The application uses the configured Groq model for response generation and validates the resulting structured response using Pydantic.

---

# 8. Running the Projects

## Data Pipeline

Navigate to:

```bash
cd data_pipeline
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python pipeline.py
```

---

## Analytics

Navigate to:

```bash
cd analytics
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run EDA:

```bash
python 01_eda.py
```

Run modeling:

```bash
python 02_modeling.py
```

---

## Support Assistant

Navigate to:

```bash
cd support_assistant
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the API:

```bash
uvicorn main:app --host 0.0.0.0 --port 7860
```

The API is available at:

```text
http://127.0.0.1:7860
```

Swagger documentation:

```text
http://127.0.0.1:7860/docs
```

---

# 9. Docker — Support Assistant

Build the Docker image:

```bash
cd support_assistant
docker build -t zepto-support-assistant .
```

Run:

```bash
docker run -p 7860:7860 -e MOCK_LLM=1 zepto-support-assistant
```

---

# 10. API Example

Endpoint:

```text
POST /ask
```

Request:

```json
{
    "query": "What is the return policy for damaged items?"
}
```

Example response:

```json
{
    "answer": "Based on the retrieved context: ...",
    "sources": [
        "doc_02",
        "doc_06",
        "doc_05"
    ],
    "confidence": 1.0
}
```

---

# 11. Overall Technology Stack

```text
                    END-TO-END PROJECT
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
   DATA PIPELINE       ANALYTICS       SUPPORT ASSISTANT
          │                │                │
          ▼                ▼                ▼
   Web Scraping           EDA              RAG
   BeautifulSoup        Pandas          ChromaDB
   Pandas               NumPy           LangGraph
   SQLite               Scikit-learn    FastAPI
   SQL                  Matplotlib      Pydantic
          │                │                │
          ▼                ▼                ▼
       ETL              ML Models       AI Assistant
```

---

# 12. Skills Demonstrated

This repository demonstrates practical experience in:

### Data Engineering

* Web scraping
* ETL
* Data cleaning
* Data transformation
* SQLite
* Database normalization
* SQL
* Pandas
* Data validation

### Data Analytics & Machine Learning

* Exploratory Data Analysis
* Statistical analysis
* Data visualization
* Feature preprocessing
* Classification
* Regression
* Random Forest
* Decision Tree
* Logistic Regression
* SMOTE
* Hyperparameter tuning
* Cross-validation
* ROC-AUC
* Model serialization

### Generative AI

* Retrieval-Augmented Generation
* Vector databases
* Embeddings
* ChromaDB
* LangGraph
* Prompt-based generation
* Structured outputs
* Pydantic validation
* FastAPI
* Docker
* Offline-first AI architecture

---

# 13. Reproducibility

The projects are designed to be reproducible.

Important fixed values include:

```text
GBP → INR:
1 GBP = 105.50 INR

Random State:
42

Support Assistant:
MOCK_LLM=1
```

The Data Pipeline does not require a live currency API.

The Analytics pipeline uses fixed random states where applicable.

The Support Assistant provides an offline deterministic baseline through `MOCK_LLM=1`.

---

# 14. Project-Level Documentation

Each module contains its own detailed README:

```text
data_pipeline/README.md
analytics/README.md
support_assistant/README.md
```

The module-level README files contain implementation details, design decisions, execution instructions, and results specific to each project.

---

# 15. Installation — All Projects

A root-level `requirements.txt` can be used to install the dependencies for the complete repository:

```bash
pip install -r requirements.txt
```

The project also maintains individual dependency files inside each module.

```text
data_pipeline/requirements.txt
analytics/requirements.txt
support_assistant/requirements.txt
```

This allows each project to be executed independently.

---

# 16. End-to-End Learning Architecture

The three projects together demonstrate a progression from raw data collection to intelligent application development:

```text
                    RAW DATA
                       │
                       ▼
              ┌─────────────────┐
              │  DATA PIPELINE  │
              │                 │
              │ Scrape → Clean  │
              │ Transform → SQL │
              └────────┬────────┘
                       │
                       ▼
                CLEAN DATA
                       │
                       ▼
              ┌─────────────────┐
              │    ANALYTICS    │
              │                 │
              │ EDA → ML → Tune │
              │ Evaluate → Save │
              └────────┬────────┘
                       │
                       ▼
              MACHINE LEARNING
                       │
                       ▼
              ┌─────────────────┐
              │ SUPPORT         │
              │ ASSISTANT       │
              │                 │
              │ RAG → Retrieval │
              │ → Generation    │
              │ → API           │
              └─────────────────┘
```

---

# 17. Final Summary

This repository contains three practical projects covering the complete journey from **data acquisition to analytics to AI application development**.

### Project 1 — Data Pipeline

Demonstrates:

```text
Web Scraping → ETL → SQLite → SQL → Pandas Validation
```

### Project 2 — Analytics

Demonstrates:

```text
EDA → Cleaning → ML → Evaluation → Tuning → Serialization
```

### Project 3 — Support Assistant

Demonstrates:

```text
Documents → Embeddings → Vector Search → RAG → FastAPI
```

Together, these projects demonstrate practical skills in:

**Python + SQL + Pandas + Data Engineering + Machine Learning + RAG + Generative AI + API Development + Docker**
