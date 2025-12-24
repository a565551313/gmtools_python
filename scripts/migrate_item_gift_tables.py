#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道具赠送权限细化系统 - 数据库迁移脚本

创建以下表：
1. item_configs - 道具配置表
2. item_level_limits - 道具等级限制表
3. item_gift_logs - 道具发送记录表
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import db
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_item_configs_table():
    """创建道具配置表"""
    logger.info("创建 item_configs 表...")
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL UNIQUE,
                display_name TEXT NOT NULL,
                description TEXT,
                icon_url TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_item_configs_name ON item_configs(item_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_configs_is_active ON item_configs(is_active)")
    
    logger.info("✓ item_configs 表创建成功")


def create_item_level_limits_table():
    """创建道具等级限制表"""
    logger.info("创建 item_level_limits 表...")
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_level_limits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                user_level INTEGER NOT NULL,
                min_quantity INTEGER DEFAULT 1,
                max_quantity INTEGER DEFAULT 99,
                reset_period_hours INTEGER DEFAULT 24,
                period_total_limit INTEGER DEFAULT 999,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(item_name, user_level),
                FOREIGN KEY (item_name) REFERENCES item_configs(item_name) ON DELETE CASCADE
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_level_limits_level ON item_level_limits(user_level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_level_limits_item ON item_level_limits(item_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_level_limits_active ON item_level_limits(is_active)")
    
    logger.info("✓ item_level_limits 表创建成功")


def create_item_gift_logs_table():
    """创建道具发送记录表"""
    logger.info("创建 item_gift_logs 表...")
    
    with db.get_cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS item_gift_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_username TEXT NOT NULL,
                sender_level INTEGER NOT NULL,
                recipient_username TEXT NOT NULL,
                item_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                reset_period_hours INTEGER,
                is_admin_send BOOLEAN DEFAULT 0,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_name) REFERENCES item_configs(item_name)
            )
        """)
        
        # 创建索引 - 用于快速查询周期配额
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_gift_logs_sender ON item_gift_logs(sender_username, sent_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_gift_logs_item_sender ON item_gift_logs(item_name, sender_username, sent_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_item_gift_logs_recipient ON item_gift_logs(recipient_username, sent_at)")
    
    logger.info("✓ item_gift_logs 表创建成功")


def insert_sample_data():
    """插入示例数据（可选）"""
    logger.info("插入示例道具配置...")
    
    sample_items = [
        ("飞行符", "飞行符", "快速移动的神奇符咒", None),
        ("气血丹", "气血丹", "恢复生命值的丹药", None),
        ("魔法药水", "魔法药水", "恢复魔法值的药水", None),
        ("经验卷轴", "经验卷轴", "增加经验值的卷轴", None),
    ]
    
    with db.get_cursor() as cursor:
        for item_name, display_name, description, icon_url in sample_items:
            try:
                cursor.execute("""
                    INSERT INTO item_configs (item_name, display_name, description, icon_url, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (item_name, display_name, description, icon_url))
                logger.info(f"  ✓ 添加道具: {display_name}")
            except Exception as e:
                logger.warning(f"  ⚠ 道具 {display_name} 可能已存在，跳过")
    
    # 为示例道具添加等级限制
    logger.info("为示例道具配置等级限制...")
    
    # 飞行符的等级限制配置示例
    level_limits = [
        # item_name, level, min, max, period_hours, period_total
        ("飞行符", 1, 1, 10, 24, 50),
        ("飞行符", 2, 1, 20, 24, 100),
        ("飞行符", 3, 1, 50, 24, 200),
        ("飞行符", 4, 1, 99, 24, 500),
        ("飞行符", 5, 1, 99, 24, 999),
        
        ("气血丹", 1, 1, 5, 24, 20),
        ("气血丹", 2, 1, 10, 24, 50),
        ("气血丹", 3, 1, 20, 24, 100),
        ("气血丹", 4, 1, 50, 24, 200),
        ("气血丹", 5, 1, 99, 24, 500),
    ]
    
    with db.get_cursor() as cursor:
        for item_name, level, min_qty, max_qty, period_hours, period_total in level_limits:
            try:
                cursor.execute("""
                    INSERT INTO item_level_limits 
                    (item_name, user_level, min_quantity, max_quantity, reset_period_hours, period_total_limit, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (item_name, level, min_qty, max_qty, period_hours, period_total))
            except Exception as e:
                logger.warning(f"  ⚠ 等级限制配置可能已存在，跳过: {item_name} - Level {level}")
    
    logger.info("✓ 示例数据插入完成")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("开始执行道具赠送权限系统数据库迁移")
    logger.info("=" * 60)
    
    try:
        # 创建表
        create_item_configs_table()
        create_item_level_limits_table()
        create_item_gift_logs_table()
        
        # 插入示例数据
        insert_sample_data()
        
        logger.info("=" * 60)
        logger.info("✓ 数据库迁移完成！")
        logger.info("=" * 60)
        logger.info("\n创建的表：")
        logger.info("  1. item_configs - 道具配置表")
        logger.info("  2. item_level_limits - 道具等级限制表")
        logger.info("  3. item_gift_logs - 道具发送记录表")
        logger.info("\n下一步：")
        logger.info("  1. 实现数据模型类 (database/item_gift.py)")
        logger.info("  2. 实现业务逻辑 (services/item_gift_service.py)")
        logger.info("  3. 创建 API 路由 (routes/item_gift_routes.py)")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 迁移失败: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
