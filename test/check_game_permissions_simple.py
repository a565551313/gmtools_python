#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接使用SQL查询游戏管理权限
"""

from database.connection import db

def main():
    print("检查游戏管理权限...")
    
    with db.get_cursor() as cursor:
        # 直接查询游戏管理权限
        cursor.execute("SELECT code, name FROM permissions WHERE category = 'game'")
        rows = cursor.fetchall()
        
        if rows:
            print("找到以下游戏管理权限：")
            for row in rows:
                print(f"  - {row['code']}: {row['name']}")
        else:
            print("没有找到游戏管理权限")
    
    print("检查完成！")

if __name__ == "__main__":
    main()
