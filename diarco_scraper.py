from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import chromedriver_py

# Use chromedriver_py to get the path to chromedriver
chrome_driver_path = chromedriver_py.binary_path

# Configure Selenium options to prevent detection
options = webdriver.ChromeOptions()
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

# Setup ChromeDriver
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

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
            brand_element = offer.find_element(By.XPATH, ".//span[contains(@class, 'yith_product_brand')]")
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
