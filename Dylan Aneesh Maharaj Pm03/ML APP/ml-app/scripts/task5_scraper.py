import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "http://books.toscrape.com/"

# Request page
response = requests.get(BASE_URL)
response.encoding = 'utf-8'  # fix encoding issues
soup = BeautifulSoup(response.text, "lxml")

# --- TASK 5: Implement selectors ---

# 1️⃣ Element selectors: select all <article> elements
articles = soup.find_all("article")
print(f"Found {len(articles)} articles using element selector.")

# 2️⃣ Class selectors: select articles by class "product_pod"
articles_class = soup.select("article.product_pod")
print(f"Found {len(articles_class)} articles using class selector.")

# 3️⃣ Attribute selectors: select <a> elements with title attribute
titles = soup.select("article.product_pod h3 a[title]")
print("First 5 titles using attribute selector:")
for t in titles[:5]:
    print("-", t["title"])

# --- Extract data for all books into a structured format ---
books_data = []

for article in articles_class:
    # Title (attribute selector)
    title_tag = article.select_one("h3 a[title]")
    title = title_tag["title"] if title_tag else None

    # Price (class selector)
    price_tag = article.select_one("p.price_color")
    price = price_tag.text.strip() if price_tag else None

    # Rating (class selector, map class name to number)
    rating_tag = article.select_one("p.star-rating")
    rating = None
    if rating_tag:
        rating_class = rating_tag.get("class", [])
        rating_map = {"One":1, "Two":2, "Three":3, "Four":4, "Five":5}
        for cls in rating_class:
            if cls in rating_map:
                rating = rating_map[cls]

    # Link (attribute selector)
    link_tag = article.select_one("h3 a")
    link = urljoin(BASE_URL, link_tag["href"]) if link_tag else None

    books_data.append({
        "title": title,
        "price": price,
        "rating": rating,
        "link": link
    })

# Print first 5 entries
print("\nFirst 5 books extracted:")
for b in books_data[:5]:
    print(b)
