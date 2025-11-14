from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd
import time

# Path to chromedriver 
service = Service(r"C:\Users\Geeks5\ML APP\ml-app\chromedriver.exe")
driver = webdriver.Chrome(service=service)

# Open the website
driver.get("http://books.toscrape.com/catalogue/page-1.html")
time.sleep(2)  # wait for page to load

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
        time.sleep(2)  # wait for the next page to load
    except:
        break  # no more pages

# Close the browser
driver.quit()

# Save to CSV
df = pd.DataFrame(all_books)
df.to_csv("books_selenium.csv", index=False)
print(f"Scraped {len(all_books)} books using Selenium")
print(df.head())
