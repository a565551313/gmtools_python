#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
活动管理API路由
使用FastAPI提供大转盘、抽奖券等活动的创建、参与和管理
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from database.activity_models import ActivityManager, Activity, ActivityReward
from auth.dependencies import get_current_active_user, get_current_admin_user
from database.models import User as AuthUser
import json
import logging

logger = logging.getLogger(__name__)

# 创建活动管理器
activity_manager = ActivityManager()

# 创建路由
activity_router = APIRouter(prefix="/api/activity", tags=["activity"])

# 请求模型
class ActivityCreateRequest(BaseModel):
    name: str
    type: str
    description: Optional[str] = ""
    game_id_required: bool = True
    max_participations: int = 0
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    config: Dict[str, Any] = {}

class ActivityUpdateRequest(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    description: Optional[str] = None
    game_id_required: Optional[bool] = None
    max_participations: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class RewardCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    type: str = "item"
    value: Dict[str, Any] = {}
    probability: float
    total_quantity: int
    icon: Optional[str] = ""
    order_index: int = 0

class ParticipateRequest(BaseModel):
    game_id: str

# 活动路由
@activity_router.post("/create")
async def create_activity(
    request: ActivityCreateRequest,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """创建活动"""
    try:
        # 创建活动对象
        activity = Activity(
            name=request.name,
            type=request.type,
            description=request.description,
            game_id_required=request.game_id_required,
            max_participations=request.max_participations,
            start_time=request.start_time,
            end_time=request.end_time,
            config=json.dumps(request.config)
        )
        
        # 创建活动
        activity_id = activity_manager.create_activity(activity)
        
        return {
            "success": True,
            "message": "活动创建成功",
            "data": {"activity_id": activity_id}
        }
        
    except Exception as e:
        logger.error(f"创建活动失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")

@activity_router.get("/list")
async def get_activities(
    limit: int = 100,
    offset: int = 0,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """获取活动列表"""
    try:
        activities = activity_manager.get_activities(limit, offset)
        
        activities_data = []
        for activity in activities:
            activity_dict = activity.to_dict()
            
            # 解析配置
            if activity.config:
                activity_dict['config_parsed'] = json.loads(activity.config)
            else:
                activity_dict['config_parsed'] = {}
            
            activities_data.append(activity_dict)
        
        return {
            "success": True,
            "data": activities_data,
            "total": len(activities_data)
        }
        
    except Exception as e:
        logger.error(f"获取活动列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")

@activity_router.get("/{activity_id}")
async def get_activity(
    activity_id: int,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """获取单个活动详情"""
    try:
        activity = activity_manager.get_activity(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 获取奖项
        rewards = activity_manager.get_rewards(activity_id)
        rewards_data = [reward.to_dict() for reward in rewards]
        
        # 获取统计数据
        stats = activity_manager.get_statistics(activity_id)
        
        activity_dict = activity.to_dict()
        if activity.config:
            activity_dict['config_parsed'] = json.loads(activity.config)
        else:
            activity_dict['config_parsed'] = {}
        
        return {
            "success": True,
            "data": {
                "activity": activity_dict,
                "rewards": rewards_data,
                "statistics": stats
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取活动详情失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")

@activity_router.put("/{activity_id}")
async def update_activity(
    activity_id: int,
    request: ActivityUpdateRequest,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """更新活动"""
    try:
        # 检查活动是否存在
        existing_activity = activity_manager.get_activity(activity_id)
        if not existing_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 创建更新对象
        activity = Activity(
            name=request.name if request.name is not None else existing_activity.name,
            type=request.type if request.type is not None else existing_activity.type,
            description=request.description if request.description is not None else existing_activity.description,
            game_id_required=request.game_id_required if request.game_id_required is not None else existing_activity.game_id_required,
            max_participations=request.max_participations if request.max_participations is not None else existing_activity.max_participations,
            start_time=request.start_time if request.start_time is not None else existing_activity.start_time,
            end_time=request.end_time if request.end_time is not None else existing_activity.end_time,
            config=json.dumps(request.config if request.config is not None else json.loads(existing_activity.config) if existing_activity.config else {})
        )
        
        # 更新活动
        success = activity_manager.update_activity(activity_id, activity)
        if not success:
            raise HTTPException(status_code=500, detail="更新失败")
        
        return {
            "success": True,
            "message": "活动更新成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新活动失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")

# ... (omitted)

@activity_router.post("/{activity_id}/add-reward")
async def add_reward(
    activity_id: int,
    request: RewardCreateRequest,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """添加活动奖项"""
    try:
        # 检查活动是否存在
        existing_activity = activity_manager.get_activity(activity_id)
        if not existing_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 检查概率总和
        rewards = activity_manager.get_rewards(activity_id)
        total_probability = sum(r.probability for r in rewards) + request.probability
        if total_probability > 100:
            raise HTTPException(
                status_code=400, 
                detail=f"总概率不能超过100%，当前总和: {total_probability}%"
            )
        
        # 创建奖项对象
        reward = ActivityReward(
            activity_id=activity_id,
            name=request.name,
            description=request.description,
            type=request.type,
            value=json.dumps(request.value),
            probability=request.probability,
            total_quantity=request.total_quantity,
            remaining_quantity=request.total_quantity,
            icon=request.icon,
            order_index=request.order_index
        )
        
        # 添加奖项
        reward_id = activity_manager.add_reward(reward)
        
        return {
            "success": True,
            "message": "奖项添加成功",
            "data": {"reward_id": reward_id}
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加奖项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"添加失败: {str(e)}")

@activity_router.put("/{activity_id}/rewards/{reward_id}")
async def update_reward(
    activity_id: int,
    reward_id: int,
    request: RewardCreateRequest,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """更新活动奖项"""
    try:
        # 检查活动是否存在
        existing_activity = activity_manager.get_activity(activity_id)
        if not existing_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
            
        # 检查概率总和 (排除当前奖项)
        rewards = activity_manager.get_rewards(activity_id)
        current_prob_sum = sum(r.probability for r in rewards if r.id != reward_id)
        if current_prob_sum + request.probability > 100:
             raise HTTPException(
                status_code=400, 
                detail=f"总概率不能超过100%，当前其他奖项总和: {current_prob_sum}%"
            )

        # 创建更新对象 (保持原有remaining_quantity，或者根据total_quantity变化调整？)
        # 简单起见，我们先获取原奖项来保留 remaining_quantity
        # 但 model update_reward 直接覆盖。
        # 我们应该先获取原奖项。
        
        # 这里简化处理，假设 remaining_quantity 不变，或者由前端传递？
        # RewardCreateRequest 没有 remaining_quantity。
        # 我们需要获取原奖项。
        
        # 由于 ActivityManager 没有 get_reward(reward_id) 方法（只有 get_rewards(activity_id)），
        # 我们只能遍历查找。
        target_reward = next((r for r in rewards if r.id == reward_id), None)
        if not target_reward:
             raise HTTPException(status_code=404, detail="奖项不存在")

        reward = ActivityReward(
            activity_id=activity_id,
            name=request.name,
            description=request.description,
            type=request.type,
            value=json.dumps(request.value),
            probability=request.probability,
            total_quantity=request.total_quantity,
            remaining_quantity=target_reward.remaining_quantity, # 保持不变
            icon=request.icon,
            order_index=request.order_index
        )
        
        success = activity_manager.update_reward(reward_id, reward)
        if not success:
            raise HTTPException(status_code=500, detail="更新失败")
            
        return {
            "success": True,
            "message": "奖项更新成功"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新奖项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")

@activity_router.delete("/{activity_id}/rewards/{reward_id}")
async def delete_reward(
    activity_id: int,
    reward_id: int,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """删除活动奖项"""
    try:
        # 检查活动是否存在
        existing_activity = activity_manager.get_activity(activity_id)
        if not existing_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 删除奖项
        success = activity_manager.delete_reward(reward_id)
        if not success:
            raise HTTPException(status_code=400, detail="删除失败")
        
        return {
            "success": True,
            "message": "奖项删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除奖项失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@activity_router.post("/{activity_id}/participate")
async def participate_in_activity(
    activity_id: int,
    request: ParticipateRequest
):
    """参与活动（无需登录）"""
    try:
        # 检查活动是否存在
        activity = activity_manager.get_activity(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 参与活动
        result = activity_manager.participate(activity_id, request.game_id)
        
        if result["success"]:
            return {
                "success": True,
                "message": "参与成功",
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result["message"])
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"参与活动失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"参与失败: {str(e)}")

@activity_router.post("/{activity_id}/history")
async def get_user_history(
    activity_id: int,
    request: ParticipateRequest
):
    """获取用户参与记录（无需登录）"""
    try:
        # 检查活动是否存在
        activity = activity_manager.get_activity(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 获取记录
        history = activity_manager.get_user_participations(activity_id, request.game_id)
        
        return {
            "success": True,
            "data": [item.to_dict() for item in history]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取参与记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取记录失败: {str(e)}")

@activity_router.get("/{activity_id}/public-info")
async def get_activity_public_info(activity_id: int):
    """获取活动公开信息（无需登录）"""
    try:
        activity = activity_manager.get_activity(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 获取奖项
        rewards = activity_manager.get_rewards(activity_id)
        rewards_data = [reward.to_dict() for reward in rewards]
        
        # 获取统计数据（仅用于显示剩余名额）
        stats = activity_manager.get_statistics(activity_id)
        
        activity_dict = activity.to_dict()
        if activity.config:
            activity_dict['config_parsed'] = json.loads(activity.config)
        else:
            activity_dict['config_parsed'] = {}
        
        return {
            "success": True,
            "data": {
                "activity": activity_dict,
                "rewards": rewards_data,
                "statistics": stats
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取活动公开信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取失败: {str(e)}")

@activity_router.delete("/{activity_id}")
async def delete_activity(
    activity_id: int,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """删除活动"""
    try:
        # 检查活动是否存在
        existing_activity = activity_manager.get_activity(activity_id)
        if not existing_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 删除活动
        success = activity_manager.delete_activity(activity_id)
        if not success:
            raise HTTPException(status_code=500, detail="删除失败")
        
        return {
            "success": True,
            "message": "活动删除成功"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除活动失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")

@activity_router.get("/{activity_id}/statistics")
async def get_activity_statistics(
    activity_id: int,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """获取活动统计"""
    try:
        # 检查活动是否存在
        existing_activity = activity_manager.get_activity(activity_id)
        if not existing_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
        
        # 获取统计数据
        stats = activity_manager.get_statistics(activity_id)
        
        return {
            "success": True,
            "data": stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取活动统计失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")

@activity_router.get("/{activity_id}/participations")
async def get_activity_participations(
    activity_id: int,
    limit: int = 100,
    offset: int = 0,
    game_id: Optional[str] = None,
    reward_name: Optional[str] = None,
    status: Optional[int] = None,
    activity_type: Optional[str] = None,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """获取活动参与记录（管理员）"""
    try:
        # 检查活动是否存在
        existing_activity = activity_manager.get_activity(activity_id)
        if not existing_activity:
            raise HTTPException(status_code=404, detail="活动不存在")
            
        participations, total = activity_manager.get_participations(
            activity_id, limit, offset, game_id, reward_name, status, activity_type
        )
        
        # participations 已经是字典列表了，不需要再调用 to_dict()
        
        return {
            "success": True,
            "data": participations,
            "total": total
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取参与记录失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取记录失败: {str(e)}")

@activity_router.post("/{activity_id}/participations/{record_id}/resend")
async def resend_reward(
    activity_id: int,
    record_id: int,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """补发奖励"""
    try:
        # 调用补发逻辑
        success, message = activity_manager.resend_reward(record_id)
        
        if success:
            return {
                "success": True,
                "message": message
            }
        else:
            raise HTTPException(status_code=500, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"补发奖励失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"补发失败: {str(e)}")