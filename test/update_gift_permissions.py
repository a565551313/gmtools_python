#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新礼物道具权限，添加新权限
"""

from database.connection import db

def main():
    print("更新礼物道具权限...")
    
    with db.get_cursor() as cursor:
        # 添加新的礼物道具权限
        print("添加新的礼物道具权限...")
        
        # 给予道具权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'gift.give_item'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('gift.give_item', '给予道具', 'gift', '给予玩家道具'))
            print("添加权限: gift.give_item - 给予道具")
        else:
            print("权限已存在: gift.give_item - 给予道具")
        
        # 给予宝石权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'gift.give_gem'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('gift.give_gem', '给予宝石', 'gift', '给予玩家宝石'))
            print("添加权限: gift.give_gem - 给予宝石")
        else:
            print("权限已存在: gift.give_gem - 给予宝石")
        
        # 获取充值类型权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'gift.get_recharge_types'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('gift.get_recharge_types', '获取类型', 'gift', '获取充值类型'))
            print("添加权限: gift.get_recharge_types - 获取类型")
        else:
            print("权限已存在: gift.get_recharge_types - 获取类型")
        
        # 获取充值卡号权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'gift.get_recharge_cards'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('gift.get_recharge_cards', '获取卡号', 'gift', '获取充值卡号'))
            print("添加权限: gift.get_recharge_cards - 获取卡号")
        else:
            print("权限已存在: gift.get_recharge_cards - 获取卡号")
        
        # 生成CDK权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'gift.generate_cdk'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('gift.generate_cdk', '生成CDK', 'gift', '生成CDK'))
            print("添加权限: gift.generate_cdk - 生成CDK")
        else:
            print("权限已存在: gift.generate_cdk - 生成CDK")
        
        # 自定义CDK权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'gift.generate_custom_cdk'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('gift.generate_custom_cdk', '自定义CDK', 'gift', '自定义CDK'))
            print("添加权限: gift.generate_custom_cdk - 自定义CDK")
        else:
            print("权限已存在: gift.generate_custom_cdk - 自定义CDK")
        
        # 新建充值类型权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'gift.new_recharge_type'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('gift.new_recharge_type', '新建类型', 'gift', '新建充值类型'))
            print("添加权限: gift.new_recharge_type - 新建类型")
        else:
            print("权限已存在: gift.new_recharge_type - 新建类型")
        
        # 删除充值类型权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'gift.del_recharge_type'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('gift.del_recharge_type', '删除类型', 'gift', '删除充值类型'))
            print("添加权限: gift.del_recharge_type - 删除类型")
        else:
            print("权限已存在: gift.del_recharge_type - 删除类型")
    
    print("礼物道具权限更新完成！")

if __name__ == "__main__":
    main()
