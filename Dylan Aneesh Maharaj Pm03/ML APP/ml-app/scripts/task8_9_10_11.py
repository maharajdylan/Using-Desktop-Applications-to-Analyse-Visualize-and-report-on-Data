# Complete Books Scraper with Cleaning, CSV, and Visualization

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import re
import time
import matplotlib.pyplot as plt

# -------------------------
# 1. Setup Selenium
# -------------------------
service = Service(r"C:\Users\Geeks5\ML APP\ml-app\chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Open the website
driver.get("http://books.toscrape.com/catalogue/page-1.html")
time.sleep(2)

all_books = []

# Loop through first 3 pages using "Next" button
for _ in range(3):
    soup = BeautifulSoup(driver.page_source, "lxml")
    articles = soup.select("article.product_pod")

    for article in articles:
        title_tag = article.select_one("h3 a[title]")
        title = title_tag["title"] if title_tag else None

        price_tag = article.select_one("p.price_color")
        price = price_tag.text.strip() if price_tag else None

        rating_tag = article.select_one("p.star-rating")
        rating = None
        if rating_tag:
            rating_class = rating_tag.get("class", [])
            rating_map = {"One":1, "Two":2, "Three":3, "Four":4, "Five":5}
            for cls in rating_class:
                if cls in rating_map:
                    rating = rating_map[cls]

        link_tag = article.select_one("h3 a")
        link = urljoin("http://books.toscrape.com/catalogue/", link_tag["href"]) if link_tag else None

        all_books.append({
            "title": title,
            "price": price,
            "rating": rating,
            "link": link
        })

    # Click the "Next" button if exists
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, "li.next a")
        next_button.click()
        time.sleep(2)
    except:
        break

# Close browser
driver.quit()

# -------------------------
# 2. Save raw data
# -------------------------
df = pd.DataFrame(all_books)
df.to_csv("books_selenium.csv", index=False)
print(f"Scraped {len(all_books)} books. Saved to books_selenium.csv")

# -------------------------
# 3. Clean data with regex
# -------------------------
df['price'] = df['price'].apply(lambda x: float(re.sub(r'[^\d.]', '', x)))
df['rating'] = df['rating'].astype(int)

df.to_csv("books_cleaned.csv", index=False)
print("Cleaned data saved to books_cleaned.csv")
print(df.head())

# -------------------------
# 4. Visualization
# -------------------------

# Bar chart: Average price per rating
avg_price_per_rating = df.groupby('rating')['price'].mean()
plt.figure(figsize=(8,5))
avg_price_per_rating.plot(kind='bar', color='skyblue')
plt.title("Average Book Price per Rating")
plt.xlabel("Rating")
plt.ylabel("Average Price (£)")
plt.xticks(rotation=0)
plt.show()

# Histogram: Distribution of book prices
plt.figure(figsize=(8,5))
plt.hist(df['price'], bins=15, color='salmon', edgecolor='black')
plt.title("Distribution of Book Prices")
plt.xlabel("Price (£)")
plt.ylabel("Number of Books")
plt.show()

