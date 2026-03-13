import sqlite3
import os

db_path = 'gmtools.db'
if not os.path.exists(db_path):
    print("DB not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT username, email FROM users")
rows = cursor.fetchall()
for row in rows:
    print(f"User: {row[0]}, Email: '{row[1]}'")
conn.close()
