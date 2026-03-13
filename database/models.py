#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户数据模型
"""

from datetime import datetime
from typing import Optional, List, Dict, Any, Tuple
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
        last_login: Optional[datetime] = None,
        bound_ids: Optional[str] = None,
        password_plain: Optional[str] = None
    ):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.password_plain = password_plain
        self.level = level
        self.role = role
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
        self.last_login = last_login
        self.bound_ids = bound_ids
    
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
            last_login=row['last_login'],
            bound_ids=row['bound_ids'] if 'bound_ids' in row.keys() else None,
            password_plain=row['password_plain'] if 'password_plain' in row.keys() else None
        )
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """转换为字典"""
        from database.level_config import LevelConfig
        config = LevelConfig.get_by_level(self.level)
        max_bind = config.max_bind_ids if config else 1
        
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
            'bound_ids': self.get_bound_ids(),
            'max_bind_ids': max_bind,
            'password_plain': self.password_plain,
            'permissions': LevelPermission.get_level_permissions(self.level)
        }
        if include_password:
            data['password_hash'] = self.password_hash
        return data
    
    @staticmethod
    def create(username: str, email: str, password_hash: str, 
               level: int = 1, role: str = "user", password_plain: Optional[str] = None) -> Optional['User']:
        """创建新用户"""
        user_id = None
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, password_plain, level, role)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (username, email, password_hash, password_plain, level, role))
                
                user_id = cursor.lastrowid
                logger.info(f"创建用户成功: {username} (ID: {user_id})")
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            return None
            
        if user_id:
            return User.get_by_id(user_id)
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
    
    def update(self, email: Optional[str] = None, level: Optional[int] = None, 
               role: Optional[str] = None, is_active: Optional[bool] = None,
               bound_ids: Optional[str] = None, password_hash: Optional[str] = None,
               password_plain: Optional[str] = None) -> bool:
        """更新用户信息"""
        try:
            updates = []
            params = []
            
            # 如果没有提供任何参数，则更新所有字段（使用当前对象的值）
            if all(v is None for v in [email, level, role, is_active, bound_ids, password_hash, password_plain]):
                updates = ["email = ?", "level = ?", "role = ?", "is_active = ?", "bound_ids = ?", "password_hash = ?", "password_plain = ?"]
                params = [self.email, self.level, self.role, 1 if self.is_active else 0, self.bound_ids, self.password_hash, self.password_plain]
            else:
                if email is not None:
                    updates.append("email = ?")
                    params.append(email)
                    self.email = email
                
                if level is not None:
                    updates.append("level = ?")
                    params.append(level)
                    self.level = level
                    
                if role is not None:
                    updates.append("role = ?")
                    params.append(role)
                    self.role = role
                    
                if is_active is not None:
                    updates.append("is_active = ?")
                    params.append(1 if is_active else 0)
                    self.is_active = is_active

                if bound_ids is not None:
                    updates.append("bound_ids = ?")
                    params.append(bound_ids)
                    self.bound_ids = bound_ids

                if password_hash is not None:
                    updates.append("password_hash = ?")
                    params.append(password_hash)
                    self.password_hash = password_hash

                if password_plain is not None:
                    updates.append("password_plain = ?")
                    params.append(password_plain)
                    self.password_plain = password_plain
            
            if not updates:
                return True
                
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(self.id)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = ?"
            
            with db.get_cursor() as cursor:
                cursor.execute(query, tuple(params))
                logger.info(f"更新用户成功: {self.username} (ID: {self.id})")
                return True
        except Exception as e:
            logger.error(f"更新用户失败: {e}")
            return False
    
    def update_password(self, new_password_hash: str, new_password_plain: Optional[str] = None) -> bool:
        """更新密码"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = ?, password_plain = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_password_hash, new_password_plain, self.id))
                
                self.password_hash = new_password_hash
                self.password_plain = new_password_plain
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

    def get_bound_ids(self) -> List[str]:
        """获取绑定的角色 ID 列表"""
        if not self.bound_ids:
            return []
        # 同时支持逗号和换行符分隔
        import re
        return [id.strip() for id in re.split(r'[,\n\r]+', self.bound_ids) if id.strip()]

    def set_bound_ids(self, ids: List[str]) -> bool:
        """设置绑定的角色 ID 列表"""
        self.bound_ids = ','.join(ids)
        return self.update(bound_ids=self.bound_ids)

    def bind_id(self, character_id: str) -> Tuple[bool, str]:
        """绑定新的角色 ID"""
        current_ids = self.get_bound_ids()
        
        # 检查是否已绑定
        if character_id in current_ids:
            return False, "该角色 ID 已绑定"
            
        # 检查绑定上限
        from database.level_config import LevelConfig
        config = LevelConfig.get_by_level(self.level)
        max_bind = config.max_bind_ids if config else 1
        
        if len(current_ids) >= max_bind:
            return False, f"绑定数量已达上限 ({max_bind})"
            
        current_ids.append(character_id)
        self.bound_ids = ','.join(current_ids)
        
        if self.update(bound_ids=self.bound_ids):
            return True, "绑定成功"
        return False, "数据库更新失败"


