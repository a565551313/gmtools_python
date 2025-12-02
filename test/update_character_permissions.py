#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新角色管理权限，删除旧权限，添加新权限
"""

from database.connection import db
from database.permissions import Permission

def main():
    print("更新角色管理权限...")
    
    with db.get_cursor() as cursor:
        # 删除旧的角色权限
        print("删除旧的角色权限...")
        cursor.execute("DELETE FROM permissions WHERE code = 'character.view'")
        print("旧权限删除完成")
        
    # 添加新的角色权限
    print("添加新的角色权限...")
    new_permissions = [
        ("character.get_info", "获取角色信息", "character", "获取角色详细信息"),
        ("character.recover_props", "恢复角色道具", "character", "恢复角色道具"),
    ]
    
    for code, name, category, description in new_permissions:
        if not Permission.get_by_code(code):
            Permission.create(code, name, category, description)
            print(f"添加权限: {code} - {name}")
        else:
            print(f"权限已存在: {code} - {name}")
    
    print("角色管理权限更新完成！")

if __name__ == "__main__":
    main()
