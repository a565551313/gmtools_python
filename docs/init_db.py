#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建默认管理员账号
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import db
from database.models import User
from auth import AuthUtils


def init_admin_user():
    """创建默认管理员账号"""
    print("=" * 60)
    print("GMTools 用户管理系统 - 数据库初始化")
    print("=" * 60)
    
    # 初始化数据库表
    print("\n[1/3] 初始化数据库表结构...")
    db.init_database()
    print("✓ 数据库表结构初始化完成")
    
    # 检查是否已存在管理员
    print("\n[2/3] 检查管理员账号...")
    admin = User.get_by_username("admin")
    
    if admin:
        print("⚠ 管理员账号已存在")
        print(f"   用户名: {admin.username}")
        print(f"   邮箱: {admin.email}")
        print(f"   角色: {admin.role}")
        
        choice = input("\n是否重置管理员密码? (y/N): ").strip().lower()
        if choice == 'y':
            new_password = input("请输入新密码 (默认: admin123): ").strip() or "admin123"
            password_hash = AuthUtils.hash_password(new_password)
            admin.update_password(password_hash)
            print(f"✓ 管理员密码已重置为: {new_password}")
        else:
            print("跳过密码重置")
    else:
        # 创建默认管理员
        print("\n[3/3] 创建默认管理员账号...")
        
        username = input("管理员用户名 (默认: admin): ").strip() or "admin"
        email = input("管理员邮箱 (默认: admin@gmtools.com): ").strip() or "admin@gmtools.com"
        password = input("管理员密码 (默认: admin123): ").strip() or "admin123"
        full_name = input("管理员全名 (默认: 系统管理员): ").strip() or "系统管理员"
        
        password_hash = AuthUtils.hash_password(password)
        
        admin = User.create(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            role="super_admin"
        )
        
        if admin:
            print("\n✓ 管理员账号创建成功!")
            print(f"   用户名: {admin.username}")
            print(f"   邮箱: {admin.email}")
            print(f"   密码: {password}")
            print(f"   角色: {admin.role}")
        else:
            print("\n✗ 管理员账号创建失败!")
            return False
    
    print("\n" + "=" * 60)
    print("数据库初始化完成!")
    print("=" * 60)
    print("\n您可以使用以下信息登录:")
    print(f"  用户名: {admin.username}")
    print(f"  API 地址: http://localhost:8000/api/users/login")
    print(f"  API 文档: http://localhost:8000/docs")
    print("\n")
    
    return True


if __name__ == "__main__":
    try:
        init_admin_user()
    except KeyboardInterrupt:
        print("\n\n操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
