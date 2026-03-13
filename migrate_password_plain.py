import sqlite3
import os

db_path = 'gmtools.db'
if not os.path.exists(db_path):
    print("DB not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Adding password_plain column...")
    cursor.execute("ALTER TABLE users ADD COLUMN password_plain VARCHAR(255)")
    conn.commit()
    print("Migration successful!")
except Exception as e:
    if "duplicate column name" in str(e).lower():
        print("Column already exists, skipping.")
    else:
        conn.rollback()
        print(f"Migration failed: {e}")
finally:
    conn.close()
