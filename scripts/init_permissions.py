#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化权限数据
创建预定义权限和默认 Level 权限模板
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db
from database.permissions import Permission, LevelPermission
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 预定义权限列表 (code, name, category, description)
PERMISSIONS = [
    # 账号管理 (3)
    ("account.view", "查看账号", "account", "查看账号基本信息"),
    ("account.recharge", "账号充值", "account", "为账号充值游戏币"),
    ("account.freeze", "冻结账号", "account", "冻结/解冻账号"),
    
    # 宠物管理 (3)
    ("pet.give", "赠送宠物", "pet", "赠送宠物给玩家"),
    ("pet.modify", "修改宠物", "pet", "修改宠物属性"),
    ("pet.delete", "删除宠物", "pet", "删除玩家宠物"),
    
    # 装备管理 (3)
    ("equipment.give", "赠送装备", "equipment", "赠送装备给玩家"),
    ("equipment.modify", "修改装备", "equipment", "修改装备属性"),
    ("equipment.delete", "删除装备", "equipment", "删除玩家装备"),
    
    # 礼物道具 (2)
    ("gift.send", "赠送道具", "gift", "赠送道具给玩家"),
    ("gift.batch", "批量赠送", "gift", "批量赠送道具"),
    
    # 角色管理 (3)
    ("character.view", "查看角色", "character", "查看角色详细信息"),
    ("character.modify", "修改角色", "character", "修改角色属性"),
    ("character.delete", "删除角色", "character", "删除玩家角色"),
    
    # 游戏管理 (4)
    ("game.announcement", "发送公告", "game", "发送游戏公告"),
    ("game.maintenance", "维护模式", "game", "开启/关闭维护模式"),
    ("game.config", "游戏配置", "game", "修改游戏配置"),
    ("game.rollback", "回档操作", "game", "执行数据回档"),
]

# 默认 Level 权限模板
DEFAULT_LEVEL_PERMISSIONS = {
    1: [
        "account.view",
        "gift.send",
    ],
    2: [
        "account.view",
        "account.recharge",
        "gift.send",
        "pet.give",
    ],
    3: [
        "account.view",
        "account.recharge",
        "pet.give",
        "equipment.give",
        "gift.send",
        "gift.batch",
    ],
    4: [
        "account.view",
        "account.recharge",
        "pet.give",
        "pet.modify",
        "equipment.give",
        "equipment.modify",
        "gift.send",
        "gift.batch",
        "character.view",
    ],
    5: [
        "account.view",
        "account.recharge",
        "account.freeze",
        "pet.give",
        "pet.modify",
        "equipment.give",
        "equipment.modify",
        "gift.send",
        "gift.batch",
        "character.view",
        "character.modify",
    ],
    6: [
        "account.view",
        "account.recharge",
        "account.freeze",
        "pet.give",
        "pet.modify",
        "pet.delete",
        "equipment.give",
        "equipment.modify",
        "equipment.delete",
        "gift.send",
        "gift.batch",
        "character.view",
        "character.modify",
        "game.announcement",
    ],
    7: [
        "account.view",
        "account.recharge",
        "account.freeze",
        "pet.give",
        "pet.modify",
        "pet.delete",
        "equipment.give",
        "equipment.modify",
        "equipment.delete",
        "gift.send",
        "gift.batch",
        "character.view",
        "character.modify",
        "character.delete",
        "game.announcement",
        "game.maintenance",
    ],
    8: [
        "account.view",
        "account.recharge",
        "account.freeze",
        "pet.give",
        "pet.modify",
        "pet.delete",
        "equipment.give",
        "equipment.modify",
        "equipment.delete",
        "gift.send",
        "gift.batch",
        "character.view",
        "character.modify",
        "character.delete",
        "game.announcement",
        "game.maintenance",
        "game.config",
    ],
    9: [
        "account.view",
        "account.recharge",
        "account.freeze",
        "pet.give",
        "pet.modify",
        "pet.delete",
        "equipment.give",
        "equipment.modify",
        "equipment.delete",
        "gift.send",
        "gift.batch",
        "character.view",
        "character.modify",
        "character.delete",
        "game.announcement",
        "game.maintenance",
        "game.config",
        "game.rollback",
    ],
    10: ["*"],  # 所有权限
}


def init_permissions():
    """初始化权限数据"""
    print("=" * 60)
    print("初始化权限系统")
    print("=" * 60)
    
    # 1. 初始化数据库表
    print("\n[1/4] 初始化数据库表...")
    db.init_database()
    print("✓ 数据库表创建完成")
    
    # 2. 创建权限
    print("\n[2/4] 创建权限...")
    created_count = 0
    for code, name, category, description in PERMISSIONS:
        existing = Permission.get_by_code(code)
        if not existing:
            if Permission.create(code, name, category, description):
                created_count += 1
            else:
                print(f"✗ 创建权限失败: {code}")
        else:
            logger.debug(f"权限已存在: {code}")
    print(f"✓ 创建了 {created_count} 个新权限")
    
    # 3. 配置 Level 权限
    print("\n[3/4] 配置 Level 权限模板...")
    for level, permission_codes in DEFAULT_LEVEL_PERMISSIONS.items():
        if LevelPermission.set_level_permissions(level, permission_codes):
            perm_count = len(permission_codes)
            print(f"✓ Level {level:2d}: {perm_count:2d} 项权限")
        else:
            print(f"✗ Level {level} 配置失败")
    
    # 4. 验证
    print("\n[4/4] 验证权限配置...")
    all_permissions = Permission.get_all()
    print(f"✓ 总权限数: {len(all_permissions)}")
    
    # 按分类统计
    by_category = Permission.get_by_category()
    for category, perms in sorted(by_category.items()):
        print(f"  - {category}: {len(perms)} 项")
    
    print("\n" + "=" * 60)
    print("权限系统初始化完成!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        init_permissions()
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
