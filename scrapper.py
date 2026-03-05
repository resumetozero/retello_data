from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

options = Options()
options.add_argument("--headless") 
options.binary_location = "/usr/bin/chromium-browser"  
options.add_argument("--no-sandbox")         
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--window-size=1920,1080")
options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36')

def versus_scrape(versus_url):
    driver = webdriver.Chrome(options=options)
    versus_data = []
    try:
        print(f"Navigating to: {versus_url}")
        driver.get(versus_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        headings = soup.select("p[class^='Item__name___']")
        print(f"Search results from Versus.com ({len(headings)} items):")
        for heading in headings:
            text = heading.get_text(strip=True)
            versus_data.append(text)
    finally:
        driver.quit()
        return versus_data


def amazon_scrape(amazon_url):
    driver = webdriver.Chrome(options=options)
    amazon_data = []
    try:
        print(f"Navigating to: {amazon_url}")
        driver.get(amazon_url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))  #(By.CSS_SELECTOR, "div[data-component-type='s-search-result']")
        soup = BeautifulSoup(driver.page_source, "html.parser")

        headings = soup.find_all("div", class_="a-section a-spacing-none puis-padding-right-small s-title-instructions-style puis-desktop-list-title-instructions-style")

        print(f"Search results from Amazon.in ({len(headings)} items):")

        for product in headings[2:]:
            brand = product.find("h2", class_="a-size-mini s-line-clamp-1").get_text(strip=True)+" " if product.find("h2", class_="a-size-mini s-line-clamp-1") else ""
            title = product.find("h2",class_="a-size-medium a-spacing-none a-color-base a-text-normal").get_text(strip=True)
            amazon_data.append(f"{brand}{title}")

    finally:
        driver.quit()
        return amazon_data
    
def croma_scrape(croma_url):
    driver = webdriver.Chrome(options=options)
    croma_data = []

    try:
        print(f"Navigating to: {croma_url}")
        driver.get(croma_url)

        # Wait until products load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "product-info")))

        soup = BeautifulSoup(driver.page_source, "html.parser")

        products = soup.find_all("div", class_="product-info")

        print(f"Search results from Croma.com ({len(products)} items):")

        for product in products:
            title_tag = product.find("h3", class_="product-title")

            if title_tag:
                title = title_tag.get_text(strip=True)
                croma_data.append(title)

    finally:
        driver.quit()

    return croma_data