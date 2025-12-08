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


class Message:
    """消息模型"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        sender_id: Optional[int] = None,
        sender_name: str = "",
        recipient_id: int = 0,
        title: str = "",
        content: str = "",
        is_read: bool = False,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.recipient_id = recipient_id
        self.title = title
        self.content = content
        self.is_read = is_read
        self.created_at = created_at
    
    @staticmethod
    def from_row(row) -> 'Message':
        """从数据库行创建消息对象"""
        if row is None:
            return None
        return Message(
            id=row['id'],
            sender_id=row['sender_id'],
            sender_name=row['sender_name'],
            recipient_id=row['recipient_id'],
            title=row['title'],
            content=row['content'],
            is_read=bool(row['is_read']),
            created_at=row['created_at']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'sender_name': self.sender_name,
            'recipient_id': self.recipient_id,
            'title': self.title,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': str(self.created_at) if self.created_at else None
        }
    
    @staticmethod
    def create(sender_id: Optional[int], sender_name: str, recipient_id: int,
               title: str, content: str) -> Optional['Message']:
        """创建新消息"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO messages (sender_id, sender_name, recipient_id, title, content)
                    VALUES (?, ?, ?, ?, ?)
                """, (sender_id, sender_name, recipient_id, title, content))
                
                message_id = cursor.lastrowid
                logger.info(f"创建消息成功: ID {message_id}")
                
                # 直接创建Message对象返回，避免重新查询数据库
                return Message(
                    id=message_id,
                    sender_id=sender_id,
                    sender_name=sender_name,
                    recipient_id=recipient_id,
                    title=title,
                    content=content,
                    is_read=False,
                    created_at=datetime.now()
                )
        except Exception as e:
            logger.error(f"创建消息失败: {e}")
            return None
    
    @staticmethod
    def get_by_id(message_id: int) -> Optional['Message']:
        """通过 ID 获取消息"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM messages WHERE id = ?", (message_id,))
                row = cursor.fetchone()
                return Message.from_row(row)
        except Exception as e:
            logger.error(f"获取消息失败 (ID: {message_id}): {e}")
            return None
    
    @staticmethod
    def get_by_recipient(recipient_id: int, limit: int = 50, offset: int = 0) -> List['Message']:
        """获取收件人的消息"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE recipient_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """, (recipient_id, limit, offset))
                
                rows = cursor.fetchall()
                return [Message.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取收件人消息失败: {e}")
            return []
    
    @staticmethod
    def get_by_sender(sender_id: int, limit: int = 50, offset: int = 0) -> List['Message']:
        """获取发件人的消息"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM messages 
                    WHERE sender_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ? OFFSET ?
                """, (sender_id, limit, offset))
                
                rows = cursor.fetchall()
                return [Message.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取发件人消息失败: {e}")
            return []
    
    @staticmethod
    def update_read_status(message_id: int, is_read: bool) -> bool:
        """更新消息阅读状态"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE messages 
                    SET is_read = ? 
                    WHERE id = ?
                """, (is_read, message_id))
                
                return True
        except Exception as e:
            logger.error(f"更新消息状态失败: {e}")
            return False
    
    @staticmethod
    def delete_by_id(message_id: int) -> bool:
        """删除消息"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
                
                logger.info(f"删除消息成功: ID {message_id}")
                return True
        except Exception as e:
            logger.error(f"删除消息失败: {e}")
            return False
    
    @staticmethod
    def delete_by_ids(message_ids: List[int]) -> int:
        """删除指定ID的消息"""
        try:
            with db.get_cursor() as cursor:
                placeholders = ','.join('?' * len(message_ids))
                cursor.execute(
                    f"DELETE FROM messages WHERE id IN ({placeholders})",
                    message_ids
                )
                deleted_count = cursor.rowcount
                logger.info(f"删除了 {deleted_count} 条消息")
                return deleted_count
        except Exception as e:
            logger.error(f"批量删除消息失败: {e}")
            return 0
    
    @staticmethod
    def count_unread(recipient_id: int) -> int:
        """统计未读消息数量"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count 
                    FROM messages 
                    WHERE recipient_id = ? AND is_read = 0
                """, (recipient_id,))
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"统计未读消息失败: {e}")
            return 0
