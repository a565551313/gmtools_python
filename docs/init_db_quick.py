#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速初始化脚本 - 创建默认管理员
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import db
from database.models import User
from auth import AuthUtils

print("=" * 60)
print("GMTools 用户管理系统 - 快速初始化")
print("=" * 60)

# 初始化数据库
print("\n[1/2] 初始化数据库...")
db.init_database()
print("✓ 数据库初始化完成")

# 创建管理员
print("\n[2/2] 创建管理员账号...")
admin = User.get_by_username("admin")

if admin:
    print("⚠ 管理员账号已存在")
    print(f"   用户名: {admin.username}")
    print(f"   邮箱: {admin.email}")
else:
    password_hash = AuthUtils.hash_password("admin123")
    admin = User.create(
        username="admin",
        email="admin@gmtools.com",
        password_hash=password_hash,
        level=10,  # 最高等级
        role="super_admin"
    )
    
    if admin:
        print("✓ 管理员账号创建成功!")
        print(f"   用户名: admin")
        print(f"   密码: admin123")
        print(f"   邮箱: admin@gmtools.com")
    else:
        print("✗ 创建失败")
        sys.exit(1)

print("\n" + "=" * 60)
print("初始化完成!")
print("=" * 60)
print("\n启动 API 服务: python api_main.py")
print("API 文档: http://localhost:8000/docs\n")
