from bs4 import BeautifulSoup
from datetime import date
import requests
import pandas as pd

"""Visit http://httpbin.org/get to get the headers for your computer/browser"""
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

def get_soup(url):
    """Get the BeautifulSoup object for a given URL."""
    result = requests.get(url, headers=HEADERS) # optional: verify=False
    result.raise_for_status()
    return BeautifulSoup(result.text, "html.parser")

def scrape_results(url, page_num):
    """Scrape the search results for a given URL and page number."""
    doc = get_soup(url + f"?pageNumber={page_num}")
    tiles = doc.find_all("div", {"class": "result-tile-below"})
    results = []
    for tile in tiles:
        for element in tile.contents:
            product_url = element.find("a")
            if product_url is not None:
                url_text = "https://www.dillards.com" + product_url["href"]
                product_doc = get_soup(url_text)
                product_titles = product_doc.find_all("h2", {"class": "product__title m-b-10"})
                product_titles.extend(product_doc.find_all("h1", {"class": "product__title m-b-10"}))
                if product_titles:
                    for product_title in product_titles:
                        item = product_title.parent
                        brands = item.find_all("span", {"class": "product__title--brand m-b-10"})
                        descriptions = item.find_all("span", {"class": "product__title--desc m-b-10"})
                        item_numbers = item.find_all("span", {"class": "item-number"})
                        sizes = item.find_all("span", {"class": "one-option"})
                        prices = item.find_all("span", {"class": "price"})
                        brand_text = description_text = item_number_text = size_text = price_text = ""
                        if brands:
                            for index, brand in enumerate(brands):
                                if index == 0:
                                    brand_text += brand.text
                                else:
                                    brand_text += "_" + brand.text
                        if descriptions:
                            for index, description in enumerate(descriptions):
                                if index == 0:
                                    description_text += description.text
                                else:                                
                                    description_text += "_" + description.text
                        if item_numbers:
                            for index, item_number in enumerate(item_numbers):
                                if index == 0:
                                    item_number_text += item_number.text.split("#")[1]
                                else:
                                    item_number_text += "_" + item_number.text.split("#")[1]
                        if sizes:
                            for index, size in enumerate(sizes):
                                if index == 0:
                                    size_text += size.text
                                else:
                                    size_text += "_" + size.text
                        if prices:
                            for index, price in enumerate(prices):
                                if index == 0:
                                    price_text += price.text
                                else:
                                    price_text += "_" + price.text
                            if price_text.find("-") < 0:
                                results += [{"Brand": brand_text,
                                             "Description": description_text,
                                             "Item #": item_number_text,
                                             "Size": size_text,
                                             "Price": price_text,
                                             "URL": url_text}]
                            else:
                                sizes_prices = item.find_all("button", {"class": "available"})
                                sizes_prices.extend(item.find_all("option", {"class": "available"}))
                                sizes_prices.extend(product_doc.find_all("div", {"class": "col-sm-3 productItem__description"}))
                                if sizes_prices:
                                    for size_price in sizes_prices:
                                        list_text = size_price.text.split("$")
                                        size_text = list_text[0].strip("- ")
                                        price_text = "$" + "$".join(list_text[1:]) if len(list_text) >= 2 else price_text
                                        results += [{"Brand": brand_text,
                                                     "Description": description_text,
                                                     "Item #": item_number_text,
                                                     "Size": size_text,
                                                     "Price": price_text,
                                                     "URL": url_text}]
                else:
                    product_titles = product_doc.find_all("div", {"class": "col-4 col-sm-3 chanelItemDesc"})
                    if product_titles:
                        for product_title in product_titles:
                            item = product_title.parent
                            brands = item.find_all("span", {"class": "chanelTitle1"})
                            descriptions = item.find_all("span", {"class": "chanelTitle2"})
                            descriptions.extend(item.find_all("span", {"class": "chanelTitle3"}))
                            item_numbers = product_doc.find_all("span", {"class": "item-number"})
                            sizes = item.find_all("span", {"class": None})
                            prices = item.find_all("span", {"class": "price"})
                            brand_text = description_text = item_number_text = size_text = price_text = ""
                            if brands:
                                for index, brand in enumerate(brands):
                                    if index == 0:
                                        brand_text += brand.text
                                    else:
                                        brand_text += "_" + brand.text
                            if descriptions:
                                for index, description in enumerate(descriptions):
                                    if index == 0:
                                        description_text += description.text
                                    else:                                
                                        description_text += "_" + description.text
                            if item_numbers:
                                for index, item_number in enumerate(item_numbers):
                                    if index == 0:
                                        item_number_text += item_number.text.split("#")[1]
                                    else:
                                        item_number_text += "_" + item_number.text.split("#")[1]
                            if sizes:
                                for index, size in enumerate(sizes):
                                    if index == 0:
                                        size_text += size.text
                                    else:
                                        size_text += "_" + size.text
                            if prices:
                                for index, price in enumerate(prices):
                                    if index == 0:
                                        price_text += price.text
                                    else:
                                        price_text += "_" + price.text
                            results += [{"Brand": brand_text,
                                         "Description": description_text,
                                         "Item #": item_number_text,
                                         "Size": size_text,
                                         "Price": price_text,
                                         "URL": url_text}]
    return(results)
        
def iterate_pages(url):
    """Iterate through all pages of search results until the last page."""
    current_page = 1
    results = []
    while True:
        print(current_page)
        page_results = scrape_results(url, current_page)
        results += page_results
        soup = get_soup(url + f"?pageNumber={current_page}")
        next_page_link = soup.find("div", {"class": "icon i-arrow-right"})
        if next_page_link is None:
            print("Done")
            break
        current_page += 1
    return(results)

if __name__ == "__main__":
    category = "skincare"
    products = iterate_pages(f"https://www.dillards.com/c/beauty-{category}")
    products = pd.DataFrame(products)
    products = products.drop_duplicates()
    products.to_csv(f"dillards_{category}_{date.today()}.csv", index=False)