#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限管理 API 路由
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from database.permissions import Permission, LevelPermission
from database.models import User
from auth.dependencies import get_current_admin_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["权限管理"])


# ==================== Pydantic 模型 ====================

class PermissionResponse(BaseModel):
    """权限响应"""
    id: int
    code: str
    name: str
    category: str
    description: str = ""


class LevelPermissionsUpdateRequest(BaseModel):
    """Level 权限更新请求"""
    permission_codes: List[str] = Field(..., description="权限代码列表")
    
    class Config:
        json_schema_extra = {
            "example": {
                "permission_codes": ["account.recharge", "gift.send", "pet.give"]
            }
        }


# ==================== API 路由 ====================

@router.get("/permissions", response_model=dict)
async def get_all_permissions(
    admin_user: User = Depends(get_current_admin_user)
):
    """
    获取所有权限列表（按分类分组）
    
    需要管理员权限
    """
    permissions_by_category = Permission.get_by_category()
    
    result = {}
    for category, perms in permissions_by_category.items():
        result[category] = [
            {
                "id": p.id,
                "code": p.code,
                "name": p.name,
                "description": p.description
            }
            for p in perms
        ]
    
    return {
        "status": "success",
        "permissions": result
    }


@router.get("/levels/{level}/permissions", response_model=dict)
async def get_level_permissions(
    level: int,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    获取指定 Level 的权限列表
    
    - **level**: Level (1-10)
    """
    if level < 1 or level > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level 必须在 1-10 之间"
        )
    
    permission_codes = LevelPermission.get_level_permissions(level)
    permission_ids = LevelPermission.get_level_permission_ids(level)
    
    # 获取权限详情
    all_permissions = Permission.get_all()
    permission_details = []
    for perm in all_permissions:
        if perm.id in permission_ids or perm.code in permission_codes:
            permission_details.append({
                "id": perm.id,
                "code": perm.code,
                "name": perm.name,
                "category": perm.category
            })
    
    return {
        "status": "success",
        "level": level,
        "permission_codes": permission_codes,
        "permissions": permission_details,
        "count": len(permission_codes)
    }


@router.put("/levels/{level}/permissions", response_model=dict)
async def update_level_permissions(
    level: int,
    data: LevelPermissionsUpdateRequest,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    更新指定 Level 的权限
    
    - **level**: Level (1-10)
    - **permission_codes**: 权限代码列表
    """
    if level < 1 or level > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Level 必须在 1-10 之间"
        )
    
    # 验证所有权限代码是否存在
    all_permissions = Permission.get_all()
    valid_codes = {p.code for p in all_permissions}
    
    # 支持通配符
    for code in data.permission_codes:
        if code not in ["*"] and not code.endswith(".*") and code not in valid_codes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的权限代码: {code}"
            )
    
    # 更新权限
    success = LevelPermission.set_level_permissions(level, data.permission_codes)
    
    if success:
        logger.info(f"管理员 {admin_user.username} 更新了 Level {level} 的权限")
        return {
            "status": "success",
            "message": f"Level {level} 权限更新成功",
            "level": level,
            "permission_count": len(data.permission_codes)
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="权限更新失败"
        )
