import sqlite3
import pandas as pd

# Connect to the .db file
conn = sqlite3.connect('all_.db')

# List all tables
tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)

# Export each table to a separate CSV
for table_name in tables['name']:
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    df.to_csv(f"{table_name}.csv", index=False)
    print(f"Exported {table_name} to {table_name}.csv")

conn.close()   