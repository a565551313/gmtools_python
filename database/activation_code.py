#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
激活码模型
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from database.connection import DatabaseConnection
import logging
import random
import string

logger = logging.getLogger(__name__)
db = DatabaseConnection()


class ActivationCode:
    """激活码模型"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        code: str = "",
        level: int = 1,
        is_used: bool = False,
        used_by: Optional[int] = None,
        used_at: Optional[datetime] = None,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None
    ):
        self.id = id
        self.code = code
        self.level = level
        self.is_used = is_used
        self.used_by = used_by
        self.used_at = used_at
        self.created_at = created_at
        self.expires_at = expires_at
    
    @staticmethod
    def from_row(row) -> 'ActivationCode':
        """从数据库行创建激活码对象"""
        if row is None:
            return None
        return ActivationCode(
            id=row['id'],
            code=row['code'],
            level=row['level'],
            is_used=bool(row['is_used']),
            used_by=row['used_by'],
            used_at=row['used_at'],
            created_at=row['created_at'],
            expires_at=row['expires_at']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'code': self.code,
            'level': self.level,
            'is_used': self.is_used,
            'used_by': self.used_by,
            'used_at': str(self.used_at) if self.used_at else None,
            'created_at': str(self.created_at) if self.created_at else None,
            'expires_at': str(self.expires_at) if self.expires_at else None
        }
    
    @staticmethod
    def generate_code(length: int = 16) -> str:
        """生成随机激活码"""
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choice(characters) for _ in range(length))
    
    @staticmethod
    def create(level: int, expires_days: int = 30, count: int = 1) -> List['ActivationCode']:
        """创建激活码"""
        try:
            with db.get_cursor() as cursor:
                activation_codes = []
                expires_at = datetime.now() + timedelta(days=expires_days)
                
                for _ in range(count):
                    code = ActivationCode.generate_code()
                    
                    cursor.execute("""
                        INSERT INTO activation_codes (code, level, is_used, expires_at)
                        VALUES (?, ?, ?, ?)
                    """, (code, level, False, expires_at))
                    
                    code_id = cursor.lastrowid
                    activation_codes.append(ActivationCode(
                        id=code_id,
                        code=code,
                        level=level,
                        is_used=False,
                        expires_at=expires_at,
                        created_at=datetime.now()
                    ))
                
                logger.info(f"创建激活码成功: {count} 个，等级: {level}")
                return activation_codes
        except Exception as e:
            logger.error(f"创建激活码失败: {e}")
            return []
    
    @staticmethod
    def get_by_code(code: str) -> Optional['ActivationCode']:
        """根据代码获取激活码"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM activation_codes WHERE code = ?", (code,))
                row = cursor.fetchone()
                return ActivationCode.from_row(row)
        except Exception as e:
            logger.error(f"获取激活码失败: {e}")
            return None
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List['ActivationCode']:
        """获取所有激活码"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM activation_codes ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
                rows = cursor.fetchall()
                return [ActivationCode.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取激活码列表失败: {e}")
            return []
    
    @staticmethod
    def get_unused(level: Optional[int] = None, limit: int = 100) -> List['ActivationCode']:
        """获取未使用的激活码"""
        try:
            with db.get_cursor() as cursor:
                if level:
                    cursor.execute(
                        "SELECT * FROM activation_codes WHERE is_used = ? AND level = ? ORDER BY created_at DESC LIMIT ?",
                        (False, level, limit)
                    )
                else:
                    cursor.execute(
                        "SELECT * FROM activation_codes WHERE is_used = ? ORDER BY created_at DESC LIMIT ?",
                        (False, limit)
                    )
                rows = cursor.fetchall()
                return [ActivationCode.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取未使用激活码失败: {e}")
            return []
    
    @staticmethod
    def activate(code: str, user_id: int) -> Optional[int]:
        """激活码"""
        try:
            with db.get_cursor() as cursor:
                # 获取激活码
                cursor.execute("""
                    SELECT * FROM activation_codes 
                    WHERE code = ? AND is_used = ? AND expires_at > ?
                """, (code, False, datetime.now()))
                row = cursor.fetchone()
                
                if not row:
                    return None
                
                activation_code = ActivationCode.from_row(row)
                
                # 更新激活码状态
                cursor.execute("""
                    UPDATE activation_codes 
                    SET is_used = ?, used_by = ?, used_at = ?
                    WHERE id = ?
                """, (True, user_id, datetime.now(), activation_code.id))
                
                logger.info(f"激活码使用成功: {code}，用户: {user_id}")
                return activation_code.level
        except Exception as e:
            logger.error(f"激活码使用失败: {e}")
            return None
    
    @staticmethod
    def delete(code: str) -> bool:
        """删除激活码"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("DELETE FROM activation_codes WHERE code = ?", (code,))
                logger.info(f"删除激活码成功: {code}")
                return True
        except Exception as e:
            logger.error(f"删除激活码失败: {e}")
            return False
    
    @staticmethod
    def count() -> int:
        """获取激活码总数"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM activation_codes")
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"获取激活码数量失败: {e}")
            return 0
    
    @staticmethod
    def count_unused() -> int:
        """获取未使用激活码数量"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM activation_codes WHERE is_used = ?", (False,))
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"获取未使用激活码数量失败: {e}")
            return 0
