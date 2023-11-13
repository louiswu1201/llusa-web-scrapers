from bs4 import BeautifulSoup
from datetime import date
import requests
import pandas as pd
import re

"""Visit http://httpbin.org/get to get the headers for your computer/browser"""
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

def get_soup(url):
    """Get the BeautifulSoup object for a given URL."""
    result = requests.get(url, headers=HEADERS) # optional: verify=False
    result.raise_for_status()
    return BeautifulSoup(result.text, "html.parser")

def scrape_results(url, page_num):
    """Scrape the search results for a given URL and page number."""
    doc = get_soup(url[0] + f"/Pageindex/{page_num}" + url[1])
    tiles = doc.find_all("li", {"class": "productThumbnailItem"})
    results = []
    if tiles:
        for tile in tiles:
            product_description = tile.find("div", {"class": "productDescription"})
            if product_description:
                regular_price = product_description.find_all("span", {"class": "regular"})
                price_text = ""
                for price in regular_price:
                    price_text += price.text.strip()
                if price_text.find("-") < 0:
                    price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", price_text)
                    if price_match:
                        price_text = price_match.group()
                    brand = product_description.find("div", {"class": "productBrand"})
                    if brand:
                        brand_text = brand.text.strip()
                    else:
                        brand_text = ""
                    sub_brand = product_description.find("div", {"class": "productSubDesc"})
                    if sub_brand:
                        sub_brand_text = sub_brand.text.strip()
                    else:
                        sub_brand_text = ""
                    description_text = product_description.find("a")["title"].strip()
                    product_url = product_description.find("a")["href"]
                    id_match = re.search(r"ID=(\d+)", product_url)
                    if id_match:
                        product_url_id = id_match.group(1)
                    else:
                        product_url_id = ""
                    discount_price = product_description.find("span", {"class": "discount"})
                    if discount_price:
                        discount_text = discount_price.text.strip()
                    else:
                        discount_text = ""
                    discount_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", discount_text)
                    if discount_match:
                        if "Only" in discount_text:
                            price_text = discount_match.group()
                            discount_text = ""
                        else:
                            discount_text = discount_match.group()
                    results += [{"Brand": brand_text,
                                 "Description": sub_brand_text + " " + description_text,
                                 "URL ID #": product_url_id,
                                 "Regular Price": price_text,
                                 "Discounted Price": discount_text,
                                 "URL": "http://www.macys.com" + product_url}]
    return(results)
        
def iterate_pages(url):
    """Iterate through all pages of search results until the last page."""
    current_page = 1
    results = []
    while True:
        print(current_page)
        page_results = scrape_results(url, current_page)
        results += page_results
        soup = get_soup(url[0] + f"/Pageindex/{current_page}" + url[1])
        next_page_link = soup.find("li", {"class": "pagination-next"})
        if next_page_link is None:
            break
        current_page += 1
    return(results)

if __name__ == "__main__":
    products = iterate_pages(("https://www.macys.com/shop/makeup-and-perfume/skin-care", "?id=30078"))
    products = pd.DataFrame(products)
    products = products.drop_duplicates()
    products.to_csv(f"macys_skincare_{date.today()}.csv", index=False)