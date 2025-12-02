#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移除旧的权限，只保留新添加的权限
"""

from database.connection import db

def main():
    # 要保留的权限代码列表
    keep_permissions = [
        # 账号管理
        'account.player_info',
        'account.kick_battle',
        'account.force_logout',
        'account.ban',
        'account.unban',
        'account.change_password',
        'account.give_title',
        'account.send_travel_fee',
        'account.open_management',
        'account.close_management',
        
        # 角色管理
        'character.view',
        'character.modify',
        
        # 装备管理
        'equipment.custom',
        'equipment.ornament',
        'equipment.affix',
        
        # 游戏管理
        'game.announcement',
        'game.config',
        
        # 礼物道具
        'gift.send',
        'gift.batch',
        
        # 宠物管理
        'pet.get_info',
        'pet.modify',
        'pet.custom_equip',
        'pet.get_mount',
        'pet.modify_mount',
        
        # 充值管理
        'recharge.currency',
        'recharge.gm_level',
        'recharge.gm_coin',
        'recharge.experience',
        'recharge.cumulative',
        'recharge.crafting_skill',
        'recharge.tailoring_skill',
        'recharge.alchemy_skill',
        'recharge.tempering_skill',
        'recharge.gang_contribution',
        'recharge.faction_contribution',
        'recharge.activity_points',
        'recharge.combat_points',
        'recharge.bagua',
    ]
    
    print("准备移除旧的权限...")
    print(f"要保留的权限数：{len(keep_permissions)}")
    print("=" * 60)
    
    with db.get_cursor() as cursor:
        # 获取所有权限
        cursor.execute("SELECT id, code, name, category FROM permissions")
        all_permissions = cursor.fetchall()
        
        print(f"数据库中总权限数：{len(all_permissions)}")
        
        # 找出要删除的权限
        permissions_to_delete = []
        for perm in all_permissions:
            if perm['code'] not in keep_permissions:
                permissions_to_delete.append(perm)
        
        print(f"要删除的权限数：{len(permissions_to_delete)}")
        
        if permissions_to_delete:
            print("要删除的权限：")
            for perm in permissions_to_delete:
                print(f"  - {perm['code']} ({perm['name']}) - {perm['category']}")
            
            # 执行删除
            print("\n执行删除...")
            for perm in permissions_to_delete:
                # 删除权限与等级的关联
                cursor.execute("DELETE FROM level_permissions WHERE permission_id = ?", (perm['id'],))
                # 删除权限本身
                cursor.execute("DELETE FROM permissions WHERE id = ?", (perm['id'],))
            
            print(f"成功删除 {len(permissions_to_delete)} 个旧权限")
        else:
            print("没有需要删除的旧权限")
    
    print("=" * 60)
    print("权限清理完成！")

if __name__ == "__main__":
    main()
