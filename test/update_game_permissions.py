#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新游戏管理权限，添加新权限，删除旧权限
"""

from database.connection import db

def main():
    print("更新游戏管理权限...")
    
    with db.get_cursor() as cursor:
        # 1. 添加新的游戏管理权限
        print("添加新的游戏管理权限...")
        
        # 发送广播权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'game.broadcast'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('game.broadcast', '发送广播', 'game', '发送游戏广播'))
            print("添加权限: game.broadcast - 发送广播")
        else:
            print("权限已存在: game.broadcast - 发送广播")
        
        # 设置经验倍率权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'game.exp_rate'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('game.exp_rate', '经验倍率', 'game', '设置游戏经验倍率'))
            print("添加权限: game.exp_rate - 经验倍率")
        else:
            print("权限已存在: game.exp_rate - 经验倍率")
        
        # 设置游戏难度权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'game.difficulty'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('game.difficulty', '游戏难度', 'game', '设置游戏难度'))
            print("添加权限: game.difficulty - 游戏难度")
        else:
            print("权限已存在: game.difficulty - 游戏难度")
        
        # 设置等级上限权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'game.level_cap'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('game.level_cap', '等级上限', 'game', '设置游戏等级上限'))
            print("添加权限: game.level_cap - 等级上限")
        else:
            print("权限已存在: game.level_cap - 等级上限")
        
        # 控制游戏活动权限
        cursor.execute("SELECT id FROM permissions WHERE code = 'game.activity'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO permissions (code, name, category, description) VALUES (?, ?, ?, ?)", 
                          ('game.activity', '活动控制', 'game', '控制游戏活动'))
            print("添加权限: game.activity - 活动控制")
        else:
            print("权限已存在: game.activity - 活动控制")
        
        # 2. 删除旧的游戏配置权限
        print("删除旧的游戏配置权限...")
        cursor.execute("DELETE FROM permissions WHERE code = 'game.config'")
        print("旧权限删除完成")
    
    print("游戏管理权限更新完成！")

if __name__ == "__main__":
    main()
