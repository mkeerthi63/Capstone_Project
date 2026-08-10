# Data Pipeline (`/data_pipeline`)

An end-to-end catalog data engineering pipeline designed to process book pricing and availability data. The pipeline scrapes live product data from `books.toscrape.com`, cleans and enriches attributes, persists the data into a normalized SQLite database, and runs analytical SQL queries validated against `pandas`.

---

## Setup & Installation

### Requirements

* Python 3.8+
* `requests`
* `beautifulsoup4`
* `pandas`

### Install Dependencies

```bash
pip install requests beautifulsoup4 pandas
```

### Run the Complete Pipeline

From the `/data_pipeline` directory:

```bash
python pipeline.py
```

The pipeline runs end to end without manual copy-pasting and automatically generates:

```text
cleaned_books.csv
books_catalog.db
```

SQL query results and the SQL-vs-Pandas JOIN comparison are also printed/logged by the pipeline.

---

## Pipeline Acceptance Requirements

The completed pipeline produces:

* **At least 60 book rows**
* **At least 3 book categories**
* Correctly typed `price_gbp`
* Integer `rating` values from 1–5
* Boolean-compatible `in_stock` values
* Calculated `price_inr`
* A normalized two-table SQLite schema
* At least 5 SQL queries
* At least one SQL `JOIN`
* SQL results read using `pd.read_sql(...)`
* The JOIN independently reproduced using `pd.merge(...)`
* Side-by-side comparison of SQL JOIN and Pandas merge results

The pipeline validates the minimum dataset requirements before completing successfully.

---

# Pipeline Architecture & Design Choices

## 1. Web Scraping (`scrape_books`)

### Source

```text
http://books.toscrape.com/
```

### Scraping Strategy

The scraper iterates through category pages obtained from the website's side navigation menu rather than making individual requests for every product detail page.

This reduces the number of HTTP requests and helps avoid unnecessary connection failures or rate-limiting.

The scraper continues across category pages until the required dataset size is reached.

The final dataset contains:

```text
Books      >= 60
Categories >= 3
```

### Resilience

A `requests.Session` is used with:

* A standard browser-style `User-Agent`
* HTTP retry handling
* Retry backoff
* Request timeouts
* Exception handling

This allows temporary network failures to be handled without unnecessarily terminating the entire pipeline.

---

# 2. Data Cleaning & Enrichment (`clean_and_enrich_data`)

## Price Parsing (`price_gbp`)

The raw website price contains the `£` currency symbol.

The symbol and other non-numeric characters are removed using regular expressions before conversion to a numeric value.

Example:

```text
£51.77
```

becomes:

```text
51.77
```

The final `price_gbp` column is stored as a floating-point numeric value.

---

## Rating Normalization (`rating`)

The website represents ratings using words.

The following mapping is applied:

| Website Value | Integer |
| ------------- | ------: |
| One           |       1 |
| Two           |       2 |
| Three         |       3 |
| Four          |       4 |
| Five          |       5 |

The final `rating` column contains integer values from **1 to 5**.

---

## Stock Availability (`in_stock`)

Raw availability text is converted into a Boolean-compatible value:

```text
"In stock" → True / 1
Otherwise  → False / 0
```

The SQLite representation uses an integer because SQLite stores Boolean values as integers.

---

## Missing and Invalid Values

Numeric fields are checked for parsing failures and missing values.

Where the project cleaning logic encounters a numeric `NaN`, median imputation may be applied using the cleaned column median.

For example:

```python
clean_df["price_gbp"] = (
    clean_df["price_gbp"]
    .fillna(clean_df["price_gbp"].median())
)
```

The pipeline also uses exception handling for scraping and parsing operations.

Required fields are validated before database loading.

---

# 3. Fixed GBP → INR Conversion

The project uses the following **fixed project-defined conversion rate**:

```text
1 GBP = 105.50 INR
```

This is a fixed baseline required by the project.

It has **no date reference** and does not use a live exchange-rate API.

The conversion is:

```python
price_inr = round(price_gbp * 105.50, 2)
```

For example:

```text
£10.00 × 105.50 = ₹1,055.00
```

Using a fixed rate ensures that the pipeline produces reproducible results.

---

# 4. CSV Export

After cleaning and enrichment, the final dataset is exported to:

```text
cleaned_books.csv
```

This file is generated automatically by `pipeline.py`.

It contains the cleaned and enriched book records before database loading.

---

# Relational Database Schema (`setup_and_load_db`)

The pipeline uses a normalized two-table SQLite database:

```text
books_catalog.db
```

