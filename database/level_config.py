#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等级配置模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from database.connection import db
import logging

logger = logging.getLogger(__name__)


class LevelConfig:
    """等级配置模型"""
    
    def __init__(
        self,
        level_value: int,
        display_name: str,
        description: str = "",
        sort_order: int = 0,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.level_value = level_value
        self.display_name = display_name
        self.description = description
        self.sort_order = sort_order
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
    
    @staticmethod
    def from_row(row) -> Optional['LevelConfig']:
        """从数据库行创建等级配置对象"""
        if row is None:
            return None
        return LevelConfig(
            level_value=row['level_value'],
            display_name=row['display_name'],
            description=row['description'] if row['description'] else "",
            sort_order=row['sort_order'],
            is_active=bool(row['is_active']),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'level_value': self.level_value,
            'display_name': self.display_name,
            'description': self.description,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'created_at': str(self.created_at) if self.created_at else None,
            'updated_at': str(self.updated_at) if self.updated_at else None
        }
    
    @staticmethod
    def get_all(active_only: bool = True) -> List['LevelConfig']:
        """获取所有等级配置（按sort_order排序）"""
        try:
            with db.get_cursor() as cursor:
                if active_only:
                    cursor.execute("""
                        SELECT * FROM level_configs 
                        WHERE is_active = 1
                        ORDER BY sort_order ASC, level_value ASC
                    """)
                else:
                    cursor.execute("""
                        SELECT * FROM level_configs 
                        ORDER BY sort_order ASC, level_value ASC
                    """)
                rows = cursor.fetchall()
                return [LevelConfig.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取等级配置列表失败: {e}")
            return []
    
    @staticmethod
    def get_by_level(level_value: int) -> Optional['LevelConfig']:
        """获取指定等级的配置"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM level_configs WHERE level_value = ?
                """, (level_value,))
                row = cursor.fetchone()
                return LevelConfig.from_row(row)
        except Exception as e:
            logger.error(f"获取等级配置失败 (level: {level_value}): {e}")
            return None
    
    @staticmethod
    def create(
        level_value: int, 
        display_name: str,
        description: str = "",
        sort_order: int = None
    ) -> Optional['LevelConfig']:
        """创建新等级"""
        try:
            # 如果未指定sort_order，使用level_value
            if sort_order is None:
                sort_order = level_value
            
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO level_configs 
                    (level_value, display_name, description, sort_order, is_active)
                    VALUES (?, ?, ?, ?, ?)
                """, (level_value, display_name, description, sort_order, True))
                
                logger.info(f"创建等级配置成功: Level {level_value} - {display_name}")
                return LevelConfig.get_by_level(level_value)
        except Exception as e:
            logger.error(f"创建等级配置失败: {e}")
            return None
    
    def update(self) -> bool:
        """更新等级信息"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE level_configs 
                    SET display_name = ?, description = ?, sort_order = ?, 
                        is_active = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE level_value = ?
                """, (
                    self.display_name, 
                    self.description, 
                    self.sort_order,
                    self.is_active,
                    self.level_value
                ))
                
                logger.info(f"更新等级配置成功: Level {self.level_value}")
                return True
        except Exception as e:
            logger.error(f"更新等级配置失败: {e}")
            return False
    
    @staticmethod
    def delete(level_value: int) -> bool:
        """删除等级（软删除：标记为不活跃）"""
        try:
            # 检查是否可以删除
            can_delete, reason = LevelConfig.can_delete(level_value)
            if not can_delete:
                logger.warning(f"无法删除等级 {level_value}: {reason}")
                return False
            
            with db.get_cursor() as cursor:
                # 软删除：设置is_active为False
                cursor.execute("""
                    UPDATE level_configs 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE level_value = ?
                """, (level_value,))
                
                logger.info(f"删除等级配置成功: Level {level_value}")
                return True
        except Exception as e:
            logger.error(f"删除等级配置失败: {e}")
            return False
    
    @staticmethod
    def can_delete(level_value: int) -> tuple[bool, str]:
        """检查等级是否可以删除"""
        try:
            with db.get_cursor() as cursor:
                # 检查是否有用户使用该等级
                cursor.execute("""
                    SELECT COUNT(*) as count FROM users WHERE level = ?
                """, (level_value,))
                row = cursor.fetchone()
                user_count = row['count'] if row else 0
                
                if user_count > 0:
                    return False, f"{user_count} 个用户正在使用该等级"
                
                # 检查是否有未使用的激活码指向该等级
                cursor.execute("""
                    SELECT COUNT(*) as count FROM activation_codes 
                    WHERE level = ? AND is_used = 0
                """, (level_value,))
                row = cursor.fetchone()
                code_count = row['count'] if row else 0
                
                if code_count > 0:
                    return False, f"{code_count} 个未使用的激活码指向该等级"
                
                return True, "可以删除"
        except Exception as e:
            logger.error(f"检查等级删除条件失败: {e}")
            return False, f"检查失败: {str(e)}"
    
    @staticmethod
    def get_usage_stats(level_value: int) -> Dict[str, int]:
        """获取等级使用统计"""
        try:
            with db.get_cursor() as cursor:
                # 用户数量
                cursor.execute("""
                    SELECT COUNT(*) as count FROM users WHERE level = ?
                """, (level_value,))
                row = cursor.fetchone()
                user_count = row['count'] if row else 0
                
                # 激活码数量（总数和未使用数）
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN is_used = 0 THEN 1 ELSE 0 END) as unused
                    FROM activation_codes 
                    WHERE level = ?
                """, (level_value,))
                row = cursor.fetchone()
                code_total = row['total'] if row and row['total'] else 0
                code_unused = row['unused'] if row and row['unused'] else 0
                
                return {
                    'user_count': user_count,
                    'activation_code_total': code_total,
                    'activation_code_unused': code_unused
                }
        except Exception as e:
            logger.error(f"获取等级使用统计失败: {e}")
            return {
                'user_count': 0,
                'activation_code_total': 0,
                'activation_code_unused': 0
            }
    
    @staticmethod
    def count() -> int:
        """获取等级总数（仅活跃）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count FROM level_configs WHERE is_active = 1
                """)
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"获取等级数量失败: {e}")
            return 0
