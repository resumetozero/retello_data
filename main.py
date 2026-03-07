from scrapper import versus_scrape, amazon_scrape, croma_scrape, flipkart_scrape
# from acer import acer_scrape
from parser import parse_title
from Database.database import create_tables, insert_product, get_all_products_json
import json
import re

def clean_product(product):

    # Normalize brand
    brand = product.get("Brand")
    if brand:
        product["Brand"] = brand.strip().lower()
    else:
        product["Brand"] = None

    # Normalize model
    model = product.get("Model")
    if model:
        product["Model"] = model.strip().lower()
    else:
        product["Model"] = None
    gpu = product.get("GPU")

    if isinstance(gpu, list):
        gpu = " / ".join(gpu)

    if isinstance(gpu, str):
        gpu = gpu.strip()

        if "not specified" in gpu.lower() or "graphics" in gpu.lower():
            gpu = None

    product["GPU"] = gpu

    year = product.get("Year")

    if not year:
        product["Year"] = None
    else:
        m = re.search(r"\d{4}", str(year))
        product["Year"] = m.group() if m else None


    ram = product.get("RAM")

    if ram:
        ram = ram.lower()
        m = re.search(r"\d+", ram)

        if m:
            product["RAM"] = f"{m.group()}gb"
        else:
            product["RAM"] = None
    else:
        product["RAM"] = None

    storage = product.get("Storage")

    if storage:

        storage = storage.lower()

        m = re.search(r"(\d+)(tb|gb)", storage)

        if m:
            product["Storage"] = m.group()
        else:
            product["Storage"] = None

    else:
        product["Storage"] = None

    screen = product.get("Screen_size")

    if screen:

        m = re.search(r"\d{2}\.?\d?", str(screen))

        if m:
            product["Screen_size"] = m.group()
        else:
            product["Screen_size"] = None

    else:
        product["Screen_size"] = None

    col = product.get("Color")

    if not col or col.lower() in ["", "n/a", "not specified", "none specified"]:
        product["Color"] = None
    return product


def sanitize_product(product):
    if not isinstance(product, dict):
        return None
    cleaned = {}
    for key, value in product.items():
        if isinstance(value, list):
            cleaned[key] = " / ".join(map(str, value))
        else:
            cleaned[key] = value
    return cleaned


