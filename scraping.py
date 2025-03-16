from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import json
import chromedriver_py


# Configurar Selenium
chrome_driver_path = chromedriver_py.binary_path


def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--incognito")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-logging")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--disable-blink-features=AutomationControlled")

    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.managed_default_content_settings.images": 2,
        "disk-cache-size": 4096,
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(executable_path=chrome_driver_path)
    return webdriver.Chrome(service=service, options=options)


def scroll_to_bottom(driver, pause_time=3):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(pause_time)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def scrape_diarco(driver):
    driver.get("https://www.diarco.com.ar/ofertas/")
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "mayorista-btn"))
    ).click()
    sleep(3)

    branch_select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "mayorista-dropdown"))
    )
    branch_select = Select(branch_select_element)
    options = branch_select.options

    branch_info = [
        {"name": option.text, "value": option.get_attribute("value")}
        for option in options
        if option.text != "Seleccioná una sucursal"
    ]

    all_offers = []
    for branch in branch_info:
        url = f'https://www.diarco.com.ar/ofertas/?e-filter-9a897e7-sucursal={branch["value"]}&tipo-sucursal=mayorista#'
        driver.get(url)
        sleep(5)
        scroll_to_bottom(driver, 4)

        offers = driver.find_elements(
            By.XPATH, "/html/body/div[2]/div[4]/div[2]/div[2]/div/div[1]/div"
        )
        for offer in offers:
            try:
                title = offer.find_element(By.CLASS_NAME, "product_title").text
                price = (
                    offer.find_element(By.CLASS_NAME, "price-container")
                    .text.replace("FINAL", "")
                    .strip()
                )
                all_offers.append(
                    {"Sucursal": branch["name"], "Producto": title, "Precio": price}
                )
            except:
                continue

    return all_offers


def scrape_yaguar(driver):
    driver.get("https://shop.yaguar.com.ar/frontendSP/asp/home.asp")

    # Esperar que la sucursal actual se cargue
    sucursal_actual_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".Sucursal p span"))
    )
    sucursal_actual = sucursal_actual_element.text.strip()

    # Extraer todas las sucursales y sus IDs
    sucursales = {}
    sucursales_elements = driver.find_elements(By.CSS_SELECTOR, "ul#nav li ul li a")

    for li in sucursales_elements:
        nombre = li.text.strip()
        onclick_text = li.get_attribute("onclick")
        if onclick_text:
            id_sucursal = onclick_text.split("(")[1].split(")")[0]
            sucursales[nombre] = id_sucursal

        # Obtener el ID de la sucursal actual
        id_sucursal_actual = sucursales.get(sucursal_actual, "ID no encontrado")

        print(f"Sucursal actual: {sucursal_actual}")
        print(f"ID de la sucursal: {id_sucursal_actual}")

    return sucursales  # Retorna todas las sucursales con sus IDs


def main():
    driver = get_driver()
    try:
        data = {
            "Diarco": scrape_diarco(driver),
            "Yaguar": scrape_yaguar(driver),
        }
        with open("hipermercados.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print("Scraping completado y guardado en 'hipermercados.json'")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
