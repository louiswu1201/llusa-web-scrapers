from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
import requests
import pandas as pd
import re

"""Visit http://httpbin.org/get to get the headers for your computer/browser"""
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

def get_soup(url):
    """Get the BeautifulSoup object for a given URL."""
    result = requests.get(url, headers=HEADERS, verify=False) # optional: verify=False
    result.raise_for_status()
    return BeautifulSoup(result.text, "html.parser")

def get_driver(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=Options())
    driver.get(url)
    return driver

def scrape_product_page(url):
    results = []
    product_page = get_driver(url)
    try:
        brand = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--body-1 Text-ds--left')]")
        brand_text = brand.text.strip()
    except:
        brand_text = ""
    try:
        description = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--title-5 Text-ds--left')]")
        description_text = description.text.strip()
    except:
        description_text = ""
    try:
        wait = WebDriverWait(product_page, 2)
        clickable_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'Button--unstyled Pill')]")))
        buttons = product_page.find_elements(By.XPATH, "//button[contains(@class, 'Button--unstyled Pill')]")
        for button in buttons:
            wait = WebDriverWait(product_page, 2)
            clickable_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'Button--unstyled Pill')]")))
            button.click()
            # print(button.get_attribute("innerHTML"))
            try:
                size = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--body-3 Text-ds--left Text-ds--black')]")
                size_text = size.text.strip()
            except:
                size_text = ""
            try:
                sku_number = product_page.find_element(By.XPATH, "//p[contains(@class, 'Text-ds Text-ds--body-3 Text-ds--left')]")
                sku_number_text = sku_number.text.strip()
                sku_number_text = re.search(r"\d+", sku_number_text).group()
            except:
                sku_number_text = ""
            try:
                original_price = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--body-2 Text-ds--left Text-ds--neutral-600 Text-ds--line-through')]")
                original_price_text = original_price.text.strip()
                original_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", original_price_text)
                if original_price_match:
                    original_price_text = original_price_match.group(0)
            except:
                try:
                    original_price = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--title-6 Text-ds--left Text-ds--black')]")
                    original_price_text = original_price.text.strip()
                    original_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", original_price_text)
                    if original_price_match:
                        original_price_text = original_price_match.group(0)
                except:
                    original_price_text = ""
            try:
                sale_price = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--title-6 Text-ds--left Text-ds--magenta-500')]")
                sale_price_text = sale_price.text.strip()
                sale_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", sale_price_text)
                if sale_price_match:
                    sale_price_text = sale_price_match.group(0)
            except:
                sale_price_text = ""
            print(brand_text + description_text + size_text + sku_number_text + original_price_text + sale_price_text)
            results += [{"Brand": brand_text,
                         "Description": description_text,
                         "Size": size_text,
                         "SKU #": sku_number_text,
                         "Original Price": original_price_text,
                         "Sale Price": sale_price_text,
                         "URL": url}]
    except:
        try:
            size = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--body-3 Text-ds--left Text-ds--black')]")
            size_text = size.text.strip()
        except:
            size_text = ""
        try:
            sku_number = product_page.find_element(By.XPATH, "//p[contains(@class, 'Text-ds Text-ds--body-3 Text-ds--left')]")
            sku_number_text = sku_number.text.strip()
            sku_number_text = re.search(r"\d+", sku_number_text).group()
        except:
            sku_number_text = ""
        try:
            original_price = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--body-2 Text-ds--left Text-ds--neutral-600 Text-ds--line-through')]")
            original_price_text = original_price.text.strip()
            original_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", original_price_text)
            if original_price_match:
                original_price_text = original_price_match.group(0)
        except:
            try:
                original_price = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--title-6 Text-ds--left Text-ds--black')]")
                original_price_text = original_price.text.strip()
                original_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", original_price_text)
                if original_price_match:
                    original_price_text = original_price_match.group(0)
            except:
                original_price_text = ""
        try:
            sale_price = product_page.find_element(By.XPATH, "//span[contains(@class, 'Text-ds Text-ds--title-6 Text-ds--left Text-ds--magenta-500')]")
            sale_price_text = sale_price.text.strip()
            sale_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", sale_price_text)
            if sale_price_match:
                sale_price_text = sale_price_match.group(0)
        except:
            sale_price_text = ""
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