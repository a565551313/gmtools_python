import sqlite3
import os

db_path = 'gmtools.db'
if not os.path.exists(db_path):
    print("DB not found")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # SQLite doesn't support dropping NOT NULL easily.
    # We need to recreate the table.
    
    print("Starting migration...")
    
    # 1. Get existing columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    columns_str = ", ".join(columns)
    
    # 2. Rename old table
    cursor.execute("ALTER TABLE users RENAME TO users_old")
    
    # 3. Create new table with correct schema
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            level INTEGER DEFAULT 1,
            role VARCHAR(20) DEFAULT 'user',
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            bound_ids TEXT
        )
    """)
    
    # 4. Copy data
    # Note: we need to handle the case where some columns might be missing in old table if it was very old
    # but based on our check_schema, it has bound_ids.
    cursor.execute(f"INSERT INTO users ({columns_str}) SELECT {columns_str} FROM users_old")
    
    # 5. Drop old table
    cursor.execute("DROP TABLE users_old")
    
    # 6. Recreate indexes
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    
    conn.commit()
    print("Migration successful!")
except Exception as e:
    conn.rollback()
    print(f"Migration failed: {e}")
finally:
    conn.close()
