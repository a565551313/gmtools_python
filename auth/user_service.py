#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证服务
"""

from typing import Optional, Tuple
from datetime import timedelta
from database.models import User, AuditLog
from auth import AuthUtils
import logging

logger = logging.getLogger(__name__)


class UserAuthService:
    """用户认证服务"""
    
    @staticmethod
    def register(
        username: str,
        email: str,
        password: str,
        level: int = 1,
        role: str = "user"
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        注册新用户
        返回: (成功标志, 用户对象, 错误消息)
        """
        # 验证用户名是否已存在
        if User.get_by_username(username):
            return False, None, "用户名已存在"
        
        # 验证邮箱是否已存在
        if User.get_by_email(email):
            return False, None, "邮箱已被注册"
        
        # 验证密码强度
        if len(password) < 6:
            return False, None, "密码长度至少为 6 位"
        
        # 哈希密码
        password_hash = AuthUtils.hash_password(password)
        
        # 创建用户
        user = User.create(
            username=username,
            email=email,
            password_hash=password_hash,
            level=level,
            role=role
        )
        
        if user:
            # 记录审计日志
            AuditLog.create(
                user_id=user.id,
                action="USER_REGISTER",
                resource="users",
                details=f"用户注册: {username}"
            )
            return True, user, None
        else:
            return False, None, "创建用户失败"
    
    @staticmethod
    def login(username: str, password: str) -> Tuple[bool, Optional[str], Optional[User], Optional[str]]:
        """
        用户登录
        返回: (成功标志, JWT Token, 用户对象, 错误消息)
        """
        # 获取用户
        user = User.get_by_username(username)
        
        if not user:
            return False, None, None, "用户名或密码错误"
        
        # 检查用户是否激活
        if not user.is_active:
            return False, None, None, "账号已被禁用"
        
        # 验证密码
        if not AuthUtils.verify_password(password, user.password_hash):
            return False, None, None, "用户名或密码错误"
        
        # 生成 JWT Token
        token_data = {
            "sub": user.username,
            "user_id": user.id,
            "role": user.role
        }
        access_token = AuthUtils.create_access_token(token_data)
        
        # 更新最后登录时间
        user.update_last_login()
        
        # 注意：审计日志在路由层记录（包含 IP 地址）
        
        return True, access_token, user, None
    
    @staticmethod
    def verify_token(token: str) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        验证 Token
        返回: (成功标志, 用户对象, 错误消息)
        """
        payload = AuthUtils.verify_token(token)
        
        if not payload:
            return False, None, "Token 无效或已过期"
        
        username = payload.get("sub")
        if not username:
            return False, None, "Token 格式错误"
        
        user = User.get_by_username(username)
        if not user:
            return False, None, "用户不存在"
        
        if not user.is_active:
            return False, None, "账号已被禁用"
        
        return True, user, None
    
    @staticmethod
    def change_password(
        user_id: int,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        修改密码
        返回: (成功标志, 错误消息)
        """
        user = User.get_by_id(user_id)
        
        if not user:
            return False, "用户不存在"
        
        # 验证旧密码
        if not AuthUtils.verify_password(old_password, user.password_hash):
            return False, "原密码错误"
        
        # 验证新密码强度
        if len(new_password) < 6:
            return False, "新密码长度至少为 6 位"
        
        # 更新密码
        new_password_hash = AuthUtils.hash_password(new_password)
        if user.update_password(new_password_hash):
            # 记录审计日志
            AuditLog.create(
                user_id=user.id,
                action="PASSWORD_CHANGE",
                resource="users",
                details=f"用户修改密码: {user.username}"
            )
            return True, None
        else:
            return False, "密码更新失败"
    
    @staticmethod
    def reset_password(user_id: int, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        重置密码（管理员操作）
        返回: (成功标志, 错误消息)
        """
        user = User.get_by_id(user_id)
        
        if not user:
            return False, "用户不存在"
        
        # 验证新密码强度
        if len(new_password) < 6:
            return False, "新密码长度至少为 6 位"
        
        # 更新密码
        new_password_hash = AuthUtils.hash_password(new_password)
        if user.update_password(new_password_hash):
            # 记录审计日志
            AuditLog.create(
                user_id=user.id,
                action="PASSWORD_RESET",
                resource="users",
                details=f"管理员重置密码: {user.username}"
            )
            return True, None
        else:
            return False, "密码重置失败"
