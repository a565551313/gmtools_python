#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理 API 路由
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, status, Request, Body
from pydantic import BaseModel, EmailStr, Field
from database.models import User, AuditLog
from auth.user_service import UserAuthService
from auth.dependencies import (
    get_current_active_user,
    get_current_admin_user,
    get_client_ip
)
from utils.password_generator import generate_secure_password

class UserCreateRequest(BaseModel):
    """创建用户请求（管理员）"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    level: int = Field(1, ge=1, le=10, description="用户等级(1-10)")
    role: str = Field("user", description="角色: user, admin, super_admin")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "newuser",
                "email": "newuser@example.com",
                "level": 1,
                "role": "user"
            }
        }


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")
    level: int = Field(1, ge=1, le=10, description="用户等级(1-10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "password123",
                "level": 1
            }
        }


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "testuser",
                "password": "password123"
            }
        }


class UserLoginResponse(BaseModel):
    """用户登录响应"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserUpdateRequest(BaseModel):
    """用户更新请求"""
    email: Optional[EmailStr] = Field(None, description="邮箱")
    level: Optional[int] = Field(None, ge=1, le=10, description="用户等级(1-10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newemail@example.com",
                "level": 2
            }
        }


class PasswordChangeRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")
    
    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "oldpassword123",
                "new_password": "newpassword123"
            }
        }


class PasswordResetRequest(BaseModel):
    """重置密码请求（管理员）"""
    new_password: Optional[str] = Field(None, min_length=6, description="新密码（留空自动生成）")
    
    class Config:
        json_schema_extra = {
            "example": {
                "new_password": "newpassword123"
            }
        }


class UserRoleUpdateRequest(BaseModel):
    """用户角色更新请求"""
    role: str = Field(..., description="角色: user, admin, super_admin")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "admin"
            }
        }


class UserStatusUpdateRequest(BaseModel):
    """用户状态更新请求"""
    is_active: bool = Field(..., description="是否激活")
    
    class Config:
        json_schema_extra = {
            "example": {
                "is_active": False
            }
        }


class UserLevelUpdateRequest(BaseModel):
    """用户等级更新请求"""
    level: int = Field(..., ge=1, le=10, description="用户等级(1-10)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "level": 5
            }
        }



# ==================== 路由定义 ====================
router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

# ==================== 公开路由 ====================

