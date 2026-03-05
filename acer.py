import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    "Accept": "image/avif,image/webp,image/png,image/svg+xml,image/*;q=0.8,*/*;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "_abck=YOUR_COOKIE_HERE; bm_mi=YOUR_COOKIE_HERE; acer_cdn_uc=IN; data-sticky-bar-click=false",
    "Host": "store.acer.com",
    "Priority": "u=6",
    "Referer": "https://store.acer.com/en-ca/media/sitemaps/en-ca/sitemap.xml",
    "Sec-Fetch-Dest": "image",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:148.0) Gecko/20100101 Firefox/148.0"
}

def acer_scrape(url):
    xml_data = requests.get(url, headers=headers)
    soup = BeautifulSoup(xml_data.content, 'lxml-xml')
    products = []
    
    # Find all <url> tags
    url_tags = soup.find_all('url')
    
    for tag in url_tags:
        loc = tag.find('loc').text.strip()
        # lastmod = tag.find('lastmod').text.strip() if tag.find('lastmod') else None
        
        # Extract the slug (the part after the last /)
        slug = loc.split('/')[-1]
        
        # model_match = re.search(
        #     r'([A-Z0-9]+\.[A-Z0-9]+\.[A-Z0-9]+|[A-Z0-9]+(?:-[A-Z0-9]+){2,})$',
        #     slug,
        #     re.I
        # )
        model_match = re.search(r'([a-z0-9]+-[a-z0-9]+-[a-z0-9]+)$', slug, re.I)
        model_id = model_match.group(1).upper() if model_match else "Unknown"
        
        # Clean the "Name" by removing the model ID from the slug and replacing dashes
        name_part = slug.replace(model_id.lower(), "").replace("-", " ").strip()
        products.append({
            "Model_ID": model_id,
            "Full_Name": name_part.title(),
            "URL": loc
        })
        
    return json.dumps(products)


url="https://store.acer.com/en-in/media/sitemaps/en-in/sitemap.xml"
parsed_data = acer_scrape(url)
print(parsed_data)