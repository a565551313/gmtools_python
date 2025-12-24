#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移：创建level_configs表并初始化默认数据
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """执行数据库迁移"""
    logger.info("开始数据库迁移：创建level_configs表...")
    
    try:
        with db.get_cursor() as cursor:
            # 检查表是否已存在
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='level_configs'
            """)
            
            if cursor.fetchone():
                logger.warning("level_configs表已存在，跳过创建")
                return
            
            # 创建level_configs表
            cursor.execute("""
                CREATE TABLE level_configs (
                    level_value INTEGER PRIMARY KEY,
                    display_name VARCHAR(50) NOT NULL,
                    description TEXT DEFAULT '',
                    sort_order INTEGER NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            logger.info("✓ 创建level_configs表成功")
            
            # 初始化默认等级数据（Level 1-10）
            default_levels = [
                (1, 'Level 1', '初级用户 - 基础权限', 1),
                (2, 'Level 2', '进阶用户 - 扩展权限', 2),
                (3, 'Level 3', '中级用户 - 中等权限', 3),
                (4, 'Level 4', '高级用户 - 较高权限', 4),
                (5, 'Level 5', '专业用户 - 专业权限', 5),
                (6, 'Level 6', '精英用户 - 精英权限', 6),
                (7, 'Level 7', '大师用户 - 大师权限', 7),
                (8, 'Level 8', '宗师用户 - 宗师权限', 8),
                (9, 'Level 9', '传奇用户 - 传奇权限', 9),
                (10, 'Level 10', '至尊用户 - 所有权限', 10),
            ]
            
            cursor.executemany("""
                INSERT INTO level_configs 
                (level_value, display_name, description, sort_order, is_active)
                VALUES (?, ?, ?, ?, 1)
            """, default_levels)
            
            logger.info(f"✓ 初始化 {len(default_levels)} 个默认等级配置成功")
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX idx_level_configs_sort_order 
                ON level_configs(sort_order)
            """)
            logger.info("✓ 创建索引成功")
            
            logger.info("=" * 50)
            logger.info("数据库迁移完成！")
            logger.info("=" * 50)
            
    except Exception as e:
        logger.error(f"✗ 数据库迁移失败: {e}")
        raise


if __name__ == "__main__":
    # 初始化数据库连接
    db.init_database()
    
    # 执行迁移
    migrate()
    
    # 验证迁移结果
    logger.info("\n验证迁移结果...")
    try:
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM level_configs")
            row = cursor.fetchone()
            count = row['count'] if row else 0
            logger.info(f"✓ level_configs表中共有 {count} 条记录")
            
            # 显示所有等级配置
            cursor.execute("""
                SELECT level_value, display_name, description 
                FROM level_configs 
                ORDER BY sort_order
            """)
            rows = cursor.fetchall()
            logger.info("\n当前等级配置：")
            logger.info("-" * 60)
            for row in rows:
                logger.info(f"  Level {row['level_value']}: {row['display_name']} - {row['description']}")
            logger.info("-" * 60)
            
    except Exception as e:
        logger.error(f"验证失败: {e}")
