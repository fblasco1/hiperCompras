from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import json
import chromedriver_py

# Use chromedriver_py to get the path to chromedriver
chrome_driver_path = chromedriver_py.binary_path

# Configure Selenium options to optimize and prevent detection
options = webdriver.ChromeOptions()

# Opciones para optimizar el rendimiento
options.add_argument("--headless")  # Ejecuta en modo headless (sin interfaz gráfica)
options.add_argument("--disable-gpu")  # Deshabilita la GPU (recomendado para headless)
options.add_argument("--no-sandbox")  # Deshabilita el modo sandbox
options.add_argument("--disable-dev-shm-usage")  # Usa /tmp en lugar de /dev/shm (mejora la compatibilidad con Docker)
options.add_argument("--window-size=1920,1080")  # Establece un tamaño de ventana fijo
options.add_argument("--disable-extensions")  # Deshabilita extensiones para reducir el tiempo de carga
options.add_argument("--disable-popup-blocking")  # Deshabilita el bloqueo de ventanas emergentes
options.add_argument("--incognito")  # Modo incógnito para reducir el uso de caché
options.add_argument("--disable-infobars")  # Deshabilita la barra de información de Chrome
options.add_argument("--disable-logging")  # Reduce la cantidad de registros generados

# Opciones para evitar la detección
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-blink-features=AutomationControlled")

# Opciones adicionales para mejorar la velocidad
prefs = {
    "profile.default_content_setting_values.notifications": 2,  # Deshabilita las notificaciones
    "profile.managed_default_content_settings.images": 2,  # Deshabilita imágenes
    "disk-cache-size": 4096  # Limita el tamaño de la caché
}
options.add_experimental_option("prefs", prefs)

# Setup ChromeDriver
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service, options=options)

def extract_info(offer, tag, sucursal):
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
                "Suc": sucursal,
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
                "Suc": sucursal,
                "Tipo": "Promo",
                "Producto": title,
                "Marca": brand,
                "Precio": f"{discount}{discount_final}".replace('\n', '').replace('dto.%', ''),
                "Descripción": description,
                "Código": code,
                "Oferta": True,
            }
        elif 'product_tag-super-descuento' in tag:
            return {
                "Suc": sucursal,
                "Tipo": "Super Descuento",
                "Producto": None,
                "Marca": None,
                "Precio": price.replace('\n', '').replace('dto.%', ''),
                "Descripcion": title,
                "Oferta": True
            }
        elif 'product_tag-oferta' in tag:
            return {
                "Suc": sucursal,
                "Tipo": "Oferta",
                "Producto": title,
                "Marca": brand,
                "Precio": price,
                "Descripción": description,
                "Código": code,
                "Oferta": True
            }
        #elif 'product_tag-cuotas' in tag:
        #    cuotas_info = offer.find_element(By.CLASS_NAME, "elementor-heading-title").text.split(' ')
        #    precio_por_cuota = price.split(' ')[0]
        #    cantidad_cuotas = cuotas_info[0]
        #    precio_final = cuotas_info[-1]
        #    return {
        #        "Suc": sucursal,
        #        "Tipo": "Cuotas",
        #        "Producto": title,
        #        "Marca": brand,
        #        "Precio por Cuota": precio_por_cuota,
        #        "Cantidad de Cuotas": cantidad_cuotas,
        #        "Precio Final": precio_final,
        #        "Descripción": description,
        #        "Código": code
        #    }
        elif 'product_tag-estandar-naranja' in tag:
            return {
                "Suc": sucursal,
                "Tipo": "Estandar Naranja",
                "Producto": title,
                "Marca": None,
                "Precio": price,
                "Descripción": description,
                "Código": code,
                "Oferta": False,
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

def scrape_diarco_offers(url, sucursal):
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        sleep(5)  # Wait for the page to load

        scroll_to_bottom(driver, 4)

        # Fetch offer details
        offers = driver.find_elements(By.XPATH, "/html/body/div[2]/div[4]/div[2]/div[2]/div/div[1]/div")
        total_offers = len(offers)
        print(f"Total offers found: {total_offers}")

        all_offers_info = []

        for i, offer in enumerate(offers):
            try:
                tag = offer.get_attribute("class")
                offer_info = extract_info(offer, tag, sucursal)
                if offer_info:
                    all_offers_info.append(offer_info)
                #    print(f"Offer {i+1} processed: {offer_info}")

            except Exception as e:
                print(f"Error processing offer {i+1}: {e}")
                driver.save_screenshot(f"error_offer_{i+1}.png")

        return all_offers_info

    except Exception as e:
        print(f"Error in scraping function: {e}")
        driver.save_screenshot("scraping_error.png")
        return []

driver.get('https://www.diarco.com.ar/ofertas/')

# Click the "mayorista" button
button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "mayorista-btn")))
ActionChains(driver).move_to_element(button).click(button).perform()
sleep(3)

# Get all branch options
branch_select_element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "mayorista-dropdown"))
)
branch_select = Select(branch_select_element)
options = branch_select.options

# Store branch information
branch_info = []
for option in options:
    if not option.get_attribute('disabled') and option.text != "Seleccioná una sucursal":
        branch_info.append({
            'name': option.text,
            'value': option.get_attribute('value')
        })

all_branches_offers = []

# Iterate through branches using direct URLs
for branch in branch_info:
    branch_url = f'https://www.diarco.com.ar/ofertas/?e-filter-9a897e7-sucursal={branch["value"]}&tipo-sucursal=mayorista#'
    print(f"Processing branch: {branch['name']}")

    offers_info = scrape_diarco_offers(branch_url, branch['name'])
    all_branches_offers.extend(offers_info)


print("Scraping completed.")

# Ordenar la lista por la clave "Suc"
sorted_data = sorted(all_branches_offers, key=lambda x: x["Suc"])

# Convertir la lista ordenada a formato JSON y guardarla en un archivo
with open('diarco.json', 'w', encoding='utf-8') as json_file:
    json.dump(sorted_data, json_file, indent=4, ensure_ascii=False)

print("El archivo 'diarco.json' se ha guardado exitosamente.")