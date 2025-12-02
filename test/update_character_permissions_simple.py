#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接使用SQL更新角色管理权限
"""

from database.connection import db

def main():
    print("更新角色管理权限...")
    
    with db.get_cursor() as cursor:
        # 1. 删除旧的角色权限
        print("删除旧的角色权限...")
        cursor.execute("DELETE FROM permissions WHERE code = 'character.view'")
        
        # 2. 添加新的角色权限
        print("添加新的角色权限...")
        
        # 获取角色信息权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'character.get_info'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('character.get_info', '获取角色信息', 'character', '获取角色详细信息'))
            print("添加权限: character.get_info - 获取角色信息")
        else:
            print("权限已存在: character.get_info - 获取角色信息")
        
        # 恢复角色道具权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'character.recover_props'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('character.recover_props', '恢复角色道具', 'character', '恢复角色道具'))
            print("添加权限: character.recover_props - 恢复角色道具")
        else:
            print("权限已存在: character.recover_props - 恢复角色道具")
    
    print("角色管理权限更新完成！")

if __name__ == "__main__":
    main()
