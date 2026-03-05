import sqlite3

DB_PATH = "Database/all_products.db"


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