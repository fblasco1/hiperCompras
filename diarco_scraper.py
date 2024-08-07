from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
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
        try:
            code_element = offer.find_element(By.XPATH, ".//h2[contains(text(), 'Cód:')]")
            code = code_element.text.split(': ')[1] if code_element else "No code found"
        except:
            pass
        
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
            discount = offer.find_element(By.CLASS_NAME, "price-container").text
            discount_final = offer.find_element(By.CLASS_NAME, "custom-decimal").text
            return {
                "Tipo": "Promo",
                "Descuento": f"{discount}{discount_final}".replace('\n', '').replace('dto.%', ''),
                "Producto": title,
                "Marca": brand,
                "Descripción": description,
                "Código": code
            }
        elif 'product_tag-super-descuento' in tag:
            return {
                "Tipo": "Super Descuento",
                "Descuento": price.replace('\n', '').replace('dto.%', ''),
                "Descripcion": title,
                "Oferta": True
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

# Función para desplazarse hasta el final de la página
def scroll_to_bottom(driver, pause_time=3):
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        # Desplazarse hasta el final de la página
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Esperar a que se carguen los nuevos elementos
        sleep(pause_time)
        # Calcular nueva altura de la página
        new_height = driver.execute_script("return document.body.scrollHeight")
        # Salir del bucle si no hay más contenido que cargar
        if new_height == last_height:
            break
        last_height = new_height

def scrape_diarco_offers(url):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        sleep(5)  # Wait for the page to load

        scroll_to_bottom(driver, 10)

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

driver.get('https://www.diarco.com.ar/ofertas/')

# Encontrar el botón por ID y hacer clic
button = driver.find_element(By.ID, "mayorista-btn")
ActionChains(driver).move_to_element(button).click(button).perform()
sleep(3)

# Iterate through each branch, skipping disabled options
branch_select = Select(driver.find_element(By.ID, "mayorista-dropdown"))

all_branches_offers = []

for option in branch_select.options:
    if option.get_attribute('disabled'):
        continue  # Skip disabled options

    branch_name = option.text
    if branch_name == "Seleccioná una sucursal":
        continue
    print(f"Processing branch: {branch_name}")

    # Select the branch
    branch_select.select_by_visible_text(branch_name)
    sleep(5)  # Wait for the page to load

    # Update the URL based on selected branch if needed
    current_url = driver.current_url
    offers_info = scrape_diarco_offers(current_url)
    all_branches_offers.extend(offers_info)

print("Scraping completed.")

# Print all offers information
for offer in offers_info:
    print(offer)