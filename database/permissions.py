#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限相关数据模型
包含 Permission 和 LevelPermission 模型
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from database.connection import DatabaseConnection
import logging

logger = logging.getLogger(__name__)
db = DatabaseConnection()


class Permission:
    """权限模型"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        code: str = "",
        name: str = "",
        category: str = "",
        description: str = "",
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.code = code
        self.name = name
        self.category = category
        self.description = description
        self.created_at = created_at
    
    @staticmethod
    def from_row(row) -> 'Permission':
        """从数据库行创建权限对象"""
        if row is None:
            return None
        return Permission(
            id=row['id'],
            code=row['code'],
            name=row['name'],
            category=row['category'],
            description=row['description'] if 'description' in row.keys() else '',
            created_at=row['created_at']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'created_at': str(self.created_at) if self.created_at else None
        }
    
    @staticmethod
    def get_all() -> List['Permission']:
        """获取所有权限"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM permissions ORDER BY category, id")
                rows = cursor.fetchall()
                return [Permission.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取所有权限失败: {e}")
            return []
    
    @staticmethod
    def get_by_category() -> Dict[str, List['Permission']]:
        """按分类获取权限"""
        permissions = Permission.get_all()
        result = {}
        for perm in permissions:
            if perm.category not in result:
                result[perm.category] = []
            result[perm.category].append(perm)
        return result
    
    @staticmethod
    def get_by_code(code: str) -> Optional['Permission']:
        """根据代码获取权限"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM permissions WHERE code = ?", (code,))
                row = cursor.fetchone()
                return Permission.from_row(row)
        except Exception as e:
            logger.error(f"获取权限失败: {e}")
            return None
    
    @staticmethod
    def create(code: str, name: str, category: str, description: str = "") -> Optional['Permission']:
        """创建新权限"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO permissions (code, name, category, description)
                    VALUES (?, ?, ?, ?)
                """, (code, name, category, description))
                
                permission_id = cursor.lastrowid
                logger.info(f"创建权限成功: {code}")
                
                return Permission.get_by_id(permission_id)
        except Exception as e:
            logger.error(f"创建权限失败: {e}")
            return None
    
    @staticmethod
    def get_by_id(permission_id: int) -> Optional['Permission']:
        """根据 ID 获取权限"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM permissions WHERE id = ?", (permission_id,))
                row = cursor.fetchone()
                return Permission.from_row(row)
        except Exception as e:
            logger.error(f"获取权限失败: {e}")
            return None


class LevelPermission:
    """Level 权限关联模型"""
    
    @staticmethod
    def get_level_permissions(level: int) -> List[str]:
        """获取指定 Level 的所有权限代码"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT p.code FROM permissions p
                    JOIN level_permissions lp ON p.id = lp.permission_id
                    WHERE lp.level = ?
                """, (level,))
                rows = cursor.fetchall()
                return [row['code'] for row in rows]
        except Exception as e:
            logger.error(f"获取 Level {level} 权限失败: {e}")
            return []
    
    @staticmethod
    def get_level_permission_ids(level: int) -> List[int]:
        """获取指定 Level 的所有权限 ID"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT permission_id FROM level_permissions
                    WHERE level = ?
                """, (level,))
                rows = cursor.fetchall()
                return [row['permission_id'] for row in rows]
        except Exception as e:
            logger.error(f"获取 Level {level} 权限 ID 失败: {e}")
            return []
    
    @staticmethod
    def set_level_permissions(level: int, permission_codes: List[str]) -> bool:
        """设置 Level 的权限（全量替换）"""
        try:
            with db.get_cursor() as cursor:
                # 删除现有权限
                cursor.execute("DELETE FROM level_permissions WHERE level = ?", (level,))
                
                # 添加新权限
                for code in permission_codes:
                    # 获取权限 ID
                    cursor.execute("SELECT id FROM permissions WHERE code = ?", (code,))
                    row = cursor.fetchone()
                    if row:
                        permission_id = row['id']
                        cursor.execute("""
                            INSERT INTO level_permissions (level, permission_id)
                            VALUES (?, ?)
                        """, (level, permission_id))
                
                logger.info(f"设置 Level {level} 权限成功: {len(permission_codes)} 项")
                return True
        except Exception as e:
            logger.error(f"设置 Level {level} 权限失败: {e}")
            return False
    
    @staticmethod
    def has_permission(level: int, permission_code: str) -> bool:
        """检查 Level 是否有指定权限"""
        permissions = LevelPermission.get_level_permissions(level)
        
        # 支持通配符
        if "*" in permissions:
            return True
        
        # 支持分类通配符，如 "account.*"
        category = permission_code.split('.')[0] if '.' in permission_code else ''
        if f"{category}.*" in permissions:
            return True
        
        return permission_code in permissions
