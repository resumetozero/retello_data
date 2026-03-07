from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


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
        print(f"Scrapping Versus.com:")
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

    
def amazon_scrape(query_amazon):

    amazon_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        print(f"Scrapping Amazon.in:")
        page_number = 1
        while True:
            url = f"https://www.amazon.in/s?k={query_amazon}&page={page_number}"
            print(f"Scraping page {page_number}")
            page.goto(url, timeout=60000)
            page.wait_for_selector("body")
            soup = BeautifulSoup(page.content(), "html.parser")
            cards = soup.select("div[data-component-type='s-search-result']")

            for card in cards:
                title = card.select_one("h2 span")
                if title:
                    amazon_data.append(title.get_text(strip=True))
                    
            # CHECK IF LAST PAGE
            next_disabled = soup.select_one(".s-pagination-next.s-pagination-disabled")
            if next_disabled:
                print("Reached last page.")
                break
            page_number += 1
        browser.close()
    print(f"Total items scraped from Amazon.in: {len(amazon_data)}")
    return amazon_data


def croma_scrape(croma_url):
    driver = webdriver.Chrome(options=options)
    croma_data = []
    try:
        # print(f"Navigating to: {croma_url}")
        print(f"Scrapping Croma.com:")
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


def flipkart_scrape(query_fcv):
    flipkart_data = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            viewport={"width":1920, "height":1080}
        )
        page = context.new_page()
        page_number = 1
        while True:
            flipkart_url = f"https://www.flipkart.com/search?q={query_fcv}&page={page_number}"
            print(f"Scrapping Flipkart.com Page {page_number}")
            page.goto(flipkart_url, timeout=60000)
            page.wait_for_selector("body")
            soup = BeautifulSoup(page.content(), "html.parser")
            products = soup.find_all("div", class_="RG5Slk")
            # STOP CONDITION
            if len(products) == 0:
                print("No more products. Stopping.")
                break
            print(f"Search results from Flipkart.com ({len(products)} items):")
            for product in products:
                title = product.get_text(strip=True)
                # print(f"Scraped: {title}")
                flipkart_data.append(title)
            page_number += 1
        browser.close()
    return flipkart_data