import sqlite3
import os

db_path = 'gmtools.db'
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

cursor.execute("SELECT id, username, password_plain FROM users")
rows = cursor.fetchall()
for row in rows:
    print(dict(row))

conn.close()
