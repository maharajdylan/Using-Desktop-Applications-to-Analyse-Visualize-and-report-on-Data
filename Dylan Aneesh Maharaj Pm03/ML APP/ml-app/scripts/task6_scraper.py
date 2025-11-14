import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"

all_books = []

# Loop through first 3 pages
for page in range(1, 4):  # pages 1, 2, 3
    url = BASE_URL.format(page)
    response = requests.get(url)
    response.encoding = 'utf-8'  # fix encoding issues
    soup = BeautifulSoup(response.text, "lxml")

    # Find all books on the page
    articles = soup.select("article.product_pod")

    for article in articles:
        # Title
        title_tag = article.select_one("h3 a[title]")
        title = title_tag["title"] if title_tag else None

        # Price
        price_tag = article.select_one("p.price_color")
        price = price_tag.text.strip() if price_tag else None

        # Rating
        rating_tag = article.select_one("p.star-rating")
        rating = None
        if rating_tag:
            rating_class = rating_tag.get("class", [])
            rating_map = {"One":1, "Two":2, "Three":3, "Four":4, "Five":5}
            for cls in rating_class:
                if cls in rating_map:
                    rating = rating_map[cls]

        # Link
        link_tag = article.select_one("h3 a")
        link = urljoin("http://books.toscrape.com/catalogue/", link_tag["href"]) if link_tag else None

        # Append book to list
        all_books.append({
            "title": title,
            "price": price,
            "rating": rating,
            "link": link
        })

print(f"Total books scraped: {len(all_books)}")

# Save to CSV
df = pd.DataFrame(all_books)
df.to_csv("books_multiple_pages.csv", index=False)
print("Data saved to books_multiple_pages.csv")

# Preview first 5 books
print(df.head())
