#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息管理 API 路由
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status, Body
from pydantic import BaseModel, Field
from database.models import Message, User
from auth.dependencies import get_current_active_user, get_current_admin_user

router = APIRouter(prefix="/api", tags=["消息管理"])


class MessageCreateRequest(BaseModel):
    """创建消息请求"""
    recipient_id: Optional[int] = Field(None, description="单个收件人用户ID（用于回复）")
    user_ids: Optional[List[int]] = Field(None, description="收件人用户ID列表（仅管理员可用）")
    title: str = Field(..., min_length=1, max_length=100, description="消息标题")
    content: str = Field(..., min_length=1, description="消息内容")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recipient_id": 1,
                "title": "回复消息",
                "content": "这是一条回复消息"
            }
        }


class MessageUpdateRequest(BaseModel):
    """更新消息请求"""
    is_read: bool = Field(..., description="是否已读")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_read": True
            }
        }


@router.post("/messages", status_code=status.HTTP_201_CREATED)
async def create_messages(
    request: MessageCreateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    创建并发送消息
    - 普通用户：只能发送给单个用户（回复功能）
    - 管理员：可以发送给多个用户
    """
    try:
        created_messages = []
        
        # 验证请求参数
        if not request.recipient_id and not request.user_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="必须提供收件人ID或用户ID列表"
            )
        
        # 处理单个收件人（普通用户回复场景）
        if request.recipient_id:
            # 检查用户是否存在
            recipient = User.get_by_id(request.recipient_id)
            if not recipient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"用户ID {request.recipient_id} 不存在"
                )
            
            # 创建消息
            message = Message.create(
                sender_id=current_user.id,
                sender_name=current_user.username,
                recipient_id=request.recipient_id,
                title=request.title,
                content=request.content
            )
            
            if message:
                created_messages.append(message.to_dict())
                result_message = f"消息已成功发送给用户ID {request.recipient_id}"
        
        # 处理多个收件人（管理员场景）
        elif request.user_ids:
            # 只有管理员可以发送给多个用户
            if current_user.role not in ["admin", "super_admin"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="只有管理员可以发送消息给多个用户"
                )
            
            success_count = 0
            failed_users = []
            
            for user_id in request.user_ids:
                # 检查用户是否存在
                recipient = User.get_by_id(user_id)
                if not recipient:
                    failed_users.append(user_id)
                    continue
                
                # 创建消息
                message = Message.create(
                    sender_id=current_user.id,
                    sender_name=current_user.username,
                    recipient_id=user_id,
                    title=request.title,
                    content=request.content
                )
                
                if message:
                    created_messages.append(message.to_dict())
                    success_count += 1
            
            # 添加成功和失败的统计信息
            result_message = f"消息已成功发送给 {success_count} 位用户"
            if failed_users:
                result_message += f"，{len(failed_users)} 位用户发送失败（用户ID不存在：{', '.join(map(str, failed_users))}）"
        
        return {
            "status": "success",
            "message": result_message,
            "data": created_messages
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送消息失败: {str(e)}"
        )


@router.get("/messages")
async def get_messages(
    type: str = "inbox",  # inbox 或 sent
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的消息
    """
    try:
        if type == "inbox":
            # 获取收件箱消息
            messages = Message.get_by_recipient(current_user.id, limit=limit, offset=offset)
        elif type == "sent":
            # 获取已发送消息
            messages = Message.get_by_sender(current_user.id, limit=limit, offset=offset)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="type 参数只能是 'inbox' 或 'sent'"
            )
        
        # 获取真实的总数
        if type == "inbox":
            total = Message.count_by_recipient(current_user.id)
        elif type == "sent":
            total = Message.count_by_sender(current_user.id)
        else:
            total = 0
        
        return {
            "status": "success",
            "data": [message.to_dict() for message in messages],
            "total": total,
            "unread_count": Message.count_unread(current_user.id) if type == "inbox" else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取消息失败: {str(e)}"
        )


@router.get("/messages/unread-count")
async def get_unread_count(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前用户的未读消息数量
    """
    try:
        unread_count = Message.count_unread(current_user.id)
        
        return {
            "status": "success",
            "data": {
                "unread_count": unread_count
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取未读消息数量失败: {str(e)}"
        )


@router.get("/messages/{message_id}")
async def get_message(
    message_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取单条消息详情
    """
    try:
        message = Message.get_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="消息不存在"
            )
        
        # 检查权限：只能查看自己的消息（收件人或发件人）
        if message.recipient_id != current_user.id and message.sender_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权查看该消息"
            )
        
        # 如果是收件人且未读，标记为已读
        if message.recipient_id == current_user.id and not message.is_read:
            Message.update_read_status(message_id, True)
            message.is_read = True
        
        return {
            "status": "success",
            "data": message.to_dict()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取消息详情失败: {str(e)}"
        )


@router.put("/messages/{message_id}")
async def update_message(
    message_id: int,
    request: MessageUpdateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    更新消息状态（仅收件人可用）
    """
    try:
        message = Message.get_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="消息不存在"
            )
        
        # 检查权限：只能更新自己的消息（收件人）
        if message.recipient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权更新该消息"
            )
        
        # 更新消息状态
        success = Message.update_read_status(message_id, request.is_read)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新消息状态失败"
            )
        
        return {
            "status": "success",
            "message": "消息状态更新成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新消息状态失败: {str(e)}"
        )


@router.delete("/messages/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    删除消息（收件人或发件人可用）
    """
    try:
        message = Message.get_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="消息不存在"
            )
        
        # 检查权限：只能删除自己的消息（收件人或发件人）
        if message.recipient_id != current_user.id and message.sender_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="无权删除该消息"
            )
        
        # 删除消息
        success = Message.delete_by_id(message_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除消息失败"
            )
        
        return {
            "status": "success",
            "message": "消息删除成功"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除消息失败: {str(e)}"
        )


@router.delete("/messages")
async def delete_messages(
    message_ids: List[int] = Body(..., embed=True, description="消息ID列表"),
    current_user: User = Depends(get_current_active_user)
):
    """
    批量删除消息（收件人或发件人可用）
    """
    try:
        # 检查所有消息的权限
        for message_id in message_ids:
            message = Message.get_by_id(message_id)
            if not message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"消息ID {message_id} 不存在"
                )
            
            # 检查权限：只能删除自己的消息（收件人或发件人）
            if message.recipient_id != current_user.id and message.sender_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"无权删除消息ID {message_id}"
                )
        
        # 批量删除消息
        deleted_count = Message.delete_by_ids(message_ids)
        
        return {
            "status": "success",
            "message": f"成功删除 {deleted_count} 条消息"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量删除消息失败: {str(e)}"
        )
