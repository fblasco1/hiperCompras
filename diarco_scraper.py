from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from time import sleep
import markdownify
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

def convert_html_to_markdown(html, title):
    # Convert HTML to Markdown
    md = markdownify.markdownify(html, heading_style="ATX")
    return f"# {title}\n\n" + md  # Add a title to the content

def scrape_diarco_offers(url):
    driver.get(url)
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

    for i, offer in enumerate(offers):
        try:
            title = offer.find_element(By.CLASS_NAME, "product_title").text
            price = offer.find_element(By.CLASS_NAME, "price-container").text
            #description_html = offer.find_element(By.XPATH, "/div/div/div[3]/div[3]/div/h2")
            #description_md = convert_html_to_markdown(description_html, title)
            
            ## Save to a Markdown file
            #filename = f"offer_{i+1:03d}_{title.replace('/', '-')}.md"
            #with open(filename, "w", encoding="utf-8") as file:
            #    file.write(description_md)
            
            print(f"Offer {i+1} saved: {title} - {price}")

        except Exception as e:
            print(f"Error fetching offer {i+1}: {e}")

    driver.quit()

# URL to scrape
url = "https://www.diarco.com.ar/ofertas/?e-filter-9a897e7-sucursal=9-de-julio&e-filter-9a897e7-product_cat=almacen&tipo-sucursal=mayorista"
scrape_diarco_offers(url)
print("Scraping completed.")
