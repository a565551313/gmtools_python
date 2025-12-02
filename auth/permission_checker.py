#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限检查逻辑
"""

from fastapi import Depends, HTTPException, status
from database.models import User
from database.permissions import LevelPermission
from auth.dependencies import get_current_active_user
import logging

logger = logging.getLogger(__name__)


def has_permission(user: User, permission_code: str) -> bool:
    """
    检查用户是否有指定权限
    
    Args:
        user: 用户对象
        permission_code: 权限代码
        
    Returns:
        bool: 是否有权限
    """
    # 超级管理员拥有所有权限
    if user.role == "super_admin":
        return True
    
    # Level 10 用户拥有所有权限
    if user.level >= 10:
        return True
        
    # 检查 Level 权限
    return LevelPermission.has_permission(user.level, permission_code)


def require_permission(permission_code: str):
    """
    权限检查依赖工厂
    
    Usage:
        @app.post("/api/gift")
        async def gift_endpoint(
            user: User = Depends(require_permission("gift.send"))
        ):
            ...
    """
    async def permission_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not has_permission(current_user, permission_code):
            logger.warning(f"用户 {current_user.username} (Level {current_user.level}) 尝试访问 {permission_code} 被拒绝")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足: 需要 {permission_code}"
            )
        return current_user
        
    return permission_checker