@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: UserRegisterRequest
):
    """
    用户注册
    
    - **username**: 用户名（3-50字符）
    - **email**: 邮箱地址
    - **password**: 密码（至少6位）
    - **full_name**: 全名（可选）
    """
    success, user, error = UserAuthService.register(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        level=user_data.level
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # 记录 IP
    ip_address = get_client_ip(request)
    AuditLog.create(
        user_id=user.id,
        action="USER_REGISTER",
        resource="users",
        details=f"新用户注册: {user.username}",
        ip_address=ip_address
    )
    
    return {
        "status": "success",
        "message": "注册成功",
        "user": user.to_dict()
    }


@router.post("/login", response_model=UserLoginResponse)
async def login(
    request: Request,
    credentials: UserLoginRequest
):
    """
    用户登录
    
    - **username**: 用户名
    - **password**: 密码
    
    返回 JWT Token
    """
    success, token, user, error = UserAuthService.login(
        username=credentials.username,
        password=credentials.password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 记录 IP
    ip_address = get_client_ip(request)
    AuditLog.create(
        user_id=user.id,
        action="USER_LOGIN",
        resource="users",
        details=f"用户登录: {user.username}",
        ip_address=ip_address
    )
    
    return UserLoginResponse(
        access_token=token,
        user=user.to_dict()
    )


# ==================== 需要认证的路由 ====================

@router.get("/me", response_model=dict)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前登录用户信息
    
    需要 Bearer Token 认证
    """
    return {
        "status": "success",
        "user": current_user.to_dict()
    }


@router.put("/me", response_model=dict)
async def update_current_user(
    request: Request,
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    更新当前用户信息
    
    - **email**: 新邮箱（可选）
    - **level**: 新等级（可选,1-10）
    """
    # 检查邮箱是否被其他用户使用
    if user_data.email and user_data.email != current_user.email:
        existing_user = User.get_by_email(user_data.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被其他用户使用"
            )
        current_user.email = user_data.email
    
    if user_data.level is not None:
        current_user.level = user_data.level
    
    if current_user.update():
        # 记录审计日志
        ip_address = get_client_ip(request)
        AuditLog.create(
            user_id=current_user.id,
            action="USER_UPDATE",
            resource="users",
            details=f"用户更新信息: {current_user.username}",
            ip_address=ip_address
        )
        
        return {
            "status": "success",
            "message": "更新成功",
            "user": current_user.to_dict()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新失败"
        )


@router.post("/me/change-password", response_model=dict)
async def change_password(
    request: Request,
    password_data: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    修改当前用户密码
    
    - **old_password**: 旧密码
    - **new_password**: 新密码（至少6位）
    """
    success, error = UserAuthService.change_password(
        user_id=current_user.id,
        old_password=password_data.old_password,
        new_password=password_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # 记录审计日志
    ip_address = get_client_ip(request)
    AuditLog.create(
        user_id=current_user.id,
        action="PASSWORD_CHANGE",
        resource="users",
        details=f"用户修改密码: {current_user.username}",
        ip_address=ip_address
    )
    
    return {
        "status": "success",
        "message": "密码修改成功"
    }


@router.get("/me/logs", response_model=dict)
async def get_current_user_logs(
    current_user: User = Depends(get_current_active_user),
    limit: int = 50
):
    """
    获取当前用户的操作日志
    
    - **limit**: 返回记录数量（默认50）
    """
    logs = AuditLog.get_by_user(current_user.id, limit=limit)
    
    return {
        "status": "success",
        "logs": logs,
        "total": len(logs)
    }


# ==================== 管理员路由 ====================

@router.get("/", response_model=dict)
async def list_users(
    admin_user: User = Depends(get_current_admin_user),
    limit: int = 100,
    offset: int = 0
):
    """
    获取用户列表（管理员）
    
    - **limit**: 每页数量（默认100）
    - **offset**: 偏移量（默认0）
    """
    users = User.get_all(limit=limit, offset=offset)
    total = User.count()
    
    return {
        "status": "success",
        "users": [user.to_dict() for user in users],
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    获取指定用户信息（管理员）
    
    - **user_id**: 用户ID
    """
    user = User.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return {
        "status": "success",
        "user": user.to_dict()
    }


@router.put("/{user_id}/role", response_model=dict)
async def update_user_role(
    request: Request,
    user_id: int,
    role_data: UserRoleUpdateRequest,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    更新用户角色（管理员）
    
    - **user_id**: 用户ID
    - **role**: 新角色（user, admin, super_admin）
    """
    user = User.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 验证角色
    valid_roles = ["user", "admin", "super_admin"]
    if role_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的角色，必须是: {', '.join(valid_roles)}"
        )
    
    user.role = role_data.role
    
    if user.update():
        # 记录审计日志
        ip_address = get_client_ip(request)
        AuditLog.create(
            user_id=admin_user.id,
            action="USER_ROLE_UPDATE",
            resource="users",
            details=f"管理员 {admin_user.username} 修改用户 {user.username} 角色为 {role_data.role}",
            ip_address=ip_address
        )
        
        return {
            "status": "success",
            "message": "角色更新成功",
            "user": user.to_dict()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="角色更新失败"
        )


@router.put("/{user_id}/level", response_model=dict)
async def update_user_level(
    request: Request,
    user_id: int,
    level_data: UserLevelUpdateRequest,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    更新用户等级（管理员）
    
    - **user_id**: 用户ID
    - **level**: 新等级（1-10）
    """
    user = User.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    user.level = level_data.level
    
    if user.update():
        # 记录审计日志
        ip_address = get_client_ip(request)
        AuditLog.create(
            user_id=admin_user.id,
            action="USER_LEVEL_UPDATE",
            resource="users",
            details=f"管理员 {admin_user.username} 修改用户 {user.username} 等级为 {level_data.level}",
            ip_address=ip_address
        )
        
        return {
            "status": "success",
            "message": "等级更新成功",
            "user": user.to_dict()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="等级更新失败"
        )



@router.put("/{user_id}/status", response_model=dict)
async def update_user_status(
    request: Request,
    user_id: int,
    status_data: UserStatusUpdateRequest,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    更新用户状态（管理员）
    
    - **user_id**: 用户ID
    - **is_active**: 是否激活
    """
    user = User.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能禁用自己
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能禁用自己的账号"
        )
    
    user.is_active = status_data.is_active
    
    if user.update():
        # 记录审计日志
        ip_address = get_client_ip(request)
        action = "USER_ACTIVATE" if status_data.is_active else "USER_DEACTIVATE"
        AuditLog.create(
            user_id=admin_user.id,
            action=action,
            resource="users",
            details=f"管理员 {admin_user.username} {'激活' if status_data.is_active else '禁用'} 用户 {user.username}",
            ip_address=ip_address
        )
        
        return {
            "status": "success",
            "message": "状态更新成功",
            "user": user.to_dict()
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="状态更新失败"
        )


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: Request,
    user_data: UserCreateRequest,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    创建新用户（管理员）
    
    - **username**: 用户名
    - **email**: 邮箱
    - **level**: 等级 (1-10)
    - **role**: 角色
    
    自动生成安全密码并返回
    """
    # 自动生成密码
    password = generate_secure_password()
    
    success, user, error = UserAuthService.register(
        username=user_data.username,
        email=user_data.email,
        password=password,
        level=user_data.level,
        role=user_data.role
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # 记录审计日志
    ip_address = get_client_ip(request)
    AuditLog.create(
        user_id=admin_user.id,
        action="USER_CREATE",
        resource="users",
        details=f"管理员 {admin_user.username} 创建用户 {user.username} (Level {user.level})",
        ip_address=ip_address
    )
    
    return {
        "status": "success",
        "message": "用户创建成功",
        "user": user.to_dict(),
        "temp_password": password
    }


@router.post("/{user_id}/reset-password", response_model=dict)
async def reset_user_password(
    request: Request,
    user_id: int,
    password_data: PasswordResetRequest,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    重置用户密码（管理员）
    
    - **user_id**: 用户ID
    - **new_password**: 新密码（可选，留空自动生成）
    """
    user = User.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 如果未提供密码，则自动生成
    new_password = password_data.new_password
    if not new_password:
        new_password = generate_secure_password()
    
    success, error = UserAuthService.reset_password(
        user_id=user_id,
        new_password=new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # 记录审计日志
    ip_address = get_client_ip(request)
    AuditLog.create(
        user_id=admin_user.id,
        action="PASSWORD_RESET_ADMIN",
        resource="users",
        details=f"管理员 {admin_user.username} 重置用户 {user.username} 的密码",
        ip_address=ip_address
    )
    
    return {
        "status": "success",
        "message": "密码重置成功",
        "temp_password": new_password
    }
    ip_address = get_client_ip(request)
    AuditLog.create(
        user_id=admin_user.id,
        action="PASSWORD_RESET_ADMIN",
        resource="users",
        details=f"管理员 {admin_user.username} 重置用户 {user.username} 的密码",
        ip_address=ip_address
    )
    
    return {
        "status": "success",
        "message": "密码重置成功"
    }


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    request: Request,
    user_id: int,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    删除用户（管理员）
    
    - **user_id**: 用户ID
    """
    user = User.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号"
        )
    
    username = user.username
    
    if user.delete():
        # 记录审计日志
        ip_address = get_client_ip(request)
        AuditLog.create(
            user_id=admin_user.id,
            action="USER_DELETE",
            resource="users",
            details=f"管理员 {admin_user.username} 删除用户 {username}",
            ip_address=ip_address
        )
        
        return {
            "status": "success",
            "message": "用户删除成功"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="用户删除失败"
        )


@router.get("/logs/all", response_model=dict)
async def get_all_logs(
    admin_user: User = Depends(get_current_admin_user),
    limit: int = 100,
    offset: int = 0
):
    """
    获取所有操作日志（管理员）
    
    - **limit**: 每页数量（默认100）
    - **offset**: 偏移量（默认0）
    """
    logs = AuditLog.get_all(limit=limit, offset=offset)
    
    return {
        "status": "success",
        "logs": logs,
        "total": len(logs),
        "limit": limit,
        "offset": offset
    }


@router.delete("/logs", response_model=dict)
async def delete_logs(
    request: Request,
    log_ids: list[int] = Body(..., embed=True),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    删除指定的操作日志（管理员）
    
    - **log_ids**: 要删除的日志ID列表
    """
    if not log_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请至少选择一条日志"
        )
    
    # 删除日志
    deleted_count = AuditLog.delete_by_ids(log_ids)
    
    # 记录删除操作
    ip_address = get_client_ip(request)
    AuditLog.create(
        user_id=admin_user.id,
        action="LOGS_DELETE",
        resource="audit_logs",
        details=f"删除了 {deleted_count} 条操作日志",
        ip_address=ip_address
    )
    
    return {
        "status": "success",
        "message": f"成功删除 {deleted_count} 条日志",
        "deleted_count": deleted_count
    }


@router.delete("/logs/all", response_model=dict)
async def clear_all_logs(
    request: Request,
    admin_user: User = Depends(get_current_admin_user)
):
    """
    清空所有操作日志（管理员）
    
    ⚠️ 危险操作：将删除所有审计日志记录
    """
    # 获取总数
    total_count = AuditLog.count_all()
    
    # 清空所有日志
    deleted_count = AuditLog.delete_all()
    
    # 记录清空操作（这条日志会被保留）
    ip_address = get_client_ip(request)
    AuditLog.create(
        user_id=admin_user.id,
        action="LOGS_CLEAR_ALL",
        resource="audit_logs",
        details=f"清空了所有操作日志（共 {total_count} 条）",
        ip_address=ip_address
    )
    
    return {
        "status": "success",
        "message": f"成功清空所有日志（共 {deleted_count} 条）",
        "deleted_count": deleted_count
    }

