import os
import re
import sqlite3
import time
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from bs4 import BeautifulSoup
BASE_URL = "http://books.toscrape.com/"
FIXED_GBP_TO_INR_RATE = 105.50
DB_NAME = "books_catalog.db"
CSV_FILE_PATH = "cleaned_books.csv"
RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}
def create_robust_session():
    """Configures a requests Session with automated retries and standard User-Agent headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False
    )
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))
    return session
# STEP 1: SCRAPING DATA (CATEGORY-FIRST TO AVOID PER-BOOK HTTP CALLS)
def scrape_books(min_books=60):
    scraped_data = []
    session = create_robust_session()
    print(f"Starting web scraping from {BASE_URL}...")
    try:
        response = session.get(BASE_URL, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        cat_nodes = soup.find("div", class_="side_categories").find("ul").find("ul").find_all("a")
        category_list = [(node.text.strip(), BASE_URL + node["href"]) for node in cat_nodes]
    except Exception as e:
        print(f"Failed to load index page: {e}")
        return pd.DataFrame()
    for cat_name, cat_url in category_list:
        if len(scraped_data) >= min_books:
            break
        current_url = cat_url
        while current_url and len(scraped_data) < min_books:
            try:
                res = session.get(current_url, timeout=10)
                if res.status_code != 200:
                    break
                cat_soup = BeautifulSoup(res.content, "html.parser")
                articles = cat_soup.find_all("article", class_="product_pod")
                for article in articles:
                    title = article.h3.a["title"]
                    price_text = article.find("p", class_="price_color").text 
                    rating_class = article.find("p", class_="star-rating")["class"]
                    rating_text = [c for c in rating_class if c != "star-rating"][0] if len(rating_class) > 1 else "Zero"       
                    availability_text = article.find("p", class_="instock availability").text.strip()
                    scraped_data.append({
                        "title": title,
                        "price_raw": price_text,
                        "rating_raw": rating_text,
                        "availability_raw": availability_text,
                        "category": cat_name
                    })
                    if len(scraped_data) >= min_books:
                        break
                next_button = cat_soup.find("li", class_="next")
                if next_button:
                    next_rel_url = next_button.a["href"]
                    current_url = current_url.rsplit('/', 1)[0] + '/' + next_rel_url
                else:
                    current_url = None
                time.sleep(0.1) 
            except requests.exceptions.RequestException as e:
                print(f"Error loading {current_url}: {e}")
                break
    print(f" Successfully scraped {len(scraped_data)} books without detail-page connection drops.")
    return pd.DataFrame(scraped_data)
# STEP 2: CLEANING, ENRICHMENT & CSV EXPORT
def clean_and_enrich_data(df, csv_path=CSV_FILE_PATH):
    print("Cleaning and enriching scraped data...")
    cleaned_rows = []
    for idx, row in df.iterrows():
        try:
            price_gbp = float(re.sub(r"[^\d.]", "", str(row["price_raw"])))
        except (ValueError, TypeError):
            price_gbp = None
        rating = RATING_MAP.get(str(row["rating_raw"]).strip().capitalize(), None)
        in_stock = 1 if "in stock" in str(row["availability_raw"]).lower() else 0
        category = str(row["category"]).strip() if row["category"] else "Uncategorized"
        title = str(row["title"]).strip()
        cleaned_rows.append({
            "title": title,
            "price_gbp": price_gbp,
            "rating": rating,
            "in_stock": in_stock,
            "category": category
        })
    clean_df = pd.DataFrame(cleaned_rows)
    if clean_df["price_gbp"].isnull().any():
        clean_df["price_gbp"].fillna(clean_df["price_gbp"].median(), inplace=True)
    if clean_df["rating"].isnull().any():
        clean_df["rating"].fillna(int(clean_df["rating"].median()), inplace=True)
    clean_df["rating"] = clean_df["rating"].astype(int)
    clean_df["price_inr"] = (clean_df["price_gbp"] * FIXED_GBP_TO_INR_RATE).round(2)
    clean_df.to_csv(csv_path, index=False)
    print(f"Cleaned data exported to CSV file: '{csv_path}'.")
    return clean_df
# STEP 3: DATABASE LOADING (SQLite)
def setup_and_load_db(clean_df, db_path=DB_NAME):
    print(f"Loading data into SQLite database at '{db_path}'...")
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name TEXT UNIQUE NOT NULL
    );
    """)
    cursor.execute("""
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
    """)
    unique_categories = clean_df["category"].unique()
    for cat in unique_categories:
        cursor.execute("INSERT INTO categories (category_name) VALUES (?);", (cat,))
    conn.commit()
    cursor.execute("SELECT category_name, category_id FROM categories;")
    cat_mapping = dict(cursor.fetchall())
    clean_df["category_id"] = clean_df["category"].map(cat_mapping)
    books_data = clean_df[["title", "price_gbp", "price_inr", "rating", "in_stock", "category_id"]].values.tolist()
    cursor.executemany("""
    INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
    VALUES (?, ?, ?, ?, ?, ?);
    """, books_data)
    conn.commit()
    print("SQLite database populated successfully.")
    return conn
