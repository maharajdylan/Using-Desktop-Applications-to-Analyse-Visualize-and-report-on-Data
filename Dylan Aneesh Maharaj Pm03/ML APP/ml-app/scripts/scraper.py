# task3_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

# Target website
BASE_URL = "http://books.toscrape.com/catalogue/page-{}.html"

# Storage for scraped data
titles = []
prices = []
ratings = []
availabilities = []

# Scrape first 5 pages (can increase later)
for page in range(1, 6):
    url = BASE_URL.format(page)
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page {page}")
        continue

    soup = BeautifulSoup(response.text, "lxml")

    books = soup.find_all("article", class_="product_pod")

    for book in books:
        # Title
        title = book.h3.a["title"]
        titles.append(title)

        # Price
        price = book.find("p", class_="price_color").text.strip()
        prices.append(price)

        # Rating (stored as a class like 'star-rating Three')
        rating = book.p["class"][1]
        ratings.append(rating)

        # Availability
        availability = book.find("p", class_="instock availability").text.strip()
        availabilities.append(availability)

# Create DataFrame
data = pd.DataFrame({
    "Title": titles,
    "Price": prices,
    "Rating": ratings,
    "Availability": availabilities
})

# Show first 10 results in terminal
print(data.head(10))

# Save to CSV
data.to_csv("books_scraped.csv", index=False, encoding="utf-8")

print("\n✅ Scraping complete! Data saved to books_scraped.csv")
