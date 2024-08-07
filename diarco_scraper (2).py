# -*- coding: utf-8 -*-
"""Diarco_Scraper.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yqlPTYZ_1zzBg8KoDkkG9xUw5VK1BMEA
"""

!python diarco_scraper.py

import requests
from bs4 import BeautifulSoup


def scrape_url (url : str):

  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  paragraphs = soup.find_all('p')
  for p in paragraphs:
    print(p.text)

scrape_url("https://en.m.wikipedia.org/wiki/The_Royal_Tenenbaums")

# Commented out IPython magic to ensure Python compatibility.
# # Set up for running selenium in Google Colab
# ## You don't need to run this code if you do it in Jupyter notebook, or other local Python setting
# %%shell
# sudo apt -y update
# sudo apt install -y wget curl unzip
# wget http://archive.ubuntu.com/ubuntu/pool/main/libu/libu2f-host/libu2f-udev_1.1.4-1_all.deb
# dpkg -i libu2f-udev_1.1.4-1_all.deb
# wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# dpkg -i google-chrome-stable_current_amd64.deb
# CHROME_DRIVER_VERSION=`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`
# wget -N https://chromedriver.storage.googleapis.com/$CHROME_DRIVER_VERSION/chromedriver_linux64.zip -P /tmp/
# unzip -o /tmp/chromedriver_linux64.zip -d /tmp/
# chmod +x /tmp/chromedriver
# mv /tmp/chromedriver /usr/local/bin/chromedriver
# pip install selenium

!pip install chromedriver-autoinstaller

import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')

import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import chromedriver_autoinstaller

# setup chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless') # ensure GUI is off
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# set path to chromedriver as per your configuration
chromedriver_autoinstaller.install()

# set the target URL
url = "https://en.m.wikipedia.org/wiki/The_Royal_Tenenbaums"

# set up the webdriver
driver = webdriver.Chrome(options=chrome_options)

from selenium.webdriver.support.ui import WebDriverWait,Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from time import sleep

def extract_info(offer, tag):
    try:
        title = offer.find_element(By.CLASS_NAME, "product_title").text

        # Elimina "FINAL" del precio
        price_container = offer.find_element(By.CLASS_NAME, "price-container").text
        price = price_container.replace('FINAL', '').strip()

        # Descripción sin el código
        description_elements = offer.find_elements(By.CLASS_NAME, "short-description-tag")
        description = " ".join([elem.text for elem in description_elements if 'Cód:' not in elem.text])

        # Código del producto
        code_element = offer.find_element(By.XPATH, ".//h2[contains(text(), 'Cód:')]")
        code = code_element.text.split(': ')[1] if code_element else "No code found"

        # Marca del producto
        try:
            brand_element = offer.find_element(By.XPATH, ".//h2[contains(@class, 'elementor-heading-title')]/span")
            brand = brand_element.text
        except:
            brand = "No brand found"

        if 'product_tag-estandar' in tag:
            return {
                "Tipo": "Estandar",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code,
                "Oferta": False
            }
        elif 'product_tag-promo' in tag:
            discount = offer.find_element(By.CLASS_NAME, "custom-decimal").text
            discount_final = offer.find_element(By.CLASS_NAME, "custom-decimal-final").text
            return {
                "Tipo": "Promo",
                "Descuento": f"{discount}{discount_final}",
                "Producto": title,
                "Marca": brand,
                "Descripción": description,
                "Código": code
            }
        elif 'product_tag-super-descuento' in tag:
            return {
                "Tipo": "Super Descuento",
                "Descuento": price,
                "Producto": title,
                "Marca": brand
            }
        elif 'product_tag-oferta' in tag:
            return {
                "Tipo": "Oferta",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code,
                "Oferta": True
            }
        elif 'product_tag-cuotas' in tag:
            cuotas_info = offer.find_element(By.CLASS_NAME, "elementor-heading-title").text.split(' ')
            precio_por_cuota = price.split(' ')[0]
            cantidad_cuotas = cuotas_info[0]
            precio_final = cuotas_info[-1]
            return {
                "Tipo": "Cuotas",
                "Producto": title,
                "Marca": brand,
                "Precio por Cuota": precio_por_cuota,
                "Cantidad de Cuotas": cantidad_cuotas,
                "Precio Final": precio_final,
                "Descripción": description,
                "Código": code
            }
        elif 'product_tag-estandar-naranja' in tag:
            return {
                "Tipo": "Estandar Naranja",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code
            }
        else:
            return None
    except Exception as e:
        print(f"Error extracting info for offer with tag {tag}: {e}")
        driver.save_screenshot(f"error_screenshot_{tag}.png")
        return None