Foreign key enforcement is enabled using:

```sql
PRAGMA foreign_keys = ON;
```

---

## Categories Table

```sql
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
);
```

The `categories` table stores unique book categories.

---

## Books Table

```sql
CREATE TABLE IF NOT EXISTS books (
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

---

## Primary Key / Foreign Key Relationship

```text
categories
    |
    | category_id
    |
    v
books.category_id
```

* `categories.category_id` → Primary Key
* `books.book_id` → Primary Key
* `books.category_id` → Foreign Key

This provides the required relational structure for the SQL JOIN.

---

# SQL Queries & Analysis

The pipeline executes **at least 5 SQL queries** covering the required SQL clauses.

The queries collectively demonstrate:

* `SELECT`
* `WHERE`
* `ORDER BY`
* `LIMIT`
* `DISTINCT`
* `BETWEEN`
* `IN`
* `GROUP BY`
* `JOIN`

---

## Query 1 — SELECT / WHERE / ORDER BY / LIMIT

Fetch the top 5 most expensive books that are currently in stock:

```sql
SELECT
    book_id,
    title,
    price_gbp,
    rating
FROM books
WHERE in_stock = 1
ORDER BY price_gbp DESC, book_id ASC
LIMIT 5;
```

---

## Query 2 — DISTINCT

Fetch the unique ratings present in the dataset:

```sql
SELECT DISTINCT rating
FROM books
ORDER BY rating;
```

---

## Query 3 — BETWEEN

Find books priced between £20 and £40:

```sql
SELECT
    book_id,
    title,
    price_gbp
FROM books
WHERE price_gbp BETWEEN 20 AND 40
ORDER BY price_gbp, book_id;
```

---

## Query 4 — IN

Find books with ratings of 4 or 5:

```sql
SELECT
    book_id,
    title,
    rating,
    price_gbp
FROM books
WHERE rating IN (4, 5)
ORDER BY rating DESC, book_id;
```

---

## Query 5 — INNER JOIN

Join books with their category names:

```sql
SELECT
    b.book_id,
    b.title,
    b.price_gbp,
    b.price_inr,
    b.rating,
    b.in_stock,
    c.category_name
FROM books AS b
INNER JOIN categories AS c
    ON b.category_id = c.category_id
ORDER BY b.price_gbp DESC, b.book_id ASC;
```

The SQL queries and their printed/logged outputs are generated by the pipeline.

---

# Pandas Validation

The project independently verifies SQL results using Pandas.

At least two SQL query results are read into Pandas DataFrames using `pd.read_sql()`.

For example:

```python
query1_df = pd.read_sql(
    query1,
    conn
)

query2_df = pd.read_sql(
    query2,
    conn
)
```

This confirms that SQL query results can be read back successfully into Pandas.

---

# SQL JOIN vs Pandas `merge()`

The SQL JOIN result is read into a DataFrame using:

```python
sql_join_df = pd.read_sql(
    join_query,
    conn
)
```

The underlying tables are separately loaded into Pandas:

```python
books_df = pd.read_sql(
    "SELECT * FROM books",
    conn
)

categories_df = pd.read_sql(
    "SELECT * FROM categories",
    conn
)
```

The same JOIN is independently reproduced using `pd.merge()`:

```python
merged_df = pd.merge(
    books_df,
    categories_df,
    on="category_id",
    how="inner"
)
```

The Pandas result is then restricted to the same columns as the SQL result:

```python
merged_df = merged_df[
    [
        "book_id",
        "title",
        "price_gbp",
        "price_inr",
        "rating",
        "in_stock",
        "category_name"
    ]
]
```

---

# Deterministic Sorting

To ensure that both approaches produce the same row order, both results use the same deterministic sorting keys:

```python
sort_columns = [
    "price_gbp",
    "book_id"
]
```

SQL:

```sql
ORDER BY b.price_gbp DESC, b.book_id ASC
```

Pandas:

```python
merged_df = merged_df.sort_values(
    by=["price_gbp", "book_id"],
    ascending=[False, True]
)
```

Both DataFrames are reset before comparison:

```python
sql_join_df = (
    sql_join_df
    .sort_values(
        by=["price_gbp", "book_id"],
        ascending=[False, True]
    )
    .reset_index(drop=True)
)

merged_df = (
    merged_df
    .sort_values(
        by=["price_gbp", "book_id"],
        ascending=[False, True]
    )
    .reset_index(drop=True)
)
```

---

# Side-by-Side Verification

The SQL JOIN and Pandas merge results are displayed side by side.

```python
comparison_df = pd.concat(
    [
        sql_join_df.add_prefix("SQL_"),
        merged_df.add_prefix("PANDAS_")
    ],
    axis=1
)

