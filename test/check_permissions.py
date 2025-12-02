#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查现有权限脚本
"""

from database.permissions import Permission

if __name__ == "__main__":
    print("现有权限：")
    permissions = Permission.get_all()
    for p in permissions:
        print(f"{p.category} - {p.code}: {p.name}")
    print(f"总数：{len(permissions)}")
