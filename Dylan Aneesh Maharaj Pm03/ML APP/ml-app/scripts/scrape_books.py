# scrape_books.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import random
import csv
import os
import pandas as pd
import matplotlib.pyplot as plt
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://books.toscrape.com/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LearningBot/1.0; +https://example.com/bot)"
}

# --- Helpers: session with retries ---
def create_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    retries = Retry(total=3, backoff_factor=0.3, status_forcelist=(500,502,504))
    s.mount("https://", HTTPAdapter(max_retries=retries))
    return s

# --- Regex helpers ---
price_re = re.compile(r"£\s*([0-9]+\.[0-9]{2})")
rating_map = {"One":1, "Two":2, "Three":3, "Four":4, "Five":5}

def extract_price(text):
    m = price_re.search(text)
    return float(m.group(1)) if m else None

def extract_rating_from_tag(tag):
    # tag like <p class="star-rating Three">...
    classes = tag.get("class", [])
    for c in classes:
        if c in rating_map:
            return rating_map[c]
    return None

# --- Parse listing page ---
def parse_listing_page(soup, page_url, session):
    books = []
    articles = soup.select("article.product_pod")
    for art in articles:
        a = art.select_one("h3 a")
        title = a.get("title", a.text.strip())
        # product page url is relative
        product_href = a.get("href")
        product_url = urljoin(page_url, product_href)

        price_tag = art.select_one("p.price_color")
        price_text = price_tag.text.strip() if price_tag else ""
        price = extract_price(price_text)

        rating_tag = art.select_one("p.star-rating")
        rating = extract_rating_from_tag(rating_tag) if rating_tag else None

        # Go to product detail page to fetch number of reviews (and more)
        try:
            resp = session.get(product_url, timeout=10)
            if resp.status_code == 200:
                detail_soup = BeautifulSoup(resp.text, "lxml")
                # The product details are in a table: <th>Number of reviews</th><td>...</td>
                num_reviews = None
                table_th = detail_soup.find("th", string=re.compile("Number of reviews", re.I))
                if table_th:
                    td = table_th.find_next_sibling("td")
                    if td:
                        try:
                            num_reviews = int(td.text.strip())
                        except:
                            num_reviews = None
                # alternate: look for "product_page" info if different layout
            else:
                num_reviews = None
        except Exception as e:
            print("Detail page fetch failed:", e)
            num_reviews = None

        books.append({
            "title": title,
            "product_url": product_url,
            "price": price,
            "rating": rating,
            "num_reviews": num_reviews,
        })

        # polite pause
        time.sleep(random.uniform(0.5, 1.2))

    return books

# --- Main scrape function (scrapes first N pages) ---
def scrape_books(pages=3, output_csv="../data/books.csv"):
    session = create_session()
    results = []

    for page in range(1, pages+1):
        if page == 1:
            url = BASE
        else:
            # second+ pages on this site
            url = urljoin(BASE, f"catalogue/page-{page}.html")

        print(f"Fetching page {page}: {url}")
        r = session.get(url, timeout=10)
        print("Status:", r.status_code)
        if r.status_code != 200:
            print("Failed to fetch page", page)
            continue

        # preview HTML
        print("HTML preview:", r.text[:500].replace("\n"," ") + "...\n")

        soup = BeautifulSoup(r.text, "lxml")
        page_books = parse_listing_page(soup, url, session)
        results.extend(page_books)

        # polite pause between pages
        time.sleep(random.uniform(1.0, 2.0))

    # ensure output folder exists
    outdir = os.path.dirname(output_csv)
    if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)

    # Save to CSV
    keys = ["title", "product_url", "price", "rating", "num_reviews"]
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"Saved {len(results)} rows to {output_csv}")
    return output_csv

# --- Data cleaning + analysis with pandas (Task 9 & 10) ---
def analyze_and_plot(csv_path="../data/books.csv"):
    df = pd.read_csv(csv_path)
    print(df.info())
    print(df.head())

    # If price is not numeric (maybe None), ensure numeric
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").astype("Int64")
    df["num_reviews"] = pd.to_numeric(df["num_reviews"], errors="coerce").astype("Int64")

    print("\nSummary stats:")
    print(df.describe(include="all"))

    # Plot 1: bar chart average price per rating
    avg_by_rating = df.groupby("rating")["price"].mean().sort_index()
    plt.figure()
    avg_by_rating.plot.bar()
    plt.title("Average price per rating")
    plt.xlabel("Rating (stars)")
    plt.ylabel("Average price (GBP)")
    plt.tight_layout()
    plt.savefig("../data/avg_price_per_rating.png")
    print("Saved plot ../data/avg_price_per_rating.png")

    # Plot 2: histogram of prices
    plt.figure()
    df["price"].dropna().plot.hist(bins=20)
    plt.title("Distribution of product prices")
    plt.xlabel("Price (GBP)")
    plt.tight_layout()
    plt.savefig("../data/price_histogram.png")
    print("Saved plot ../data/price_histogram.png")

    # Also print the dataframe head cleaned
    print(df.head())

if __name__ == "__main__":
    csv_path = scrape_books(pages=3, output_csv="../data/books.csv")
    analyze_and_plot(csv_path)
