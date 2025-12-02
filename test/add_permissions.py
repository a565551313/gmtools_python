#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加所有缺失的权限
"""

from database.permissions import Permission

def add_permission_if_not_exists(code, name, category, description):
    """如果权限不存在则添加"""
    existing = Permission.get_by_code(code)
    if not existing:
        Permission.create(code, name, category, description)
        print(f"添加权限: {category} - {code}: {name}")
    else:
        print(f"权限已存在: {category} - {code}: {name}")

def main():
    # 账号管理权限
    account_permissions = [
        ("account.player_info", "玩家信息", "account", "查询玩家详细信息"),
        ("account.kick_battle", "踢出战斗", "account", "将玩家从战斗中踢出"),
        ("account.force_logout", "强制下线", "account", "强制玩家下线"),
        ("account.ban", "封禁账号", "account", "封禁玩家账号"),
        ("account.unban", "解封账号", "account", "解封玩家账号"),
        ("account.change_password", "修改密码", "account", "修改玩家密码"),
        ("account.give_title", "给予称谓", "account", "给予玩家称谓"),
        ("account.send_travel_fee", "发送路费", "account", "发送路费给玩家"),
        ("account.open_management", "开通管理", "account", "开通玩家管理权限"),
        ("account.close_management", "关闭管理", "account", "关闭玩家管理权限"),
    ]
    
    # 充值管理权限
    recharge_permissions = [
        ("recharge.currency", "货币充值", "recharge", "充值各种货币（仙玉、点卡等）"),
        ("recharge.gm_level", "GM等级充值", "recharge", "充值GM等级"),
        ("recharge.gm_coin", "GM币充值", "recharge", "充值GM币"),
        ("recharge.experience", "经验充值", "recharge", "充值经验"),
        ("recharge.cumulative", "累充充值", "recharge", "充值累计充值"),
        ("recharge.crafting_skill", "打造熟练", "recharge", "充值打造熟练度"),
        ("recharge.tailoring_skill", "裁缝熟练", "recharge", "充值裁缝熟练度"),
        ("recharge.alchemy_skill", "炼金熟练", "recharge", "充值炼金熟练度"),
        ("recharge.tempering_skill", "淬灵熟练", "recharge", "充值淬灵熟练度"),
        ("recharge.gang_contribution", "帮贡充值", "recharge", "充值帮派贡献"),
        ("recharge.faction_contribution", "门贡充值", "recharge", "充值门派贡献"),
        ("recharge.activity_points", "活跃积分", "recharge", "充值活跃积分"),
        ("recharge.combat_points", "比武积分", "recharge", "充值比武积分"),
        ("recharge.bagua", "八卦设置", "recharge", "设置玩家八卦"),
    ]
    
    # 宝宝管理权限
    pet_permissions = [
        ("pet.get_info", "获取宝宝信息", "pet", "获取玩家宝宝信息"),
        ("pet.get_mount", "获取坐骑", "pet", "获取玩家坐骑信息"),
        ("pet.modify_mount", "修改坐骑", "pet", "修改坐骑属性"),
        ("pet.custom_equip", "宝宝装备定制", "pet", "定制宝宝装备"),
    ]
    
    # 装备管理权限
    equipment_permissions = [
        ("equipment.custom", "装备定制", "equipment", "定制各种装备"),
        ("equipment.ornament", "灵饰定制", "equipment", "定制灵饰"),
        ("equipment.affix", "词条管理", "equipment", "管理装备词条"),
    ]
    
    # 添加所有权限
    all_permissions = account_permissions + recharge_permissions + pet_permissions + equipment_permissions
    
    for code, name, category, description in all_permissions:
        add_permission_if_not_exists(code, name, category, description)
    
    print("\n权限添加完成！")
    print(f"总共处理: {len(all_permissions)} 项权限")

if __name__ == "__main__":
    main()
