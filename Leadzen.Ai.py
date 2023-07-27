import csv
import requests
from bs4 import BeautifulSoup
import time

# Part 1: Scrape product listings
base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_"
pages_to_scrape = 20

def scrape_product_listings(page_url):
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, "html.parser")
    product_items = soup.select(".s-asin")
    
    products = []
    for item in product_items:
        url = "https://www.amazon.in" + item.find("a", class_="a-link-normal")["href"]
        name = item.find("span", class_="a-text-normal").text
        price = item.select_one(".a-offscreen")
        price = price.text.strip() if price else "N/A"
        rating = item.select_one(".a-icon-alt")
        rating = rating.text if rating else "N/A"
        num_reviews = item.select_one(".a-size-base")
        num_reviews = num_reviews.text if num_reviews else "N/A"
        products.append({"url": url, "name": name, "price": price, "rating": rating, "num_reviews": num_reviews})
    return products

all_products = []
for page_num in range(1, pages_to_scrape + 1):
    page_url = base_url + str(page_num)
    products = scrape_product_listings(page_url)
    all_products.extend(products)
    time.sleep(2)  # Add a delay to avoid overwhelming the server

# Part 2: Scrape detailed product information
def scrape_product_details(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    description = soup.select_one("meta[name='description']")["content"]
    asin = soup.find("th", text="ASIN").find_next_sibling("td").text.strip()
    product_description = soup.select_one("#productDescription p")
    product_description = product_description.text.strip() if product_description else "N/A"
    manufacturer = soup.find("a", {"id": "bylineInfo"})
    manufacturer = manufacturer.text.strip() if manufacturer else "N/A"
    
    return {"description": description, "asin": asin, "product_description": product_description, "manufacturer": manufacturer}

# Scrape additional details for the first 200 products (limiting to 200 to avoid excessively long execution times)
total_products_to_scrape = 200
final_data = []
for idx, product in enumerate(all_products[:total_products_to_scrape], 1):
    print(f"Scraping product {idx}/{total_products_to_scrape}...")
    product_details = scrape_product_details(product["url"])
    final_data.append({**product, **product_details})
    time.sleep(2)  # Add a delay to avoid overwhelming the server

# Export data to a CSV file
csv_file = "amazon_products.csv"
field_names = ["url", "name", "price", "rating", "num_reviews", "description", "asin", "product_description", "manufacturer"]

with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=field_names)
    writer.writeheader()
    writer.writerows(final_data)

print(f"Scraping completed. Data saved to {csv_file}.")
