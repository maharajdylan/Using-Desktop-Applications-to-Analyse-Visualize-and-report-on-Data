import requests
from bs4 import BeautifulSoup

url = "http://books.toscrape.com/"

response = requests.get(url)
print("Status code:", response.status_code)

soup = BeautifulSoup(response.text, "lxml")

# Find all books
books = soup.select("article.product_pod")
print("Found books:", len(books))

# Print first book details
first_book = books[0]
title = first_book.h3.a["title"]
price = first_book.select_one("p.price_color").text
rating = first_book.p["class"][1]

print("Title:", title)
print("Price:", price)
print("Rating:", rating)
