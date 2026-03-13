import sqlite3
import os

db_path = 'gmtools.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

def print_table_info(table_name):
    print(f"\nTable: {table_name}")
    try:
        cursor.execute(f"PRAGMA table_info({table_name})")
        rows = cursor.fetchall()
        for row in rows:
            print(dict(row))
    except Exception as e:
        print(f"Error checking {table_name}: {e}")

print_table_info('users')
print_table_info('level_configs')
conn.close()
