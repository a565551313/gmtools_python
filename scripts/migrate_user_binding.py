#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户角色ID绑定系统 - 数据库迁移脚本
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

def migrate():
    """执行迁移"""
    logger.info("开始数据库迁移...")
    
    with db.get_cursor() as cursor:
        # 1. 为 users 表添加 bound_ids 字段
        try:
            logger.info("检查 users 表 bound_ids 字段...")
            cursor.execute("PRAGMA table_info(users)")
            columns = [row['name'] for row in cursor.fetchall()]
            if 'bound_ids' not in columns:
                logger.info("添加 bound_ids 字段到 users 表...")
                cursor.execute("ALTER TABLE users ADD COLUMN bound_ids TEXT")
                logger.info("✓ users 表更新成功")
            else:
                logger.info("  users 表已存在 bound_ids 字段")
        except Exception as e:
            logger.error(f"更新 users 表失败: {e}")
            return False

        # 2. 为 level_configs 表添加 max_bind_ids 字段
        try:
            logger.info("检查 level_configs 表 max_bind_ids 字段...")
            cursor.execute("PRAGMA table_info(level_configs)")
            columns = [row['name'] for row in cursor.fetchall()]
            if 'max_bind_ids' not in columns:
                logger.info("添加 max_bind_ids 字段到 level_configs 表...")
                # 默认值为 1
                cursor.execute("ALTER TABLE level_configs ADD COLUMN max_bind_ids INTEGER DEFAULT 1")
                logger.info("✓ level_configs 表更新成功")
            else:
                logger.info("  level_configs 表已存在 max_bind_ids 字段")
        except Exception as e:
            logger.error(f"更新 level_configs 表失败: {e}")
            return False

    logger.info("✓ 数据库迁移完成！")
    return True

if __name__ == "__main__":
    success = migrate()
    sys.exit(0 if success else 1)
