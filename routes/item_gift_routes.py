#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道具赠送系统 API 路由

提供道具配置、等级限制、发送操作的 REST API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List
from auth.dependencies import get_current_user, get_current_admin_user, get_current_super_admin
from database.models import User
from database.item_gift import ItemConfig, ItemLevelLimit, ItemGiftLog
from services.item_gift_service import ItemGiftService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


# ==================== 请求/响应模型 ====================

class ItemConfigCreateRequest(BaseModel):
    """创建道具配置请求"""
    item_name: str = Field(..., description="道具名称（唯一标识）")
    display_name: Optional[str] = Field(None, description="显示名称（可选，默认同道具名）")
    description: Optional[str] = Field("", description="道具描述")
    icon_url: Optional[str] = Field(None, description="图标URL")


class ItemConfigUpdateRequest(BaseModel):
    """更新道具配置请求"""
    item_name: Optional[str] = None  # 支持重命名
    display_name: Optional[str] = None
    description: Optional[str] = None
    icon_url: Optional[str] = None
    is_active: Optional[bool] = None


class ItemLevelLimitCreateRequest(BaseModel):
    """创建等级限制请求"""
    item_name: str
    user_level: int = Field(..., ge=1, le=100)
    min_quantity: int = Field(1, ge=1)
    max_quantity: int = Field(99, ge=1)
    reset_period_hours: int = Field(24, ge=1)
    period_total_limit: int = Field(999, ge=1)


class ItemLevelLimitBatchCreateRequest(BaseModel):
    """批量创建等级限制请求"""
    items: List[str]
    user_levels: List[int] = Field(..., description="适用等级列表")
    min_quantity: int = Field(1, ge=1)
    max_quantity: int = Field(99, ge=1)
    reset_period_hours: int = Field(24, ge=1)
    period_total_limit: int = Field(999, ge=1)


class ItemLevelLimitUpdateRequest(BaseModel):
    """更新等级限制请求"""
    item_name: Optional[str] = None
    user_level: Optional[int] = None
    min_quantity: Optional[int] = Field(None, ge=1)
    max_quantity: Optional[int] = Field(None, ge=1)
    reset_period_hours: Optional[int] = Field(None, ge=1)
    period_total_limit: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None


class CheckGiftRequest(BaseModel):
    """检查发送请求"""
    item_name: str
    quantity: int = Field(..., ge=1)


class SendGiftRequest(BaseModel):
    """发送道具请求"""
    recipient_username: str
    item_name: str
    quantity: int = Field(..., ge=1)


# ==================== 道具配置管理 API（超级管理员）====================

@router.get("/item-configs", response_model=dict)
async def get_item_configs(
    super_admin: User = Depends(get_current_super_admin)
):
    """获取所有道具配置"""
    try:
        configs = ItemConfig.get_all()
        return {
            "status": "success",
            "data": [config.to_dict() for config in configs]
        }
    except Exception as e:
        logger.error(f"获取道具配置失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item-configs/{item_name}", response_model=dict)
async def get_item_config(
    item_name: str,
    super_admin: User = Depends(get_current_super_admin)
):
    """获取单个道具配置"""
    config = ItemConfig.get_by_name(item_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"道具 '{item_name}' 不存在")
    
    return {
        "status": "success",
        "data": config.to_dict()
    }


