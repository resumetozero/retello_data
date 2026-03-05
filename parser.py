import re
import requests
import json


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"


def call_llm(batch):
    prompt = f"""
            Extract laptop specifications from titles.

            Return ONLY a JSON array.

            Schema:
            Brand, Model, Year, Screen_size, CPU, GPU, RAM, Storage, Color, Weight.

            Rules:

            Model:
            Keep only laptop series name and model code.
            Remove CPU, GPU, RAM, storage, screen size, and words like Laptop or Gaming.

            Examples:
            "Acer Aspire Lite AL15-53 Intel Core i5 Laptop 16GB RAM"
            → "Aspire Lite AL15-53"
            "acer Aspire Go 14,14th Gen, Intel Core Ultra 5 125H, 16GB DDR5, 512GB, WUXGA IPS, 14.0"/35.56cm, Win 11, MS Office, Steel Gray, 1.5 kg, AG14-71M, Backlit KB, AI Powered Laptop"
            → "Aspire Go 14 AG14-71M"
            "Nitro V 15 (2025) Core i7-13620H RTX 5050 Laptop"
            → "Nitro V 15 (2025)"

            Screen_size:
            Return format like "15.6 inch".

            CPU:
            Return ONLY the processor model.
            Do NOT include GPU.
            If title contains "Ultra 9 275HX / RTX 5080", CPU = "Ultra 9 275HX".

            GPU:
            Return ONLY the graphics model.
            Do NOT include CPU.
            If title contains "Ultra 9 275HX / RTX 5080", GPU = "RTX 5080".

            RAM:
            Return only number + GB (example: 16GB).

            Storage:
            Return size + type (example: 512GB SSD).

            Year:
            Extract only if a 4 digit year exists.

            Return valid JSON only.

            Titles:
            {chr(10).join(batch)}
            """
            
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0,
                    "num_predict": 600
                }
            },
            timeout=120
        )

    except requests.exceptions.RequestException as e:
        print("LLM request failed:", e)
        return []

    output = response.json().get("response", "").strip()

    # remove markdown if model adds it
    output = output.replace("```json", "").replace("```", "").strip()

    start = output.find("[")
    end = output.rfind("]")

    if start != -1 and end != -1:
        json_str = output[start:end+1]
    else:
        print("No JSON detected")
        return []

    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        print("Failed to parse JSON from model output:")
        print(json_str)
        return []


def parse_title(titles, batch_size=3):
    results = []

    for i in range(0, len(titles), batch_size):

        batch = titles[i:i + batch_size]

        print(f"Processing batch {i//batch_size + 1}...")

        parsed = call_llm(batch)

        for idx, item in enumerate(parsed):

            original_title = batch[idx] if idx < len(batch) else None

            item = normalize_product(item, original_title)

            results.append(item)

    return results


def extract_model_code(title):
    match = re.search(r'[A-Z]{2,5}\d{2,}-\d+[A-Z]*', title)

    if match:
        return match.group()

    return None


def normalize_product(product, original_title=None):
    if product.get("Brand"):
        product["Brand"] = product["Brand"].title()


    if product.get("Model"):

        model = product["Model"]

        model = re.split(r',|Intel|AMD|Ryzen|Core', model)[0].strip()

        product["Model"] = model

    if product.get("Screen_size"):

        m = re.search(r'\d{1,2}\.?[\d]?', product["Screen_size"])

        if m:
            product["Screen_size"] = f"{m.group()} inch"

    if product.get("RAM"):

        m = re.search(r'\d+', product["RAM"])

        if m:
            product["RAM"] = f"{m.group()}GB"

    if product.get("Storage"):

        m = re.search(r'(\d+)\s?(GB|TB)', product["Storage"], re.I)

        if m:
            product["Storage"] = f"{m.group(1)}{m.group(2).upper()} SSD"

    if product.get("GPU") in ["", "N/A", "NHD Graphics"]:
        product["GPU"] = None

    if product.get("Weight"):

        m = re.search(r'\d+\.?\d*', product["Weight"])

        if m:
            product["Weight"] = f"{m.group()}KG"

    if original_title:

        model_code = extract_model_code(original_title)

        if model_code:
            product["Model_Code"] = model_code
      
    if product.get("CPU") and product.get("GPU"):
        cpu = product["CPU"]
        gpu = product["GPU"]
        if gpu in cpu:
            product["CPU"] = cpu.replace(gpu, "").replace("/", "").strip()

    return product