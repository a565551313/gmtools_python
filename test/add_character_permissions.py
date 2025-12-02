#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为角色管理模块添加具体的权限
"""

from database.permissions import Permission

def main():
    # 添加角色管理的具体权限
    character_permissions = [
        ("character.get_info", "获取角色信息", "character", "获取角色详细信息"),
        ("character.recover_props", "恢复角色道具", "character", "恢复角色道具"),
    ]
    
    print("添加角色管理的具体权限...")
    for code, name, category, description in character_permissions:
        # 检查权限是否已存在
        if not Permission.get_by_code(code):
            Permission.create(code, name, category, description)
            print(f"添加权限: {code} - {name}")
        else:
            print(f"权限已存在: {code} - {name}")
    
    print("角色管理权限添加完成！")

if __name__ == "__main__":
    main()