def scrape_diarco_offers(url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        sleep(5)  # Wait for the page to load

        # Scroll down to load more products
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(5):  # Adjust the number of times to scroll as needed
            body.send_keys(Keys.PAGE_DOWN)
            sleep(3)  # Adjust the wait time as needed

        # Fetch offer details
        offers = driver.find_elements(By.XPATH, "/html/body/div[2]/div[4]/div[2]/div[2]/div/div[1]/div")
        total_offers = len(offers)
        print(f"Total offers found: {total_offers}")

        all_offers_info = []

        for i, offer in enumerate(offers):
            try:
                tag = offer.get_attribute("class")
                offer_info = extract_info(offer, tag)
                if offer_info:
                    all_offers_info.append(offer_info)
                    print(f"Offer {i+1} processed: {offer_info}")

            except Exception as e:
                print(f"Error processing offer {i+1}: {e}")
                driver.save_screenshot(f"error_offer_{i+1}.png")

        return all_offers_info

    except Exception as e:
        print(f"Error in scraping function: {e}")
        driver.save_screenshot("scraping_error.png")
        return []

    finally:
        driver.quit()

# URL to scrape
url = "https://www.diarco.com.ar/ofertas/?e-filter-9a897e7-sucursal=9-de-julio&e-filter-9a897e7-product_cat=almacen&tipo-sucursal=mayorista"
offers_info = scrape_diarco_offers(url)
print("Scraping completed.")

# Print all offers information
for offer in offers_info:
    print(offer)
# quit the driver
driver.quit()

!pip install chromedriver-autoinstaller

import sys
sys.path.insert(0, '/usr/lib/chromium-browser/chromedriver')

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import chromedriver_autoinstaller

# Setup Chrome options
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')  # Ensure GUI is off
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')

# Install and set path to chromedriver as per your configuration
chromedriver_autoinstaller.install()

# Set up the webdriver
driver = webdriver.Chrome(options=chrome_options)

def extract_info(offer, tag):
    try:
        title = offer.find_element(By.CLASS_NAME, "product_title").text
        price_container = offer.find_element(By.CLASS_NAME, "price-container").text
        price = price_container.replace('FINAL', '').strip()
        description_elements = offer.find_elements(By.CLASS_NAME, "short-description-tag")
        description = " ".join([elem.text for elem in description_elements if 'Cód:' not in elem.text])
        code_element = offer.find_element(By.XPATH, ".//h2[contains(text(), 'Cód:')]")
        code = code_element.text.split(': ')[1] if code_element else "No code found"
        brand_element = offer.find_element(By.XPATH, ".//h2[contains(@class, 'elementor-heading-title')]/span")
        brand = brand_element.text if brand_element else "No brand found"

        if 'product_tag-estandar' in tag:
            return {
                "Tipo": "Estandar",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code,
                "Oferta": False
            }
        elif 'product_tag-promo' in tag:
            discount = offer.find_element(By.CLASS_NAME, "custom-decimal").text
            discount_final = offer.find_element(By.CLASS_NAME, "custom-decimal-final").text
            return {
                "Tipo": "Promo",
                "Descuento": f"{discount}{discount_final}",
                "Producto": title,
                "Marca": brand,
                "Descripción": description,
                "Código": code
            }
        elif 'product_tag-super-descuento' in tag:
            return {
                "Tipo": "Super Descuento",
                "Descuento": price,
                "Producto": title,
                "Marca": brand
            }
        elif 'product_tag-oferta' in tag:
            return {
                "Tipo": "Oferta",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code,
                "Oferta": True
            }
        elif 'product_tag-cuotas' in tag:
            cuotas_info = offer.find_element(By.CLASS_NAME, "elementor-heading-title").text.split(' ')
            precio_por_cuota = price.split(' ')[0]
            cantidad_cuotas = cuotas_info[0]
            precio_final = cuotas_info[-1]
            return {
                "Tipo": "Cuotas",
                "Producto": title,
                "Marca": brand,
                "Precio por Cuota": precio_por_cuota,
                "Cantidad de Cuotas": cantidad_cuotas,
                "Precio Final": precio_final,
                "Descripción": description,
                "Código": code
            }
        elif 'product_tag-estandar-naranja' in tag:
            return {
                "Tipo": "Estandar Naranja",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code
            }
        else:
            return None
    except Exception as e:
        print(f"Error extracting info for offer with tag {tag}: {e}")
        driver.save_screenshot(f"error_screenshot_{tag}.png")
        return None

def scrape_diarco_offers(url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        sleep(5)  # Wait for the page to load

        # Scroll down to load more products
        body = driver.find_element(By.TAG_NAME, 'body')
        for _ in range(5):  # Adjust the number of times to scroll as needed
            body.send_keys(Keys.PAGE_DOWN)
            sleep(3)  # Adjust the wait time as needed

        # Fetch offer details
        offers = driver.find_elements(By.XPATH, "/html/body/div[2]/div[4]/div[2]/div[2]/div/div[1]/div")
        total_offers = len(offers)
        print(f"Total offers found: {total_offers}")

        all_offers_info = []

        for i, offer in enumerate(offers):
            try:
                tag = offer.get_attribute("class")
                offer_info = extract_info(offer, tag)
                if offer_info:
                    all_offers_info.append(offer_info)
                    print(f"Offer {i+1} processed: {offer_info}")

            except Exception as e:
                print(f"Error processing offer {i+1}: {e}")
                driver.save_screenshot(f"error_offer_{i+1}.png")

        return all_offers_info

    except Exception as e:
        print(f"Error in scraping function: {e}")
        driver.save_screenshot("scraping_error.png")
        return []

# Iterate through each branch, skipping disabled options
branch_select = Select(driver.find_element(By.ID, "mayorista-dropdown"))

all_branches_offers = []

for option in branch_select.options:
    if option.get_attribute('disabled'):
        continue  # Skip disabled options

    branch_name = option.text
    print(f"Processing branch: {branch_name}")

    # Select the branch
    branch_select.select_by_visible_text(branch_name)
    time.sleep(5)  # Wait for the page to load

    # Update the URL based on selected branch if needed
    current_url = driver.current_url
    offers_info = scrape_diarco_offers(current_url)
    all_branches_offers.extend(offers_info)

# Print all offers information for all branches
for offer in all_branches_offers:
    print(offer)

print("Scraping completed.")
driver.quit()

# URL to scrape
url = "https://www.diarco.com.ar/ofertas/?e-filter-9a897e7-sucursal=9-de-julio&e-filter-9a897e7-product_cat=almacen&tipo-sucursal=mayorista"
offers_info = scrape_diarco_offers(url)
print("Scraping completed.")

# Print all offers information
for offer in offers_info:
    print(offer)

# Function to extract information from offers
def extract_info(offer, tag):
    try:
        title = offer.find_element(By.CLASS_NAME, "product_title").text

        # Elimina "FINAL" del precio
        price_container = offer.find_element(By.CLASS_NAME, "price-container").text
        price = price_container.replace('FINAL', '').strip()

        # Descripción sin el código
        description_elements = offer.find_elements(By.CLASS_NAME, "short-description-tag")
        description = " ".join([elem.text for elem in description_elements if 'Cód:' not in elem.text])

        # Código del producto
        code_element = offer.find_element(By.XPATH, ".//h2[contains(text(), 'Cód:')]")
        code = code_element.text.split(': ')[1] if code_element else "No code found"

        # Marca del producto
        try:
            brand_element = offer.find_element(By.XPATH, ".//h2[contains(@class, 'elementor-heading-title')]/span")
            brand = brand_element.text
        except:
            brand = "No brand found"

        if 'product_tag-estandar' in tag:
            return {
                "Tipo": "Estandar",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code,
                "Oferta": False
            }
        elif 'product_tag-promo' in tag:
            discount = offer.find_element(By.CLASS_NAME, "custom-decimal").text
            discount_final = offer.find_element(By.CLASS_NAME, "custom-decimal-final").text
            return {
                "Tipo": "Promo",
                "Descuento": f"{discount}{discount_final}",
                "Producto": title,
                "Marca": brand,
                "Descripción": description,
                "Código": code
            }
        elif 'product_tag-super-descuento' in tag:
            return {
                "Tipo": "Super Descuento",
                "Descuento": price,
                "Producto": title,
                "Marca": brand
            }
        elif 'product_tag-oferta' in tag:
            return {
                "Tipo": "Oferta",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code,
                "Oferta": True
            }
        elif 'product_tag-cuotas' in tag:
            cuotas_info = offer.find_element(By.CLASS_NAME, "elementor-heading-title").text.split(' ')
            precio_por_cuota = price.split(' ')[0]
            cantidad_cuotas = cuotas_info[0]
            precio_final = cuotas_info[-1]
            return {
                "Tipo": "Cuotas",
                "Producto": title,
                "Marca": brand,
                "Precio por Cuota": precio_por_cuota,
                "Cantidad de Cuotas": cantidad_cuotas,
                "Precio Final": precio_final,
                "Descripción": description,
                "Código": code
            }
        elif 'product_tag-estandar-naranja' in tag:
            return {
                "Tipo": "Estandar Naranja",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code
            }
        else:
            return None
    except Exception as e:
        print(f"Error extracting info for offer with tag {tag}: {e}")
        driver.save_screenshot(f"error_screenshot_{tag}.png")
        return None

# quit the driver
driver.quit()