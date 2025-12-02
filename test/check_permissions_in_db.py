#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库中的权限表内容
"""

from database.connection import db

def main():
    print("数据库中的权限列表：")
    print("=" * 60)
    print("ID | 权限代码 | 权限名称 | 分类 | 描述")
    print("=" * 60)
    
    with db.get_cursor() as cursor:
        cursor.execute("SELECT id, code, name, category, description FROM permissions ORDER BY category, id")
        rows = cursor.fetchall()
        
        for row in rows:
            print(f"{row['id']:2d} | {row['code']:25s} | {row['name']:10s} | {row['category']:10s} | {row['description']}")
    
    print("=" * 60)
    print(f"总权限数：{len(rows)}")

if __name__ == "__main__":
    main()
