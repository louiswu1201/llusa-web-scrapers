import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
import time
import re

def get_driver(url):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=Options())
    driver.get(url)
    return driver

def scrape_product_page(url):
    results = []
    product_page = get_driver(url)
    try:
        brand = product_page.find_element(By.XPATH, "//a[contains(@data-at, 'brand_name')]")
        brand_text = brand.text.strip()
    except Exception:
        brand_text = ""
    try:
        description = product_page.find_element(By.XPATH, "//span[contains(@data-at, 'product_name')]")
        description_text = description.text.strip()
    except Exception:
        description_text = ""
    try:
        wait = WebDriverWait(product_page, 2)
        clickable_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@data-at, 'swatch')]")))
        buttons = product_page.find_elements(By.XPATH, "//button[contains(@data-at, 'swatch')]")
        for button in buttons:
            button.click()
            try:
                size = product_page.find_element(By.XPATH, "//div[contains(@data-at, 'sku_name_label')]")
                size_text = size.text.strip()
            except Exception:
                size_text = ""
            try:
                sku_number = product_page.find_element(By.XPATH, "//p[contains(@data-at, 'item_sku')]")
                sku_number_text = sku_number.text.strip()
                sku_number_text = re.search(r"\d+", sku_number_text).group()
            except Exception:
                sku_number_text = ""
            try:
                original_price = product_page.find_element(By.XPATH, "//b[contains(@class, 'css-p9xrit')]")
                original_price_text = original_price.text.strip()
                original_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", original_price_text)
                if original_price_match:
                    original_price_text = original_price_match.group(0)
            except Exception:
                try:
                    original_price = product_page.find_element(By.XPATH, "//span[contains(@class, 'css-18jtttk')]")
                    original_price_text = original_price.text.strip()
                    original_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", original_price_text)
                    if original_price_match:
                        original_price_text = original_price_match.group(0)
                except Exception:
                    original_price_text = ""
            try:
                sale_price = product_page.find_element(By.XPATH, "//b[contains(@class, 'css-5fq4jh')]")
                sale_price_text = sale_price.text.strip()
                sale_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", sale_price_text)
                if sale_price_match:
                    sale_price_text = sale_price_match.group(0)
            except Exception:
                sale_price_text = ""
            results += [{"Brand": brand_text,
                         "Description": description_text,
                         "Size": size_text,
                         "SKU #": sku_number_text,
                         "Original Price": original_price_text,
                         "Sale Price": sale_price_text,
                         "URL": url}]
    except Exception:
        try:
            size = product_page.find_element(By.XPATH, "//div[contains(@data-at, 'sku_name_label')]")
            size_text = size.text.strip()
        except Exception:
            size_text = ""
        try:
            sku_number = product_page.find_element(By.XPATH, "//p[contains(@data-at, 'item_sku')]")
            sku_number_text = sku_number.text.strip()
            sku_number_text = re.search(r"\d+", sku_number_text).group()
        except Exception:
            sku_number_text = ""
        try:
            original_price = product_page.find_element(By.XPATH, "//b[contains(@class, 'css-p9xrit')]")
            original_price_text = original_price.text.strip()
            original_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", original_price_text)
            if original_price_match:
                original_price_text = original_price_match.group(0)
        except Exception:
            try:
                original_price = product_page.find_element(By.XPATH, "//span[contains(@class, 'css-18jtttk')]")
                original_price_text = original_price.text.strip()
                original_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", original_price_text)
                if original_price_match:
                    original_price_text = original_price_match.group(0)
            except Exception:
                original_price_text = ""
        try:
            sale_price = product_page.find_element(By.XPATH, "//b[contains(@class, 'css-5fq4jh')]")
            sale_price_text = sale_price.text.strip()
            sale_price_match = re.search(r"\$\d{1,3}(?:,\d{3})*\.\d{2}", sale_price_text)
            if sale_price_match:
                sale_price_text = sale_price_match.group(0)
        except Exception:
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
    results = []
    brand_page = get_driver(url)
    while True:
        while True:
            brand_page.execute_script("window.scrollBy(0, 250)", "")
            time.sleep(.1)
            if brand_page.execute_script("return (window.innerHeight + window.scrollY) >= document.body.scrollHeight;"):
                break
        try:
            wait = WebDriverWait(brand_page, 2)
            show_more_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'css-bk5oor eanm77i0')]")))
            show_more_button.click()
        except Exception:
            break
    try:
        product_urls = brand_page.find_elements(By.XPATH, "//a[contains(@class, 'css-klx76')]")
        for product_url in product_urls:
            url_text = product_url.get_attribute("href").strip()
            product_results = scrape_product_page(url_text)
            results += product_results
    except Exception:
        print("no results")
    return results

def iterate_pages(brand_list):
    results = []
    for brand in brand_list:
        print(brand)
        page_results = scrape_brand_page(f"http://www.sephora.com/brand/{brand}/skincare")
        results += page_results
    return results

if __name__ == "__main__":
    # brands = ["biossance"]
    # brands = ["augustinus-bader",
    #           "biossance",
    #           "caudalie",
    #           "charlotte-tilbury",
    #           "dr-dennis-gross-skincare",
    #           "dr-jart",
    #           "farmacy",
    #           "fenty-skin-rihanna",
    #           "fresh",
    #           "gisou",
    #           "glow-recipe",
    #           "ilia",
    #           "the-inkey-list",
    #           "laneige",
    #           "l-occitane",
    #           "merit",
    #           "moroccanoil",
    #           "ole-henriksen",
    #           "paulas-choice",
    #           "sephora-collection",
    #           "sk-ii",
    #           "skinfix",
    #           "sol-de-janeiro",
    #           "stripes",
    #           "sulwhasoo",
    #           "summer-fridays",
    #           "tatcha"]
    # products = iterate_pages(brands)
    products = scrape_product_page("https://www.sephora.com/product/kale-spinach-hyaluronic-acid-age-prevention-cream-P411388?skuId=1863604&icid2=products%20grid:p411388:product")
    products = pd.DataFrame(products)
    products = products.drop_duplicates()
    products.to_csv(f"sephora_skincare_{date.today()}.csv", index=False)
    print("Done")