@router.post("/item-configs", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_item_config(
    data: ItemConfigCreateRequest,
    super_admin: User = Depends(get_current_super_admin)
):
    """创建道具配置"""
    # 检查是否已存在
    existing = ItemConfig.get_by_name(data.item_name)
    if existing:
        raise HTTPException(status_code=400, detail=f"道具 '{data.item_name}' 已存在")
    
    config = ItemConfig.create(
        item_name=data.item_name,
        display_name=data.display_name,
        description=data.description,
        icon_url=data.icon_url
    )
    
    if not config:
        raise HTTPException(status_code=500, detail="创建道具配置失败")
    
    logger.info(f"超级管理员 {super_admin.username} 创建道具配置: {data.item_name}")
    
    return {
        "status": "success",
        "message": f"道具 '{data.item_name}' 创建成功",
        "data": config.to_dict()
    }


@router.put("/item-configs/{item_name}", response_model=dict)
async def update_item_config(
    item_name: str,
    data: ItemConfigUpdateRequest,
    super_admin: User = Depends(get_current_super_admin)
):
    """更新道具配置"""
    config = ItemConfig.get_by_name(item_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"道具 '{item_name}' 不存在")
    
    # 如果请求包含新的 item_name 且不同于当前名称，执行重命名
    if data.item_name and data.item_name != item_name:
        # 检查新名称是否已被占用
        if ItemConfig.get_by_name(data.item_name):
            raise HTTPException(status_code=400, detail=f"道具名称 '{data.item_name}' 已存在")
            
        if not config.rename(data.item_name):
            raise HTTPException(status_code=500, detail="重命名失败")
            
        # 更新 item_name 引用以便后续更新其他字段
        item_name = data.item_name
    
    success = config.update(
        display_name=data.display_name,
        description=data.description,
        icon_url=data.icon_url,
        is_active=data.is_active
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="更新道具配置失败")
    
    logger.info(f"超级管理员 {super_admin.username} 更新道具配置: {item_name}")
    
    # 重新获取更新后的数据
    updated_config = ItemConfig.get_by_name(item_name)
    
    return {
        "status": "success",
        "message": f"道具 '{item_name}' 更新成功",
        "data": updated_config.to_dict() if updated_config else None
    }


@router.delete("/item-configs/{item_name}", response_model=dict)
async def delete_item_config(
    item_name: str,
    super_admin: User = Depends(get_current_super_admin)
):
    """删除道具配置（软删除）"""
    config = ItemConfig.get_by_name(item_name)
    if not config:
        raise HTTPException(status_code=404, detail=f"道具 '{item_name}' 不存在")
    
    success = ItemConfig.delete(item_name)
    if not success:
        raise HTTPException(status_code=500, detail="删除道具配置失败")
    
    logger.info(f"超级管理员 {super_admin.username} 删除道具配置: {item_name}")
    
    return {
        "status": "success",
        "message": f"道具 '{item_name}' 已删除"
    }


# ==================== 等级限制管理 API（超级管理员）====================

@router.get("/item-level-limits", response_model=dict)
async def get_all_limits(
    super_admin: User = Depends(get_current_super_admin)
):
    """获取所有等级限制"""
    try:
        limits = ItemLevelLimit.get_all()
        return {
            "status": "success",
            "data": [limit.to_dict() for limit in limits]
        }
    except Exception as e:
        logger.error(f"获取等级限制失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/item-level-limits/level/{level}", response_model=dict)
async def get_limits_by_level(
    level: int,
    super_admin: User = Depends(get_current_super_admin)
):
    """获取某等级的所有限制"""
    limits = ItemLevelLimit.get_all_by_level(level)
    return {
        "status": "success",
        "data": [limit.to_dict() for limit in limits]
    }


@router.get("/item-level-limits/item/{item_name}", response_model=dict)
async def get_limits_by_item(
    item_name: str,
    super_admin: User = Depends(get_current_super_admin)
):
    """获取某道具的所有等级限制"""
    limits = ItemLevelLimit.get_all_by_item(item_name)
    return {
        "status": "success",
        "data": [limit.to_dict() for limit in limits]
    }


@router.post("/item-level-limits", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_level_limit(
    data: ItemLevelLimitCreateRequest,
    super_admin: User = Depends(get_current_super_admin)
):
    """创建等级限制"""
    # 检查道具是否存在
    item = ItemConfig.get_by_name(data.item_name)
    if not item:
        raise HTTPException(status_code=404, detail=f"道具 '{data.item_name}' 不存在")
    
    # 检查是否已存在
    existing = ItemLevelLimit.get_limit(data.item_name, data.user_level)
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"道具 '{data.item_name}' Level {data.user_level} 的限制已存在"
        )
    
    limit = ItemLevelLimit.create(
        item_name=data.item_name,
        user_level=data.user_level,
        min_quantity=data.min_quantity,
        max_quantity=data.max_quantity,
        reset_period_hours=data.reset_period_hours,
        period_total_limit=data.period_total_limit
    )
    
    if not limit:
        raise HTTPException(status_code=500, detail="创建等级限制失败")
    
    logger.info(
        f"超级管理员 {super_admin.username} 创建等级限制: "
        f"{data.item_name} - Level {data.user_level}"
    )
    
    return {
        "status": "success",
        "message": f"等级限制创建成功",
        "data": limit.to_dict()
    }


@router.post("/item-level-limits/batch", response_model=dict, status_code=status.HTTP_201_CREATED)
async def batch_create_level_limits(
    data: ItemLevelLimitBatchCreateRequest,
    super_admin: User = Depends(get_current_super_admin)
):
    """批量创建等级限制"""
    limits_data = []
    
    # 双重循环：遍历所有选中的道具和等级
    for item_name in data.items:
        # 检查道具是否存在
        if not ItemConfig.get_by_name(item_name):
            continue
            
        for level in data.user_levels:
            # 检查是否已存在
            if ItemLevelLimit.get_limit(item_name, level):
                continue
                
            limits_data.append({
                'item_name': item_name,
                'user_level': level,
                'min_quantity': data.min_quantity,
                'max_quantity': data.max_quantity,
                'reset_period_hours': data.reset_period_hours,
                'period_total_limit': data.period_total_limit
            })
    
    if not limits_data:
        raise HTTPException(status_code=400, detail="没有有效的限制规则可创建（可能道具不存在或规则已存在）")
        
    success = ItemLevelLimit.batch_create(limits_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="批量创建失败")
        
    logger.info(f"超级管理员 {super_admin.username} 批量创建 {len(limits_data)} 条限制规则")
    
    return {
        "status": "success",
        "message": f"成功创建 {len(limits_data)} 条限制规则"
    }


@router.put("/item-level-limits/{limit_id}", response_model=dict)
async def update_level_limit(
    limit_id: int,
    data: ItemLevelLimitUpdateRequest,
    super_admin: User = Depends(get_current_super_admin)
):
    """更新等级限制"""
    # 简化处理：通过get_all找到对应的limit
    all_limits = ItemLevelLimit.get_all()
    limit = next((l for l in all_limits if l.id == limit_id), None)
    
    if not limit:
        raise HTTPException(status_code=404, detail=f"限制ID {limit_id} 不存在")
    
    # 如果修改了 item_name 或 user_level，需要检查冲突
    if (data.item_name and data.item_name != limit.item_name) or \
       (data.user_level and data.user_level != limit.user_level):
        
        new_item = data.item_name or limit.item_name
        new_level = data.user_level or limit.user_level
        
        existing = ItemLevelLimit.get_limit(new_item, new_level)
        if existing and existing.id != limit_id:
            raise HTTPException(status_code=400, detail=f"目标规则已存在: {new_item} - Level {new_level}")

    success = limit.update(
        min_quantity=data.min_quantity,
        max_quantity=data.max_quantity,
        reset_period_hours=data.reset_period_hours,
        period_total_limit=data.period_total_limit,
        is_active=data.is_active,
        item_name=data.item_name,
        user_level=data.user_level
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="更新等级限制失败")
    
    logger.info(f"超级管理员 {super_admin.username} 更新等级限制 ID: {limit_id}")
    
    # 重新获取
    updated_limit = next((l for l in ItemLevelLimit.get_all() if l.id == limit_id), None)
    
    return {
        "status": "success",
        "message": "等级限制更新成功",
        "data": updated_limit.to_dict() if updated_limit else None
    }


@router.delete("/item-level-limits/{limit_id}", response_model=dict)
async def delete_level_limit(
    limit_id: int,
    super_admin: User = Depends(get_current_super_admin)
):
    """删除等级限制"""
    success = ItemLevelLimit.delete_by_id(limit_id)
    if not success:
        raise HTTPException(status_code=500, detail="删除等级限制失败")
    
    logger.info(f"超级管理员 {super_admin.username} 删除等级限制 ID: {limit_id}")
    
    return {
        "status": "success",
        "message": "等级限制已删除"
    }


# ==================== 权限检查和发送 API（普通用户）====================

@router.post("/items/check-gift", response_model=dict)
async def check_gift(
    data: CheckGiftRequest,
    current_user: User = Depends(get_current_user)
):
    """检查是否可以发送道具"""
    is_admin = current_user.role in ['admin', 'super_admin']
    
    can_send, message = ItemGiftService.check_gift_permission(
        sender_username=current_user.username,
        sender_level=current_user.level,
        item_name=data.item_name,
        quantity=data.quantity,
        is_admin=is_admin
    )
    
    return {
        "status": "success" if can_send else "error",
        "can_send": can_send,
        "message": message
    }


@router.post("/items/send-gift", response_model=dict)
async def send_gift(
    data: SendGiftRequest,
    current_user: User = Depends(get_current_user)
):
    """执行道具发送"""
    is_admin = current_user.role in ['admin', 'super_admin']
    
    success, message = ItemGiftService.send_item_gift(
        sender_username=current_user.username,
        sender_level=current_user.level,
        recipient_username=data.recipient_username,
        item_name=data.item_name,
        quantity=data.quantity,
        is_admin=is_admin
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {
        "status": "success",
        "message": message
    }


@router.get("/items/my-limits", response_model=dict)
async def get_my_limits(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的所有道具限制"""
    limits = ItemGiftService.get_user_limits(current_user.level)
    return {
        "status": "success",
        "data": limits
    }


@router.get("/items/my-usage", response_model=dict)
async def get_my_usage(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户的配额使用情况"""
    usage = ItemGiftService.get_user_usage(current_user.username, current_user.level)
    return {
        "status": "success",
        "data": usage
    }


@router.get("/items/available", response_model=dict)
async def get_available_items(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户可发送的道具列表"""
    items = ItemGiftService.get_available_items(current_user.level)
    return {
        "status": "success",
        "data": items
    }


@router.get("/items/send-history", response_model=dict)
async def get_send_history(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """获取发送历史"""
    logs = ItemGiftLog.get_recent_logs(current_user.username, limit)
    return {
        "status": "success",
        "data": [log.to_dict() for log in logs]
    }