class AuditLog:
    """审计日志模型"""
    
    def __init__(
        self,
        id: Optional[int] = None,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        action: str = "",
        resource: Optional[str] = None,
        details: Optional[str] = None,
        ip_address: Optional[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.user_id = user_id
        self.username = username  # 关联查询得到的用户名
        self.action = action
        self.resource = resource
        self.details = details
        self.ip_address = ip_address
        self.created_at = created_at
    
    @staticmethod
    def from_row(row) -> 'AuditLog':
        """从数据库行创建审计日志对象"""
        if row is None:
            return None
        return AuditLog(
            id=row['id'],
            user_id=row['user_id'],
            username=row['username'] if 'username' in row.keys() else None,
            action=row['action'],
            resource=row['resource'],
            details=row['details'],
            ip_address=row['ip_address'],
            created_at=row['created_at']
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action,
            'resource': self.resource,
            'details': self.details,
            'ip_address': self.ip_address,
            'created_at': str(self.created_at) if self.created_at else None
        }
    
    @staticmethod
    def create(user_id: Optional[int], action: str, resource: Optional[str] = None, 
               details: Optional[str] = None, ip_address: Optional[str] = None) -> bool:
        """创建审计日志"""
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
    def get_all(limit: int = 100, offset: int = 0) -> List['AuditLog']:
        """获取所有审计日志（包含用户名）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT l.*, u.username 
                    FROM audit_logs l
                    LEFT JOIN users u ON l.user_id = u.id
                    ORDER BY l.created_at DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                rows = cursor.fetchall()
                return [AuditLog.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取审计日志列表失败: {e}")
            return []

    @staticmethod
    def get_by_user(user_id: int, limit: int = 50) -> List['AuditLog']:
        """获取指定用户的审计日志"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT l.*, u.username 
                    FROM audit_logs l
                    LEFT JOIN users u ON l.user_id = u.id
                    WHERE l.user_id = ? 
                    ORDER BY l.created_at DESC 
                    LIMIT ?
                """, (user_id, limit))
                rows = cursor.fetchall()
                return [AuditLog.from_row(row) for row in rows]
        except Exception as e:
            logger.error(f"获取用户审计日志失败: {e}")
            return []

    @staticmethod
    def delete_by_ids(log_ids: List[int]) -> bool:
        """批量删除审计日志"""
        if not log_ids:
            return True
        try:
            placeholders = ','.join(['?'] * len(log_ids))
            query = f"DELETE FROM audit_logs WHERE id IN ({placeholders})"
            with db.get_cursor() as cursor:
                cursor.execute(query, tuple(log_ids))
                return True
        except Exception as e:
            logger.error(f"删除审计日志失败: {e}")
            return False

    @staticmethod
    def clear_all() -> bool:
        """清空所有审计日志"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("DELETE FROM audit_logs")
                return True
        except Exception as e:
            logger.error(f"清空审计日志失败: {e}")
            return False


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
    def from_row(row) -> Optional['Message']:
        """从数据库行创建对象"""
        if not row:
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

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "recipient_id": self.recipient_id,
            "title": self.title,
            "content": self.content,
            "is_read": self.is_read,
            "created_at": self.created_at
        }

    @staticmethod
    def create(
        sender_id: Optional[int],
        sender_name: str,
        recipient_id: int,
        title: str,
        content: str
    ) -> Optional['Message']:
        """创建新消息"""
        message_id = None
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO messages (sender_id, sender_name, recipient_id, title, content)
                    VALUES (?, ?, ?, ?, ?)
                """, (sender_id, sender_name, recipient_id, title, content))
                message_id = cursor.lastrowid
        except Exception as e:
            logger.error(f"创建消息失败: {e}")

        if message_id:
            return Message.get_by_id(message_id)
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
        """获取指定收件人的消息"""
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
            logger.error(f"获取用户消息失败: {e}")
            return []

    @staticmethod
    def get_by_sender(sender_id: int, limit: int = 50, offset: int = 0) -> List['Message']:
        """获取指定发件人的消息"""
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
            logger.error(f"获取已发送消息失败: {e}")
            return []

    @staticmethod
    def count_by_recipient(recipient_id: int) -> int:
        """获取收件人的消息总数"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM messages WHERE recipient_id = ?", (recipient_id,))
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"统计收件人消息失败: {e}")
            return 0

    @staticmethod
    def count_by_sender(sender_id: int) -> int:
        """获取发件人的消息总数"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM messages WHERE sender_id = ?", (sender_id,))
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"统计发件人消息失败: {e}")
            return 0

    @staticmethod
    def count_unread(recipient_id: int) -> int:
        """获取未读消息数量"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as count FROM messages WHERE recipient_id = ? AND is_read = 0", (recipient_id,))
                row = cursor.fetchone()
                return row['count'] if row else 0
        except Exception as e:
            logger.error(f"统计未读消息失败: {e}")
            return 0

    @staticmethod
    def update_read_status(message_id: int, is_read: bool) -> bool:
        """更新已读状态"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("UPDATE messages SET is_read = ? WHERE id = ?", (1 if is_read else 0, message_id))
                return True
        except Exception as e:
            logger.error(f"更新消息状态失败: {e}")
            return False

    @staticmethod
    def delete_by_id(message_id: int) -> bool:
        """删除单条消息"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("DELETE FROM messages WHERE id = ?", (message_id,))
                return True
        except Exception as e:
            logger.error(f"删除消息失败: {e}")
            return False

    @staticmethod
    def delete_by_ids(message_ids: List[int]) -> int:
        """批量删除消息"""
        if not message_ids:
            return 0
        try:
            placeholders = ','.join(['?'] * len(message_ids))
            query = f"DELETE FROM messages WHERE id IN ({placeholders})"
            with db.get_cursor() as cursor:
                cursor.execute(query, tuple(message_ids))
                return cursor.rowcount
        except Exception as e:
            logger.error(f"批量删除消息失败: {e}")
            return 0
