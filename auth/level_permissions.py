#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 Level 的权限控制依赖项
"""

from typing import Callable
from fastapi import Depends, HTTPException, status
from database.models import User
from auth.dependencies import get_current_active_user


def require_level(min_level: int) -> Callable:
    """
    要求最低用户等级的依赖项工厂
    
    Args:
        min_level: 最低等级要求 (1-10)
    
    Returns:
        依赖项函数
    
    Usage:
        @app.post("/api/advanced-feature")
        async def advanced_feature(
            user: User = Depends(require_level(5))
        ):
            # 只有等级 >= 5 的用户才能访问
            pass
    """
    async def level_checker(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要等级 {min_level} 或更高,当前等级: {current_user.level}"
            )
        return current_user
    
    return level_checker


# 预定义的常用等级依赖项
async def require_level_1(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """要求等级 >= 1 (所有用户)"""
    return current_user


async def require_level_3(
    current_user: User = Depends(require_level(3))
) -> User:
    """要求等级 >= 3"""
    return current_user


async def require_level_5(
    current_user: User = Depends(require_level(5))
) -> User:
    """要求等级 >= 5 (中级用户)"""
    return current_user


async def require_level_7(
    current_user: User = Depends(require_level(7))
) -> User:
    """要求等级 >= 7 (高级用户)"""
    return current_user


async def require_level_10(
    current_user: User = Depends(require_level(10))
) -> User:
    """要求等级 >= 10 (最高等级)"""
    return current_user
