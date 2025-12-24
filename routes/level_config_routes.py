#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等级配置管理 API 路由
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from database.level_config import LevelConfig
from database.models import User
from auth.dependencies import get_current_super_admin
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["等级配置管理"])


# ==================== Pydantic 模型 ====================

class LevelConfigResponse(BaseModel):
    """等级配置响应"""
    level_value: int
    display_name: str
    description: str = ""
    sort_order: int
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    # 额外统计信息
    user_count: Optional[int] = None
    activation_code_total: Optional[int] = None
    activation_code_unused: Optional[int] = None


class LevelConfigCreateRequest(BaseModel):
    """创建等级配置请求"""
    level_value: int = Field(..., ge=1, le=100, description="等级值（1-100）")
    display_name: str = Field(..., min_length=1, max_length=50, description="显示名称")
    description: str = Field(default="", max_length=200, description="等级描述")
    sort_order: Optional[int] = Field(default=None, description="排序顺序")
    
    class Config:
        json_schema_extra = {
            "example": {
                "level_value": 11,
                "display_name": "钻石",
                "description": "钻石等级用户",
                "sort_order": 11
            }
        }


class LevelConfigUpdateRequest(BaseModel):
    """更新等级配置请求"""
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=200)
    sort_order: Optional[int] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    
    class Config:
        json_schema_extra = {
            "example": {
                "display_name": "青铜一",
                "description": "青铜段位第一级"
            }
        }


# ==================== API 路由 ====================

@router.get("/level-configs", response_model=dict)
async def get_all_level_configs(
    include_inactive: bool = False,
    include_stats: bool = True,
    super_admin: User = Depends(get_current_super_admin)
):
    """
    获取所有等级配置列表
    
    - **include_inactive**: 是否包含已停用的等级
    - **include_stats**: 是否包含使用统计
    """
    configs = LevelConfig.get_all(active_only=not include_inactive)
    
    result = []
    for config in configs:
        config_dict = config.to_dict()
        
        # 添加使用统计
        if include_stats:
            stats = LevelConfig.get_usage_stats(config.level_value)
            config_dict.update(stats)
        
        result.append(config_dict)
    
    return {
        "status": "success",
        "data": result,
        "total": len(result)
    }


@router.get("/level-configs/{level_value}", response_model=dict)
async def get_level_config(
    level_value: int,
    super_admin: User = Depends(get_current_super_admin)
):
    """
    获取指定等级的配置详情
    
    - **level_value**: 等级值
    """
    config = LevelConfig.get_by_level(level_value)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"等级 {level_value} 不存在"
        )
    
    config_dict = config.to_dict()
    
    # 添加使用统计
    stats = LevelConfig.get_usage_stats(level_value)
    config_dict.update(stats)
    
    return {
        "status": "success",
        "data": config_dict
    }


@router.post("/level-configs", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_level_config(
    data: LevelConfigCreateRequest,
    super_admin: User = Depends(get_current_super_admin)
):
    """
    创建新等级配置
    
    - **level_value**: 等级值（1-100，必须唯一）
    - **display_name**: 显示名称
    - **description**: 等级描述（可选）
    - **sort_order**: 排序顺序（可选，默认使用level_value）
    """
    # 检查等级值是否已存在
    existing = LevelConfig.get_by_level(data.level_value)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"等级 {data.level_value} 已存在"
        )
    
    # 创建等级配置
    config = LevelConfig.create(
        level_value=data.level_value,
        display_name=data.display_name,
        description=data.description,
        sort_order=data.sort_order
    )
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建等级配置失败"
        )
    
    logger.info(f"超级管理员 {super_admin.username} 创建了新等级: Level {data.level_value} - {data.display_name}")
    
    return {
        "status": "success",
        "message": f"等级 {data.level_value} 创建成功",
        "data": config.to_dict()
    }


@router.put("/level-configs/{level_value}", response_model=dict)
async def update_level_config(
    level_value: int,
    data: LevelConfigUpdateRequest,
    super_admin: User = Depends(get_current_super_admin)
):
    """
    更新等级配置
    
    - **level_value**: 等级值
    - **display_name**: 新的显示名称（可选）
    - **description**: 新的描述（可选）
    - **sort_order**: 新的排序顺序（可选）
    - **is_active**: 是否启用（可选）
    """
    config = LevelConfig.get_by_level(level_value)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"等级 {level_value} 不存在"
        )
    
    # 更新字段
    if data.display_name is not None:
        config.display_name = data.display_name
    if data.description is not None:
        config.description = data.description
    if data.sort_order is not None:
        config.sort_order = data.sort_order
    if data.is_active is not None:
        config.is_active = data.is_active
    
    # 保存更新
    if not config.update():
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新等级配置失败"
        )
    
    logger.info(f"超级管理员 {super_admin.username} 更新了等级配置: Level {level_value}")
    
    return {
        "status": "success",
        "message": f"等级 {level_value} 更新成功",
        "data": config.to_dict()
    }


@router.delete("/level-configs/{level_value}", response_model=dict)
async def delete_level_config(
    level_value: int,
    force: bool = False,
    super_admin: User = Depends(get_current_super_admin)
):
    """
    删除等级配置（软删除）
    
    - **level_value**: 等级值
    - **force**: 是否强制删除（默认false，将检查是否有用户使用）
    
    注意：这是软删除，等级配置会被标记为不活跃，但不会从数据库中物理删除
    """
    config = LevelConfig.get_by_level(level_value)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"等级 {level_value} 不存在"
        )
    
    # 检查是否可以删除
    if not force:
        can_delete, reason = LevelConfig.can_delete(level_value)
        if not can_delete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无法删除等级: {reason}。如需强制删除，请设置force=true"
            )
    
    # 执行软删除
    if not LevelConfig.delete(level_value):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除等级配置失败"
        )
    
    logger.info(f"超级管理员 {super_admin.username} 删除了等级配置: Level {level_value} (force={force})")
    
    return {
        "status": "success",
        "message": f"等级 {level_value} 已删除"
    }


@router.get("/level-configs/{level_value}/can-delete", response_model=dict)
async def check_can_delete_level(
    level_value: int,
    super_admin: User = Depends(get_current_super_admin)
):
    """
    检查等级是否可以删除
    
    - **level_value**: 等级值
    
    返回是否可以删除及原因
    """
    can_delete, reason = LevelConfig.can_delete(level_value)
    
    # 获取使用统计
    stats = LevelConfig.get_usage_stats(level_value)
    
    return {
        "status": "success",
        "data": {
            "can_delete": can_delete,
            "reason": reason,
            "usage_stats": stats
        }
    }
