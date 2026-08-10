# Module 1 — Catalog Data Pipeline (`/data_pipeline`)

## Overview
This module builds an end-to-end data engineering pipeline designed to benchmark catalog-style pricing and availability data for competitive intelligence workflows. It extracts raw product data from `books.toscrape.com`, cleans and enriches the dataset, loads it into a normalized relational SQLite database, and runs analytical queries validated against `pandas`.

---

## Installation & Setup

### Requirements
* Python 3.8+
* Libraries: `requests`, `beautifulsoup4`, `pandas`

### Quick Start
1. **Navigate to the module directory:**
   ```bash
   cd data_pipeline
->Install required dependencies:
pip install requests beautifulsoup4 pandas
->Run the complete pipeline:
python pipeline.py
(Running this script auto-generates cleaned_books.csv and books_catalog.db in the current directory).
Pipeline Architecture & Design Choices
## 1. Web Scraping (scrape_books)
Source: http://books.toscrape.com/
Strategy: Iterates directly through specific category pages from the side navigation menu instead of issuing individual HTTP requests per product detail page.
This prevents network rate-limiting and avoids connection dropouts (ConnectionRefusedError / Errno 111).
Resilience: Implements a requests.Session configured with a standard Chrome User-Agent and automated HTTP retry backoffs (urllib3.util.Retry).
## 2. Data Cleaning & Imputation Decisions (clean_and_enrich_data)
Price Parsing (price_gbp): Removes non-numeric currency symbols (£) using regular expressions ([^\d.]) and casts values to float.
Rating Normalization (rating): Maps word-based star ratings (One through Five) into explicit integer values (1 to 5).
Stock Availability (in_stock): Converts raw availability strings (In stock) to binary integers (1 for True, 0 for False).
Missing Value Imputation: If numeric price or rating fields fail to parse or contain NaN, median imputation is applied (fillna(clean_df['field'].median())) to keep summary statistics robust without dropping valid rows or causing pipeline crashes.
Currency Conversion (price_inr): Enriches price data using the project-defined fixed baseline conversion rate:
$$\text{1 GBP} = \text{105.50 INR}$$
(This artificial constant requires no live network/API lookups).
CSV Export: Saves the cleaned and enriched dataset locally to cleaned_books.csv prior to database loading.
## Relational Database Schema (setup_and_load_db)
Data is structured into a 2-table normalized relational SQLite schema (books_catalog.db) with Foreign Key constraints enabled (PRAGMA foreign_keys = ON;):
SQL-- Categories Reference Table
CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL
);

-- Main Product Table
CREATE TABLE IF NOT EXISTS books (
    book_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price_gbp REAL NOT NULL,
    price_inr REAL NOT NULL,
    rating INTEGER NOT NULL,
    in_stock INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories (category_id)
);
SQL Queries & Pandas ValidationThe script executes 5 SQL queries demonstrating required SQL clauses:SELECT / WHERE / ORDER BY / LIMIT: Fetch top 5 most expensive in-stock items.DISTINCT: Fetch unique star ratings available in the dataset.BETWEEN: Filter books priced within £20.00 to £40.00.IN: Select highly rated items (rating in 4 or 5).JOIN: Relational join connecting books to categories on category_id.Deterministic Tie-Breaking & VerificationTo guarantee consistent sorting between SQLite and Pandas when prices are identical, both queries enforce a secondary sort key on book_id ASC:SQL JOIN: ORDER BY b.price_gbp DESC, b.book_id ASCPandas Merge: .sort_values(by=["price_gbp", "book_id"], ascending=[False, True])Outputs from pd.read_sql_query() and pd.merge() are validated using pd.testing.assert_frame_equal().
