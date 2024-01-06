from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
import random
import time
import requests
import pandas as pd
import re

"""Visit http://httpbin.org/get to get the headers for your computer/browser"""
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

def get_soup(url, retailer):
    try:
        match retailer:
            case "sephora":
                driver = webdriver.Chrome()
                driver.get(url)
                WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.XPATH, "//span[contains(@data-at, 'product_name')]")))
                page_content = driver.page_source
                driver.quit()
            case _:
                request = requests.get(url, headers=HEADERS) # add verify=False to arguments if in the office
                request.raise_for_status()
                time.sleep(random.random())
                page_content = request.text
        return BeautifulSoup(page_content, "html.parser")
    except Exception as e:
        print(f"Exception: Failed to connect to {url}\n{e}")
        return None

def scrape_product_page(url, retailer):
    brand_text = description_text = size_text = srp_text = markdown_text = sku_number_text = ""
    product_doc = get_soup(url, retailer)
    if product_doc:
        match retailer:
            case "sephora":
                brand = product_doc.find("a", {"data-at": "brand_name"})
                description = product_doc.find("span", {"data-at": "product_name"})
                size = product_doc.find("span", {"data-at": "sku_size_label"})
                if not size:
                    size = product_doc.find("div", {"data-at": "sku_name_label"})
                sku_number = re.search(r"(?<=skuId=)\d+", url)
                srp = product_doc.find("b", {"class": "css-p9xrit"})
                if not srp:
                    srp = product_doc.find("b", {"class": "css-0"})
                else:
                    markdown = product_doc.find("b", {"class": "css-5fq4jh"})
            case "ulta":
                brand = product_doc.find("span", {"class": "Text-ds Text-ds--body-1 Text-ds--left"})
                description = product_doc.find("span", {"class": "Text-ds Text-ds--title-5 Text-ds--left"})
                size = product_doc.find("span", {"class": "Text-ds Text-ds--body-3 Text-ds--left Text-ds--black"})
                sku_number = re.search(r"(?<=sku=)\d+", url)
                srp = product_doc.find("span", {"class": "Text-ds Text-ds--body-2 Text-ds--left Text-ds--neutral-600 Text-ds--line-through"})
                if not srp:
                    srp = product_doc.find("span", {"class": "Text-ds Text-ds--title-6 Text-ds--left Text-ds--black"})
                else:
                    markdown = product_doc.find("span", {"class": "Text-ds Text-ds--title-6 Text-ds--left Text-ds--magenta-500"})
            case "macys":
                brand = product_doc.find("a", {"data-auto": "product-brand"})
                description = product_doc.find("div", {"data-auto": "product-name"})
                size = product_doc.find("div", {"data-auto": "size-header"})
                sku_number = re.search(r"(?<=ID=)\d+", url)
                srp = product_doc.find("div", {"class": "c-strike"})
                if not srp:
                    srp = product_doc.find("div", {"class": "lowest-sale-price"})
                else:
                    markdown = product_doc.find("div", {"class": "lowest-sale-price"})
        if brand:
            brand_text = brand.text.strip()
        if description:
            description_text = description.text.strip()
        if size:
            size_text = size.text.strip()
        if sku_number:
            sku_number_text = sku_number.group(0)
        if srp:
            srp_text = srp.text.strip()
        if markdown:
            markdown_text = markdown.text.strip()
    return [{"Brand": brand_text,
             "Description": description_text,
             "Size": size_text,
             "SKU #": sku_number_text,
             "SRP": srp_text,
             "Markdown": markdown_text,
             "URL": url}]

def iterate_pages(urls, retailer):
    num_products = len(urls)
    products = []
    for i, url in enumerate(urls):
        print(f"Scraping {retailer} page {i + 1} of {num_products}")
        products += scrape_product_page(url, retailer)
    return products

if __name__ == "__main__":
    retailers = ["sephora", "ulta", "macys"]
    for retailer in retailers:
        urls = pd.read_csv(f"input/{retailer}_urls.csv", delimiter=",", header=None).iloc[:, 0].values.tolist()
        random.shuffle(urls)
        products = pd.DataFrame(iterate_pages(urls, retailer)).drop_duplicates()
        products.to_csv(f"output/{date.today()}_{retailer}_srps.csv", index=False)