# STEP 4: QUERY EXECUTION & PANDAS MERGE
def execute_queries_and_validations(conn):
    print("\n" + "="*50)
    print(" SQL QUERIES EXECUTION ")
    print("="*50)
    q1 = "SELECT title, price_gbp, price_inr FROM books WHERE in_stock = 1 ORDER BY price_inr DESC LIMIT 5;"
    print("--- Query 1: Top 5 Expensive Books (SELECT, WHERE, ORDER BY, LIMIT) ---")
    print(pd.read_sql_query(q1, conn).to_string(index=False))
    q2 = "SELECT DISTINCT rating FROM books ORDER BY rating ASC;"
    print("--- Query 2: Distinct Star Ratings (DISTINCT) ---")
    print(pd.read_sql_query(q2, conn).to_string(index=False))
    q3 = "SELECT title, price_gbp FROM books WHERE price_gbp BETWEEN 20.0 AND 40.0 ORDER BY price_gbp ASC LIMIT 5;"
    print("--- Query 3: Price Range £20 to £40 (BETWEEN) ---")
    print(pd.read_sql_query(q3, conn).to_string(index=False))
    q4 = "SELECT title, rating, price_inr FROM books WHERE rating IN (4, 5) ORDER BY rating DESC LIMIT 5;"
    print("--- Query 4: Ratings IN (4, 5) ---")
    print(pd.read_sql_query(q4, conn).to_string(index=False))
    q5 = """
    SELECT b.book_id, b.title, c.category_name, b.rating, b.price_gbp, b.price_inr
    FROM books b
    JOIN categories c ON b.category_id = c.category_id
    WHERE b.rating >= 4
    ORDER BY b.price_gbp DESC, b.book_id ASC
    LIMIT 10;
    """
    print("--- Query 5: Relational JOIN (Books + Categories) ---")
    df_sql_join = pd.read_sql_query(q5, conn)
    print(df_sql_join.to_string(index=False))
    print("="*50)
    print(" PANDAS PD.MERGE COMPARISON ")
    print("="*50)
    books_df = pd.read_sql_query("SELECT * FROM books;", conn)
    categories_df = pd.read_sql_query("SELECT * FROM categories;", conn)
    merged_df = pd.merge(books_df, categories_df, on="category_id", how="inner")
    pandas_result = (
        merged_df[merged_df["rating"] >= 4]
        .sort_values(by=["price_gbp", "book_id"], ascending=[False, True])
        [["book_id", "title", "category_name", "rating", "price_gbp", "price_inr"]]
        .head(10)
        .reset_index(drop=True)
    )
    print("--- Pandas pd.merge Output ---")
    print(pandas_result.to_string(index=False))
    pd.testing.assert_frame_equal(df_sql_join.reset_index(drop=True), pandas_result)
    print(" SQL JOIN matches Pandas pd.merge output perfectly!")
if __name__ == "__main__":
    raw_df = scrape_books(min_books=60)
    if not raw_df.empty:
        clean_df = clean_and_enrich_data(raw_df)
        db_conn = setup_and_load_db(clean_df)
        execute_queries_and_validations(db_conn)
        db_conn.close()
    else:
        print("[!] Scraping yielded no data. Please verify network connectivity.")