if __name__ == "__main__":
    data={}
    search_input = input("Enter your search items: ")

    query_fcv = search_input.replace(" ", "%20")
    query_amazon = search_input.replace(" ", "+")

    #include details of the old laptops some with year
    versus_url = f"https://versus.com/en/search?p=objs&q={query_fcv}"

    #e-commerce websites
    croma_url = f"https://www.croma.com/searchB?q={query_fcv}%3Arelevance&text={query_fcv}"
    
    #flipkart and amazon are directly called from scrapping.py

    #laptops websies
    # hp_url = f"https://www.hp.com/in-en/search.html?q={query_fcv}"
    # dell_url = f"https://www.dell.com/en-in/search?query={query_fcv}"

    # ------------------------------------------------------------------
    # For testing purpose, using data instead of scrapping
    
    # data_amazon =['acer Aspire 3, Intel Pentium N6000, 12GB LPDDR4X RAM, 256GB SSD, HD, 15.6"/39.62cm, Windows 11 Home, Pure Silver, 1.5KG, A325-45, Thin and Light Laptop','acer Aspire 3, Intel Core Celeron N4500, 12GB LPDDR4X RAM, 512GB SSD, HD, 15.6"/39.62cm, Windows 11 Home, Pure Silver, 1.5KG, A325-45, Thin and Light Laptop', 'acer Aspire Lite, 12th gen, Intel Core i5-12450H Processor, 16 GB, 512GB, Full HD IPS, 15.6"/39.62 cm, Windows 11 Home, MSO, Pure Silver, 1.70 kg, AL15-52H, Backlit Keyboard', 'acer Aspire Go 14,14th Gen, Intel Core Ultra 5 125H, 16GB DDR5, 512GB, WUXGA IPS, 14.0"/35.56cm, Win 11, MS Office, Steel Gray, 1.5 kg, AG14-71M, Backlit KB, AI Powered Laptop','acer SmartChoice ALG, 13th Gen Intel Core i5-13420H, NVIDIA GeForce RTX 3050-6GB DDR6, 16GB RAM, 512GB SSD, FHD 15.6"/39.62 cm, 144Hz, Windows 11 Home, Steel Gray, 1.99 KG, AL15G-53,Gaming Laptop','acer Nitro V 15, AMD Ryzen 7-7445HS, NVIDIA GeForce RTX 4050-6 GB, 16GB DDR5, 512GB SSD, FHD IPS, 15.6"/39.62cm, 165Hz, Win 11 Home, Obsidian Black, 2.1KG, ANV15-42, Gaming Laptop', 'acer Nitro V 15, AMD Ryzen 7-7445HS, NVIDIA GeForce RTX 4050-6 GB, 16GB DDR5, 512GB SSD, FHD IPS, 15.6"/39.62cm, 165Hz, Win 11 Home, Obsidian Black, 2.1KG, ANV15-42, Gaming Laptop', 'acer Aspire AMD Ryzen 5-7430U Processor Laptop with 39.62 cm (15.6") Full HD LED IPS Display (8GB RAM/512 GB SSD/WiFi 6/AMD Graphics/Win11 Home/55Wh) AS15-42, Backlit Keyboard, Pure Silver, 1.79KG', 'acer SmartChoice Aspire Lite, AMD Ryzen 3 7330U Processor, 8 GB RAM, 512 GB SSD, Full HD, 15.6"/39.62cm, Windows 11 Home, Steel Gray, 1.6KG, AL15-41, Metal Body, Premium Thin and Light Laptop', 'ULTIMUS APEX Laptop Intel Pentium Quad Core 8 GB DDR3 512 GB SSD Expandable~1TB 14.1 HD IPS Laptop Anti-Glare Ultra Thin Bezel 180° Hinge 3.0x3 USB HDMI SD Card Slot Win 11 Home 1.25KG Silver', 'acer Aspire Lite, AMD Ryzen 5 7430U Processor, 16 GB RAM, 512 GB SSD, Full HD, 15.6"/39.62 cm, Windows 11 Home,MSO, Steel Gray, 1.59 kg, AL15-41, Thin and Light Laptop', 'acer Professional 14, AMD Ryzen 3-7330U, 8GB RAM, 512GB SSD, 14" Full HD,UHD Graphics, Premium Metal Body, Windows 11 Pro, MSO 21, 1.34KG, Travel Lite, TL14-42M, Light Laptop 8GB RAM', 'acer TravelLite Thin Laptop AMD Ryzen 5 7430U (6-Core) |8GB RAM, 512GB SSD | 14" Full HD Anti-Glare Display |Privacy Shutter| Windows 11| MS Office | Metal Body | 1.34Kg | Black | 1 Year Warranty', 'acer Nitro V, AMD Ryzen 5 6600H, NVIDIA GeForce RTX 3050-6GB, 16GB DDR5, 512GB SSD, FHD IPS, 15.6"/39.6cm, 165 Hz, Win 11 Home, Obsidian Black, 2.1KG, ANV15-41, Gaming Laptop', 'acer Aspire Lite, 13th Gen Intel Core i3-1305U, 8GB RAM, 512GB SSD, FHD, 15.6"/39.62cm, Windows 11 Home, Steel Gray, 1.59KG, AL15-53, Metal Body, Thin and Light Premium, Laptop']
    # data_versus=['Acer Predator Helios 16 PH16-71-948L 16" Intel Core i9-13900HX 2.2GHz / Nvidia GeForce RTX 4080 Laptop / 32GB RAM / 1TB SSD', 'Acer ConceptD 5 (2023) 16" Intel Core i7-12700H 2.3GHz / Nvidia GeForce RTX 3070 Ti Laptop / 32GB RAM / 1TB SSD', 'Acer Predator Helios Neo 16 (2023) 16" Intel Core i9-13900HX 2.2GHz / Nvidia GeForce RTX 4060 Laptop / 32GB RAM / 1TB SSD', 'Acer Predator Helios 16 (2023) Intel Core i7-13700HX 2.1GHz / Nvidia GeForce RTX 4070 Laptop / 16GB RAM / 1TB SSD', 'Acer Nitro 16 (2023) AMD Ryzen 9 7940HS 4GHz / Nvidia GeForce RTX 4070 Laptop / 16GB RAM / 1TB SSD', 'Acer Nitro 16 (2023) AMD Ryzen 5 7640HS 4.3GHz / Nvidia GeForce RTX 4050 Laptop / 16GB RAM / 512GB SSD', 'Acer Nitro 16 (2023) AMD Ryzen 5 7640HS 4.3GHz / Nvidia GeForce RTX 4050 Laptop / 8GB RAM / 512GB SSD', 'Acer Nitro 17 (2023) 17.3" AMD Ryzen 9 7940HS 4GHz / Nvidia GeForce RTX 4070 Laptop / 32GB RAM / 1TB SSD', 'Acer Nitro 5 (2023) 15.6" Intel Core i7-12650H 2.3GHz / Nvidia GeForce RTX 4060 Laptop / 16GB RAM / 512GB SSD', 'Acer Nitro 16 (2023) AMD Ryzen 7 7840HS 3.8GHz / Nvidia GeForce RTX 4050 Laptop / 16GB RAM / 1TB SSD', 'Acer Nitro 16 (2023) AMD Ryzen 7 7840HS 3.8GHz / Nvidia GeForce RTX 4060 Laptop / 16GB RAM / 1TB SSD', 'Acer Nitro 16 (2023) AMD Ryzen 7 7840HS 3.8GHz / Nvidia GeForce RTX 4060 Laptop / 16GB RAM / 512GB SSD', 'Acer Nitro 16 (2023) Intel Core i7-13700H 2.4GHz / Nvidia GeForce RTX 4050 Laptop / 16GB RAM / 512GB SSD', 'Acer Nitro V 15 (2023) 15.6" Intel Core i7-13620H 2.4GHz / Nvidia GeForce RTX 4060 Laptop / 16GB RAM / 1TB SSD', 'Acer Nitro 5 (2023) 15.6" Intel Core i7-12650H 2.3GHz / Nvidia GeForce RTX 4050 Laptop / 16GB RAM / 512GB SSD', 'Acer Nitro 5 (2023) 15.6" Intel Core i5-12450H 2GHz / Nvidia GeForce RTX 4050 Laptop / 16GB RAM / 512GB SSD', 'Acer Nitro V 15 (2023) 15.6" Intel Core i5-13420H 2.1GHz / Nvidia GeForce RTX 2050 Laptop / 16GB RAM / 512GB SSD', 'Acer Nitro V 15 (2023) 15.6" Intel Core i5-13420H 2.1GHz / Nvidia GeForce RTX 2050 Laptop / 8GB RAM / 512GB SSD', 'Acer Nitro V 15 (2023) 15.6" Intel Core i5-13420H 2.1GHz / Nvidia GeForce RTX 3050 Laptop / 16GB RAM / 512GB SSD', 'Acer Nitro V 15 (2023) 15.6" Intel Core i5-13420H 2.1GHz / Nvidia GeForce RTX 3050 Laptop / 8GB RAM / 512GB SSD']
    # data["amazon"]=data_amazon
    # data["versus"]=data_versus
    # ------------------------------------------------------------------
    
    data["croma"]=croma_scrape(croma_url)
    data["versus"]=versus_scrape(versus_url)
    data["amazon"]=amazon_scrape(query_amazon)
    data["flipkart"]=flipkart_scrape(query_fcv)

    print("Parsing titles with LLM...")

    create_tables() #creating tables in the database if not already created


    for source, titles in data.items():
        print(f"Parsing titles from {source}...")
        structured_data = parse_title(titles)

        for item in structured_data:
            item = sanitize_product(item)
            item = clean_product(item)
            insert_product(item)
            
    print("Data inserted into the database successfully.")

    # print(json.dumps(get_product_family("Nitro V 15 (2025)"), indent=2)) # user based product family creation  in terminal
    
    # print(json.dumps(get_all_products_json(), indent=4)) #all data in json format in terminal
    jd = get_all_products_json()
    with open("products.json", "w") as f:
        json.dump(jd, f, indent=4)