import sqlite3
import re


DB_PATH = "Database/new_all_products.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT,
        model TEXT,
        UNIQUE(brand, model)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS variants (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_id INTEGER,
        cpu TEXT,
        gpu TEXT,
        ram TEXT,
        storage TEXT,
        screen_size TEXT,
        color TEXT,
        weight TEXT,
        year TEXT,

        UNIQUE(model_id, cpu, ram, storage),

        FOREIGN KEY(model_id) REFERENCES models(id)
    )
    """)

    conn.commit()
    conn.close()


def insert_product(product):

    conn = get_connection()
    cursor = conn.cursor()

    brand = product.get("Brand")
    model = product.get("Model")

    cursor.execute("""
    INSERT OR IGNORE INTO models (brand, model)
    VALUES (?, ?)
    """, (brand, model))

    cursor.execute("""
    SELECT id FROM models
    WHERE brand=? AND model=?
    """, (brand, model))

    row = cursor.fetchone()
    if not row:
        conn.close()
        return

    model_id = row["id"]

    cpu = product.get("CPU") or ""
    ram = product.get("RAM") or ""
    storage = product.get("Storage") or ""

    cursor.execute("""
    INSERT OR IGNORE INTO variants
    (model_id, cpu, gpu, ram, storage, screen_size, color, weight, year)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        model_id,
        cpu,
        product.get("GPU"),
        ram,
        storage,
        product.get("Screen_size"),
        product.get("Color"),
        product.get("Weight"),
        product.get("Year")
    ))

    conn.commit()
    conn.close()


def clean_model_names():

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT id, brand, model FROM models")
    rows = cursor.fetchall()

    for r in rows:

        model_id = r["id"]
        brand = r["brand"]
        model = r["model"]

        cleaned_model = re.sub(r"\s*\(\d{4}\)", "", model).strip()

        if cleaned_model == model:
            continue

        print(f"Cleaning: {model} → {cleaned_model}")

        cursor.execute(
            "SELECT id FROM models WHERE brand=? AND model=?",
            (brand, cleaned_model)
        )

        existing = cursor.fetchone()

        if existing:

            new_model_id = existing["id"]

            print(f"Merging model_id {model_id} → {new_model_id}")

            # move variants safely
            cursor.execute(
                """
                INSERT OR IGNORE INTO variants
                (model_id, cpu, gpu, ram, storage, screen_size, color, weight, year)
                SELECT ?, cpu, gpu, ram, storage, screen_size, color, weight, year
                FROM variants
                WHERE model_id = ?
                """,
                (new_model_id, model_id)
            )

            # delete old variants
            cursor.execute(
                "DELETE FROM variants WHERE model_id=?",
                (model_id,)
            )

            # delete old model
            cursor.execute(
                "DELETE FROM models WHERE id=?",
                (model_id,)
            )

        else:

            cursor.execute(
                "UPDATE models SET model=? WHERE id=?",
                (cleaned_model, model_id)
            )

    conn.commit()
    conn.close()

    print("Model cleaning + merge complete.")


def get_product_family(model_name):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT m.brand, m.model,
               v.cpu, v.gpu, v.ram, v.storage,
               v.screen_size, v.color, v.weight, v.year
        FROM models m
        JOIN variants v
        ON m.id = v.model_id
        WHERE m.model = ?
    """, (model_name,))

    rows = cursor.fetchall()

    if not rows:
        conn.close()
        return None

    brand = rows[0]["brand"]
    model = rows[0]["model"]

    screen_sizes = set()
    cpus = set()
    gpus = set()
    rams = set()
    storages = set()
    colors = set()
    weights = set()
    years = set()

    for r in rows:

        if r["screen_size"]:
            screen_sizes.add(r["screen_size"])

        if r["cpu"]:
            cpus.add(r["cpu"])

        if r["gpu"]:
            gpus.add(r["gpu"])

        if r["ram"]:
            rams.add(r["ram"])

        if r["storage"]:
            storages.add(r["storage"])

        if r["color"]:
            colors.add(r["color"])

        if r["weight"]:
            weights.add(r["weight"])

        if r["year"]:
            try:
                years.add(int(r["year"]))
            except:
                pass

    series_years = sorted(years) if years else []

    result = {
        "product_family": {
            "brand": brand,
            "model_name": model,
            "series_year": series_years
        },
        "variant_dimensions": {
            "screen_size": sorted(screen_sizes),
            "cpu": sorted(cpus),
            "gpu": sorted(gpus),
            "ram": sorted(rams),
            "storage": sorted(storages),
            "colour": sorted(colors),
            "weight": sorted(weights)
        }
    }

    conn.close()

    return result


def get_all_products_json():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT model FROM models")

    models = cursor.fetchall()

    result = []

    for m in models:

        data = get_product_family(m["model"])

        if data:
            result.append(data)

    conn.close()

    return result