print(comparison_df)
```

The results are also checked for equivalence:

```python
pd.testing.assert_frame_equal(
    sql_join_df,
    merged_df,
    check_dtype=False
)
```

Successful execution confirms:

```text
SQL JOIN result == Pandas merge result
```

The side-by-side comparison is saved/generated by the pipeline for submission verification.

---

# ETL Workflow

```text
                 Books to Scrape
                        │
                        ▼
                    EXTRACT
                        │
                        ▼
                 Raw Book Data
                        │
                        ▼
                   TRANSFORM
                        │
          ┌─────────────┼──────────────┐
          │             │              │
          ▼             ▼              ▼
     Clean Price   Convert Rating   Stock Status
          │             │              │
          └─────────────┼──────────────┘
                        │
                        ▼
                GBP → INR Conversion
                  1 GBP = 105.50 INR
                        │
                        ▼
                      LOAD
                        │
                        ▼
                SQLite Database
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        categories               books
             │                     │
             └────── INNER JOIN ───┘
                        │
                        ▼
                   SQL Analysis
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
        pd.read_sql()          pd.merge()
             │                     │
             └──────────┬──────────┘
                        ▼
                 Result Comparison
```

---

# Generated Files

After running:

```bash
python pipeline.py
```

the pipeline generates:

```text
/data_pipeline/
│
├── pipeline.py
├── requirements.txt
├── README.md
├── cleaned_books.csv
├── books_catalog.db
│
└── outputs/
    ├── query_results.txt
    └── join_comparison.csv
```

The SQLite database can be regenerated from scratch by rerunning:

```bash
python pipeline.py
```

No manual database population is required.

---

# Git Workflow

The module is maintained within the single project repository using a feature branch.

The repository history demonstrates:

1. Feature branch creation
2. At least two commits on the feature branch
3. Merge back into `main`

Example:

```bash
git checkout -b feature/data-pipeline

git add .
git commit -m "Add book scraping and cleaning pipeline"

git add .
git commit -m "Add SQLite database and SQL analysis"

git checkout main
git merge feature/data-pipeline
```

The complete repository history can be checked using:

```bash
git log --oneline --graph --all
```

---

# Acceptance Criteria Checklist

| Requirement                          | Status |
| ------------------------------------ | ------ |
| ≥60 book rows                        | ✅      |
| ≥3 categories                        | ✅      |
| `price_gbp` correctly typed          | ✅      |
| `rating` integer 1–5                 | ✅      |
| `in_stock` Boolean-compatible        | ✅      |
| `price_inr` present                  | ✅      |
| Fixed rate `1 GBP = 105.50 INR`      | ✅      |
| No external currency API             | ✅      |
| Two-table SQLite schema              | ✅      |
| Primary Key / Foreign Key            | ✅      |
| Database recreation script           | ✅      |
| ≥5 SQL queries                       | ✅      |
| `SELECT`                             | ✅      |
| `WHERE`                              | ✅      |
| `ORDER BY`                           | ✅      |
| `LIMIT`                              | ✅      |
| `DISTINCT`                           | ✅      |
| `BETWEEN`                            | ✅      |
| `IN`                                 | ✅      |
| `GROUP BY`                           | ✅      |
| `JOIN`                               | ✅      |
| SQL outputs printed/logged           | ✅      |
| At least two `pd.read_sql()` results | ✅      |
| JOIN reproduced with `pd.merge()`    | ✅      |
| Side-by-side comparison              | ✅      |
| Equivalent outputs verified          | ✅      |
| README installation/run instructions | ✅      |
| Cleaning decisions documented        | ✅      |
| Feature branch created               | ✅      |
| At least two commits                 | ✅      |
| Feature branch merged into `main`    | ✅      |

---

# Learning Outcomes

This project demonstrates practical experience with:

* Web Scraping
* ETL Pipeline Development
* Data Cleaning
* Data Transformation
* Feature Engineering
* Pandas
* SQLite
* Relational Database Design
* Primary Keys and Foreign Keys
* SQL Queries
* SQL JOINs
* `pd.read_sql()`
* `pd.merge()`
* Data Validation
* Exception Handling
* Git Branching and Merging
* Reproducible Data Pipelines

---

## Author

**Keerthi**

**B.Tech – Computer Science & Engineering**

**Skills:** Python, SQL, Pandas, SQLite, BeautifulSoup, Data Engineering, ETL Pipelines
