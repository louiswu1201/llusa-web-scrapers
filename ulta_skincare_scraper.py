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

def scrape_product_page(url):
    results = []
    brand_text = description_text = size_text = original_price_text = sale_price_text = sku_number_text = ""
    # TODO: use selenium to click every pill selector button.
    product_doc = get_soup(url)
    buttons = product_doc.find_all("div", {"class": "PillSelector__pills"})
    product_information = product_doc.find("div", {"class": "ProductInformation"})
    if product_information:
        brand_results = product_information.find_all("span", {"class": "Text-ds Text-ds--body-1 Text-ds--left"})
        brand_text = ""
        if brand_results:
            for brand in brand_results:
                brand_text += brand.text.strip()
        description_results = product_information.find_all("span", {"class": "Text-ds Text-ds--title-5 Text-ds--left"})
        description_text = ""
        if description_results:
            for description in description_results:
                description_text += description.text.strip()
        sku_numbers = product_information.find_all("span", {"class": "Text-ds Text-ds--body-3 Text-ds--left"})
        sku_number_text = ""
        if sku_numbers:
            for sku_number in sku_numbers:
                if "Item" in sku_number.text:
                    sku_number_text += sku_number.text
            sku_number_match = re.search(r"\d+", sku_number_text)
            if sku_number_match:
                sku_number_text = sku_number_match.group()
    product_size = product_doc.find("div", {"class": "ProductDimension"})
    if product_size:
        size = product_size.find("span", {"class": "Text-ds Text-ds--body-3 Text-ds--left Text-ds--black"})
        if size:
            size_text = size.text.strip()
    product_pricing = product_doc.find("div", {"class": "ProductPricing"})
    if product_pricing:
        original_price = product_pricing.find("span", {"class": "Text-ds Text-ds--body-2 Text-ds--left Text-ds--neutral-600 Text-ds--line-through"})
        if original_price:
            original_price_text = original_price.text.strip()
            sale_price = product_pricing.find("span", {"class": "Text-ds Text-ds--title-6 Text-ds--left Text-ds--magenta-500"})
            if sale_price:
                sale_price_text = sale_price.text.strip()
        else:
            original_price_text = product_pricing.text.strip()
    results += [{"Brand": brand_text,
                 "Description": description_text,
                 "Size": size_text,
                 "SKU #": sku_number_text,
                 "Original Price": original_price_text,
                 "Sale Price": sale_price_text,
                 "URL": url}]
    return results

def scrape_brand_page(url):
    """Scrape the search results for a given URL and page number."""
    doc = get_soup(url)
    results = []
    tiles = doc.find_all("div", {"class": "ProductCard"})
    if tiles:
        for tile in tiles:
            brand_text = description_text = size_text = original_price_text = sale_price_text = url_text = sku_number_text = ""
            brand = tile.find("span", {"class": "ProductCard__brand"})
            if brand:
                brand_text = brand.text.strip()
            description = tile.find("span", {"class": "ProductCard__product"})
            if description:
                description_text = description.text.strip()
            # on_sale = tile.find("div", {"class": "ProductCard__badge"})
            url = tile.find("a")
            if url:
                url_text = url["href"].strip()
            sku_number_match = re.search(r"\bsku=(\d+)\b", url_text)
            if sku_number_match:
                sku_number_text = sku_number_match.group(1)
            original_price = tile.find("span", {"class": "Text-ds Text-ds--body-2 Text-ds--left Text-ds--black"})
            if original_price:
                original_price_text = original_price.text.strip()
            else:
                original_price = tile.find("span", {"class": "Text-ds Text-ds--body-2 Text-ds--left Text-ds--neutral-600 Text-ds--line-through"})
                if original_price:
                    original_price_text = original_price.text.strip()
            sale_price = tile.find("span", {"class": "Text-ds Text-ds--body-2 Text-ds--left Text-ds--magenta-500"})
            if sale_price:
                sale_price_text = sale_price.text.strip()
            if original_price_text.find("-") < 0:
                results += [{"Brand": brand_text,
                            "Description": description_text,
                            "Size": size_text,
                            "SKU #": sku_number_text,
                            "Original Price": original_price_text,
                            "Sale Price": sale_price_text,
                            "URL": url_text}]
            else:
                results += scrape_product_page(url_text)
    return results
        
def iterate_pages(brands):
    """Iterate through all brand pages."""
    results = []
    for brand in brands:
        print(brand)
        page_results = scrape_brand_page(f"http://www.ulta.com/brand/{brand}?category=skin-care")
        results += page_results
    return results

if __name__ == "__main__":
    brands = ["ahava",
              "belif",
              "bio-oil",
              "bobbi-brown",
              "burts-bees",
              "chanel",
              "clarins",
              "clinique",
              "cosrx",
              "derma-e",
              "dermalogica",
              "dior",
              "drunk-elephant",
              "elf-cosmetics",
              "elemis",
              "first-aid-beauty",
              "fresh",
              "glamglow",
              "good-molecules",
              "grande-cosmetics",
              "hempz",
              "honest-beauty",
              "jack-black",
              "kate-somerville",
              "kopari-beauty",
              "estee-lauder",
              "mac",
              "mario-badescu",
              "murad",
              "origins",
              "osea",
              "patchology",
              "peach-lily",
              "peter-thomas-roth",
              "philosophy",
              "proactiv",
              "shiseido",
              "st-tropez",
              "strivectin",
              "sun-bum",
              "sunday-riley",
              "supergoop",
              "ordinary",
              "tonymoly",
              "tula"]
    products = iterate_pages(brands)
    products = pd.DataFrame(products)
    products = products.drop_duplicates()
    products.to_csv(f"ulta_skincare_{date.today()}.csv", index=False)
    print("Done")