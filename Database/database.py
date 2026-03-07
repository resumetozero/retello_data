import sqlite3
import re


DB_PATH = "Database/new_all_products.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        brand TEXT NOT NULL,
        model TEXT NOT NULL,
        UNIQUE(brand, model)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS variants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id INTEGER NOT NULL,
    cpu TEXT NOT NULL,
    gpu TEXT,
    ram TEXT NOT NULL,
    storage TEXT NOT NULL,
    screen_size TEXT NOT NULL,
    color TEXT,
    weight TEXT,
    year TEXT,

    UNIQUE(model_id, cpu, ram, storage, screen_size),

    FOREIGN KEY(model_id) REFERENCES models(id)
)
    """)

    conn.commit()
    conn.close()
    
    
def normalize_text(text):
    if text is None:
        return None
    text = str(text).strip().lower()
    if text == "":
        return None
    return text


def insert_product(product):

    conn = get_connection()
    cursor = conn.cursor()

    brand = normalize_text(product.get("Brand"))
    model = normalize_text(product.get("Model"))
    cpu = normalize_text(product.get("CPU"))
    gpu = normalize_text(product.get("GPU"))
    ram = normalize_text(product.get("RAM"))
    storage = normalize_text(product.get("Storage"))
    screen = normalize_text(product.get("Screen_size"))

    color = normalize_text(product.get("Color"))
    weight = normalize_text(product.get("Weight"))
    year = normalize_text(product.get("Year"))

    required = [brand, model, cpu, ram, storage, screen]

    if not all(required):
        conn.close()
        return

    # Insert model
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

    # Try inserting variant
    cursor.execute("""
    INSERT OR IGNORE INTO variants
    (model_id, cpu, gpu, ram, storage, screen_size, color, weight, year)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        model_id,
        cpu,
        gpu,
        ram,
        storage,
        screen,
        color,
        weight,
        year
    ))

    # Fetch the variant (existing or newly inserted)
    cursor.execute("""
    SELECT id, color, weight, year
    FROM variants
    WHERE model_id=? AND cpu=? AND ram=? AND storage=? AND screen_size=?
    """, (model_id, cpu, ram, storage, screen))

    variant = cursor.fetchone()

    if variant:

        new_color = variant["color"] or color
        new_weight = variant["weight"] or weight
        new_year = variant["year"] or year

        cursor.execute("""
        UPDATE variants
        SET color=?, weight=?, year=?
        WHERE id=?
        """, (new_color, new_weight, new_year, variant["id"]))

    conn.commit()
    conn.close()

def get_product_family(model_name):
    model_name = normalize_text(model_name)

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