#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超级简单的初始化脚本
"""

import sqlite3
import bcrypt
import os

# 数据库路径
db_path = os.path.join(os.path.dirname(__file__), "gmtools.db")

print("=" * 60)
print("初始化数据库...")
print("=" * 60)

# 创建数据库连接
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建用户表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        level INTEGER DEFAULT 1,
        role VARCHAR(20) DEFAULT 'user',
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )
""")

# 创建审计日志表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action VARCHAR(100) NOT NULL,
        resource VARCHAR(100),
        details TEXT,
        ip_address VARCHAR(45),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
""")

# 创建会话表
cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token VARCHAR(500) NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
""")

conn.commit()
print("✓ 数据库表创建完成")

# 检查管理员是否存在
cursor.execute("SELECT * FROM users WHERE username = 'admin'")
admin = cursor.fetchone()

if admin:
    print("⚠ 管理员账号已存在")
else:
    # 创建管理员
    print("\n创建管理员账号...")
    password = "admin123"
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, level, role)
        VALUES (?, ?, ?, ?, ?)
    """, ("admin", "admin@gmtools.com", password_hash, 10, "super_admin"))
    
    conn.commit()
    print("✓ 管理员账号创建成功!")
    print(f"   用户名: admin")
    print(f"   密码: {password}")
    print(f"   等级: 10")
    print(f"   角色: super_admin")

cursor.close()
conn.close()

print("\n" + "=" * 60)
print("初始化完成!")
print("=" * 60)
print("\n启动 API: python api_main.py")
print("文档: http://localhost:8000/docs\n")
