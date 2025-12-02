#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接检查数据库中的权限表
"""

import sqlite3
import os

def main():
    print("检查数据库中的权限表...")
    
    # 获取数据库路径
    db_path = os.path.join(os.path.dirname(__file__), 'gmtools.db')
    print(f"数据库路径: {db_path}")
    
    if not os.path.exists(db_path):
        print("数据库文件不存在！")
        return
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 查询游戏管理权限
        print("\n查询游戏管理权限：")
        cursor.execute("SELECT code, name, category, description FROM permissions WHERE category = 'game' OR category = 'account' OR category = 'character' OR category = 'pet' OR category = 'equipment'")
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                print(f"  - {row[0]}: {row[1]} ({row[2]}) - {row[3]}")
        else:
            print("  没有找到权限记录")
        
        # 查询所有权限
        print("\n查询所有权限：")
        cursor.execute("SELECT code, name, category FROM permissions ORDER BY category, code")
        rows = cursor.fetchall()
        
        if rows:
            for row in rows:
                print(f"  - {row[0]}: {row[1]} ({row[2]})")
        else:
            print("  没有找到权限记录")
            
        # 查询权限表结构
        print("\n权限表结构：")
        cursor.execute("PRAGMA table_info(permissions)")
        rows = cursor.fetchall()
        for row in rows:
            print(f"  - {row[1]}: {row[2]}")
            
    except Exception as e:
        print(f"查询出错: {e}")
    finally:
        conn.close()
    
    print("\n检查完成！")

if __name__ == "__main__":
    main()
