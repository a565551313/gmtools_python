#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from database.connection import db
from database.permissions import LevelPermission
import logging

logger = logging.getLogger(__name__)


class User:
    """用户模型"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        username: str = "",
        email: str = "",
        password_hash: str = "",
        level: int = 1,
        role: str = "user",
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.level = level
        self.role = role
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_login = last_login
    
    @staticmethod
    def from_row(row) -> 'User':
        """从数据库行创建用户对象"""
        if row is None:
            return None
        return User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            password_hash=row['password_hash'],
            level=row['level'],
            role=row['role'],
            is_active=bool(row['is_active']),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            last_login=row['last_login']
        )
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """转换为字典"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'level': self.level,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': str(self.created_at) if self.created_at else None,
            'updated_at': str(self.updated_at) if self.updated_at else None,
            'last_login': str(self.last_login) if self.last_login else None,
            'permissions': LevelPermission.get_level_permissions(self.level)
        }
        if include_password:
            data['password_hash'] = self.password_hash
        return data
    
    @staticmethod
    def create(username: str, email: str, password_hash: str, 
               level: int = 1, role: str = "user") -> Optional['User']:
        """创建新用户"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, level, role)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, email, password_hash, level, role))
                
                user_id = cursor.lastrowid
                logger.info(f"创建用户成功: {username} (ID: {user_id})")
                
                return User.get_by_id(user_id)
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return None
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional['User']:
        """通过 ID 获取用户"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                row = cursor.fetchone()
                return User.from_row(row)
        except Exception as e:
            logger.error(f"获取用户失败 (ID: {user_id}): {e}")
            return None
    
    @staticmethod
    def get_by_username(username: str) -> Optional['User']:
        """通过用户名获取用户"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                return User.from_row(row)
        except Exception as e:
            logger.error(f"获取用户失败 (username: {username}): {e}")
            return None
    
    @staticmethod
    def get_by_email(email: str) -> Optional['User']:
        """通过邮箱获取用户"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
                row = cursor.fetchone()
                return User.from_row(row)
        except Exception as e:
            logger.error(f"获取用户失败 (email: {email}): {e}")
            return None
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List['User']:
        """获取所有用户"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
                    (limit, offset)
                )
                rows = cursor.fetchall()
                return [User.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return []
    
    @staticmethod
    def count() -> int:
        """获取用户总数"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM users")
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"获取用户数量失败: {e}")
            return 0
    
    def update(self) -> bool:
        """更新用户信息"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET email = ?, level = ?, role = ?, is_active = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (self.email, self.level, self.role, self.is_active, self.id))
                
                logger.info(f"更新用户成功: {self.username}")
                return True
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return False
    
    def update_password(self, new_password_hash: str) -> bool:
        """更新密码"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_password_hash, self.id))
                
                self.password_hash = new_password_hash
                logger.info(f"更新密码成功: {self.username}")
                return True
        except Exception as e:
            logger.error(f"更新密码失败: {e}")
            return False
    
    def update_last_login(self) -> bool:
        """更新最后登录时间"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET last_login = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (self.id,))
                
                return True
        except Exception as e:
            logger.error(f"更新登录时间失败: {e}")
            return False
    
    def delete(self) -> bool:
        """删除用户"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("DELETE FROM users WHERE id = ?", (self.id,))
                logger.info(f"删除用户成功: {self.username}")
                return True
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            return False


class AuditLog:
    """操作日志模型"""
    
    @staticmethod
    def create(user_id: Optional[int], action: str, resource: Optional[str] = None,
               details: Optional[str] = None, ip_address: Optional[str] = None) -> bool:
        """创建操作日志"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO audit_logs (user_id, action, resource, details, ip_address)
                    VALUES (?, ?, ?, ?, ?)
                """, (user_id, action, resource, details, ip_address))
                
                return True
        except Exception as e:
            logger.error(f"创建审计日志失败: {e}")
            return False
    
    @staticmethod
    def get_by_user(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """获取用户的操作日志"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM audit_logs 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取审计日志失败: {e}")
            return []
    
    @staticmethod
    def get_all(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """获取所有操作日志"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT al.*, u.username 
                    FROM audit_logs al
                    LEFT JOIN users u ON al.user_id = u.id
                    ORDER BY al.created_at DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取审计日志失败: {e}")
            return []
    
    @staticmethod
    def count_all() -> int:
        """获取日志总数"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM audit_logs")
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"获取日志数量失败: {e}")
            return 0
    
    @staticmethod
    def delete_by_ids(log_ids: List[int]) -> int:
        """删除指定ID的日志"""
        try:
            with db.get_cursor() as cursor:
                placeholders = ','.join('?' * len(log_ids))
                cursor.execute(
                    f"DELETE FROM audit_logs WHERE id IN ({placeholders})",
                    log_ids
                )
                deleted_count = cursor.rowcount
                logger.info(f"删除了 {deleted_count} 条审计日志")
                return deleted_count
        except Exception as e:
            logger.error(f"删除审计日志失败: {e}")
            return 0
    
    @staticmethod
    def delete_all() -> int:
        """删除所有日志"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("DELETE FROM audit_logs")
                deleted_count = cursor.rowcount
                logger.info(f"清空了所有审计日志（共 {deleted_count} 条）")
                return deleted_count
        except Exception as e:
            logger.error(f"清空审计日志失败: {e}")
            return 0
