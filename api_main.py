#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMTools API 服务入口
使用 FastAPI 提供 RESTful API 接口
"""

import sys
import os
import asyncio
from contextlib import asynccontextmanager
import argparse
import logging
import uvicorn
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from network.client import GMToolsClient
from services.account_service import AccountService
from services.pet_service import PetService
from services.equipment_service import EquipmentService
from services.gift_service import GiftService
from services.character_service import CharacterService
from services.game_service import GameService
from database.activation_code import ActivationCode
from database.permissions import Permission, LevelPermission
from api_examples import (
    ACCOUNT_EXAMPLES, PET_EXAMPLES, EQUIPMENT_EXAMPLES, 
    GIFT_EXAMPLES, CHARACTER_EXAMPLES, GAME_EXAMPLES
)
from config.settings import SERVER_HOST, SERVER_PORT, GM_ACCOUNT, GM_PASSWORD

# 配置日志
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Depends, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,  # 强制重新配置日志
    handlers=[logging.StreamHandler(sys.stdout)]  # 明确输出到 stdout
)
logger = logging.getLogger(__name__)

# 全局实例
client: Optional[GMToolsClient] = None
account_service: Optional[AccountService] = None
pet_service: Optional[PetService] = None
equipment_service: Optional[EquipmentService] = None
gift_service: Optional[GiftService] = None
character_service: Optional[CharacterService] = None
game_service: Optional[GameService] = None

# 导入新的认证依赖
from auth.dependencies import get_current_active_user
from auth.level_permissions import require_level
from database.models import User as AuthUser, AuditLog

# 通用请求模型
class ModuleRequest(BaseModel):
    function: str
    args: Dict[str, Any] = {}

class ResponseDispatcher:
    """响应分发器 - 支持收集所有响应"""
    def __init__(self):
        self.listeners: Dict[int, asyncio.Future] = {}  # 单序号监听器
        self.collectors: Dict[str, Dict[str, Any]] = {}  # 响应收集器 {request_id: {responses: [], event: Event}}
        self.lock = asyncio.Lock()
        self.loop = None

    def register(self, seq_no: int) -> asyncio.Future:
        """注册等待特定序号的响应（用于登录等特定场景）"""
        future = self.loop.create_future()
        self.listeners[seq_no] = future
        return future
    
    def register_collector(self, request_id: str) -> str:
        """注册响应收集器，返回 request_id"""
        import time
        if request_id not in self.collectors:
            self.collectors[request_id] = {
                'responses': [],
                'event': asyncio.Event(),
                'start_time': time.time()  # 记录创建时间
            }
        return request_id
    
    def get_collected_responses(self, request_id: str) -> list:
        """获取收集到的所有响应"""
        if request_id in self.collectors:
            responses = self.collectors[request_id]['responses']
            del self.collectors[request_id]
            return responses
        return []
        
    def cancel(self, seq_no: int, future: asyncio.Future):
        """取消等待"""
        if seq_no in self.listeners and self.listeners[seq_no] is future:
            del self.listeners[seq_no]
    
    def cancel_collector(self, request_id: str):
        """取消收集器"""
        if request_id in self.collectors:
            del self.collectors[request_id]

    def has_active_collectors(self) -> bool:
        """检查是否有活跃的收集器（表示正在处理API请求）"""
        return len(self.collectors) > 0

    def get_collector_event(self, request_id: str) -> asyncio.Event:
        """获取收集器的事件对象"""
        if request_id in self.collectors:
            return self.collectors[request_id]['event']
        return None
            
    def dispatch(self, data: dict):
        """分发收到的数据 (线程安全)"""
        import time
        seq_no = data.get("seq_no")
        current_time = time.time()
        
        # 1. 处理单序号监听器（用于登录等）
        if seq_no in self.listeners:
            future = self.listeners[seq_no]
            if not future.done():
                self.loop.call_soon_threadsafe(future.set_result, data)
            del self.listeners[seq_no]
        
        # 2. 将响应添加到所有活跃的收集器（但只添加到创建时间之后的响应）
        for request_id, collector in list(self.collectors.items()):
            # 只添加在收集器创建之后到达的响应（允许0.1秒的缓冲）
            if current_time >= collector['start_time'] - 0.1:
                collector['responses'].append(data)
                # 触发事件通知有新响应
                self.loop.call_soon_threadsafe(collector['event'].set)

# 全局分发器
dispatcher = ResponseDispatcher()

# 共享的 GameClient 实例
shared_client = None

def set_shared_client(client):
    """设置共享的 GameClient 实例"""
    global shared_client
    shared_client = client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """服务生命周期管理"""
    global client, account_service, pet_service, equipment_service, gift_service, character_service, game_service
    
    # --- 启动逻辑 ---
    # 初始化数据库
    from database.connection import db as database
    logger.info("正在初始化数据库...")
    database.init_database()
    logger.info("数据库初始化完成")
    
    # 确保 dispatcher 获取到正确的 loop
    dispatcher.loop = asyncio.get_running_loop()

    
    logger.info("正在初始化 GMTools API 服务...")
    
    if shared_client:
        logger.info("使用共享的 GameClient 实例")
        client = shared_client
        # 注册分发器到共享客户端
        # 使用标记避免重复注册 multicast_on_receive，防止回调链堆叠
        if not getattr(client, '_dispatcher_registered', False):
            original_on_receive = client.on_receive
            
            def multicast_on_receive(data):
                if original_on_receive:
                    original_on_receive(data)
                dispatcher.dispatch(data)
                
            client.on_receive = multicast_on_receive
            client._dispatcher_registered = True
            logger.info("已注册响应分发器到共享客户端")
        else:
            logger.info("分发器已注册，跳过重复注册")
    else:
        client = GMToolsClient()
        if client.connect(SERVER_HOST, SERVER_PORT):
            logger.info(f"成功连接到游戏服务器: {SERVER_HOST}:{SERVER_PORT}")
            # 启动分发器的监听
            client.on_receive = dispatcher.dispatch
        else:
            logger.error(f"连接游戏服务器失败: {SERVER_HOST}:{SERVER_PORT}")

    account_service = AccountService(client, dispatcher)
    pet_service = PetService(client, dispatcher)
    equipment_service = EquipmentService(client, dispatcher)
    gift_service = GiftService(client, dispatcher)
    activity_manager.set_gift_service(gift_service)
    character_service = CharacterService(client, dispatcher)
    game_service = GameService(client, dispatcher)
    
    # 设置默认操作账号 (GM账号)
    for service in [account_service, pet_service, equipment_service, gift_service, character_service, game_service]:
        service.set_current_account(GM_ACCOUNT)
        
    # 如果是独立连接，则执行登录
    if not shared_client:
        logger.info(f"正在尝试登录 GM 账号: {GM_ACCOUNT}...")
        
        # 注册登录响应监听
        login_future = dispatcher.register(7) # 登录成功
        login_fail_future = dispatcher.register(999) # 登录失败
        
        # 发送登录请求
        if client.send_login(GM_ACCOUNT, GM_PASSWORD):
            try:
                # 等待登录响应，超时时间 10 秒
                done, pending = await asyncio.wait(
                    [login_future, login_fail_future], 
                    return_when=asyncio.FIRST_COMPLETED,
                    timeout=10.0
                )
                
                if login_future in done:
                    logger.info(f"GM 账号登录验证通过，API 服务准备就绪")
                elif login_fail_future in done:
                    logger.warning(f"警告: GM 账号登录失败")
                else:
                    logger.warning("警告: 登录响应超时")
                    
            except Exception as e:
                 logger.error(f"登录过程异常: {e}")
        else:
            logger.error("错误: 发送登录请求失败")
            
        # 清理未完成的 future
        dispatcher.cancel(7, login_future)
        dispatcher.cancel(999, login_fail_future)
    else:
        logger.info("使用共享连接，跳过 API 独立登录")

    yield

    # --- 关闭逻辑 ---
    if client and not shared_client:
        print("正在断开与游戏服务器的连接...")
        client.disconnect()

# 创建 FastAPI 应用
app = FastAPI(
    title="GMTools API",
    description="梦江南超级GM工具 RESTful API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册用户管理路由
from routes.user_routes import router as user_router
app.include_router(user_router)

# 注册活动管理路由
from routes.activity_routes import activity_router, activity_manager
app.include_router(activity_router)

# 注册消息管理路由
from routes.message_routes import router as message_router
app.include_router(message_router)

@app.middleware("http")

async def log_requests(request: Request, call_next):
    """记录所有请求的中间件"""
    import time
    start_time = time.time()
    
    # 打印请求信息
    logger.info(f"收到请求: {request.method} {request.url.path}")
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(f"请求处理完成: {request.method} {request.url.path} - 状态码: {response.status_code} - 耗时: {process_time:.4f}s")
    
    return response

# 挂载静态文件目录
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    return {"message": "GMTools API is running", "connected": client.connected if client else False}

@app.get("/docs-custom")
async def custom_docs():
    """自定义 API 测试页面"""
    return FileResponse(os.path.join(static_dir, "api_tester.html"))

@app.get("/user-management")
async def user_management():
    """用户管理页面"""
    return FileResponse(os.path.join(static_dir, "user-management.html"))

@app.get("/user-functions")
async def user_functions():
    """用户功能系统页面"""
    return FileResponse(os.path.join(static_dir, "user-functions.html"))

@app.get("/level-permissions")
async def level_permissions():
    """权限配置页面"""
    return FileResponse(os.path.join(static_dir, "level-permissions.html"))

@app.get("/activation-codes")
async def activation_codes():
    """激活码管理页面"""
    return FileResponse(os.path.join(static_dir, "activation-codes.html"))

async def handle_service_request(service, request: ModuleRequest):
    """通用服务请求处理"""
    if not client or not client.connected:
        if not client.connect(SERVER_HOST, SERVER_PORT):
            raise HTTPException(status_code=503, detail="Game server not connected")
    if not hasattr(service, request.function):
        raise HTTPException(status_code=400, detail=f"Function '{request.function}' not found in service")
    try:
        method = getattr(service, request.function)
        result = method(**request.args)
        if isinstance(result, bool):
            success = result
            response_data = None
        else:
            # result 是 awaitable，等待结果
            response_data = await result
            success = bool(response_data)

        if success:
            # 返回实际的响应数据
            if isinstance(response_data, (dict, list)):
                return {"status": "success", "data": response_data}
            elif response_data:
                return {"status": "success", "data": response_data}
            else:
                return {"status": "success", "message": f"Executed {request.function}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send command")
    except TypeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid arguments: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 注册权限管理路由
from routes.permission_routes import router as permission_router
app.include_router(permission_router)

# 注册活动管理路由
from routes.activity_routes import activity_router
app.include_router(activity_router)

# 导入权限检查
from auth.permission_checker import require_permission, has_permission

# 功能权限映射表
FUNCTION_PERMISSIONS = {
    # 账号模块
    "account": {
        "recharge_currency": "recharge.currency",
        "send_travel_fee": "account.send_travel_fee",
        "recharge_gm_level": "recharge.gm_level",
        "manage_account": "account.ban",
        "change_password": "account.change_password",
        "give_title": "account.give_title",
        "recharge_skill": "recharge.crafting_skill",
        "recharge_faction": "recharge.faction_contribution",
        "recharge_gm_coin": "recharge.gm_coin",
        "recharge_record": "account.player_info",
        "set_bagua": "recharge.bagua",
    },
    # 宠物模块
    "pet": {
        "get_pet_info": "pet.get_info",
        "modify_pet": "pet.modify",
        "custom_pet_equip": "pet.custom_equip",
        "get_mount": "pet.get_mount",
        "modify_mount": "pet.modify_mount",
    },
    # 装备模块
    "equipment": {
        "get_equipment": "equipment.custom",
        "send_equipment": "equipment.custom",
        "get_ornament": "equipment.ornament",
        "send_ornament": "equipment.ornament",
        "get_pet_equipment": "equipment.custom",
        "send_pet_equipment": "equipment.custom",
        "get_affix": "equipment.affix",
        "send_affix": "equipment.affix",
    },
    # 礼物模块
    "gift": {
        "give_item": "gift.give_item",
        "give_gem": "gift.give_gem",
        "get_recharge_types": "gift.get_recharge_types",
        "get_recharge_card": "gift.get_recharge_cards",
        "generate_cdk": "gift.generate_cdk",
        "generate_custom_cdk": "gift.generate_custom_cdk",
        "new_recharge_type": "gift.new_recharge_type",
        "del_recharge_type": "gift.del_recharge_type",
    },
    # 角色模块
    "character": {
        "get_character_info": "character.get_info",
        "recover_character_props": "character.recover_props",
        "modify_character": "character.modify",
    },
    # 游戏模块
    "game": {
        "send_broadcast": "game.broadcast",
        "send_announcement": "game.announcement",
        "set_exp_rate": "game.exp_rate",
        "set_difficulty": "game.difficulty",
        "set_level_cap": "game.level_cap",
        "trigger_activity": "game.activity",
    }
}

def check_function_permission(user: AuthUser, module: str, function: str):
    """检查用户是否有执行特定功能的权限"""
    # 获取该功能需要的权限
    module_perms = FUNCTION_PERMISSIONS.get(module, {})
    required_perm = module_perms.get(function)
    
    # 如果没有明确定义权限，则默认需要该模块的查看权限或基础权限
    if not required_perm:
        # 尝试使用模块名作为权限前缀
        if module == "account":
            required_perm = "account.view"
        elif module == "pet":
            required_perm = "pet.modify"
        elif module == "equipment":
            required_perm = "equipment.modify"
        elif module == "gift":
            required_perm = "gift.send"
        elif module == "character":
            required_perm = "character.view"
        elif module == "game":
            required_perm = "game.config"
        else:
            required_perm = f"{module}.view"
            
    if not has_permission(user, required_perm):
        logger.warning(f"用户 {user.username} (Level {user.level}) 尝试执行 {module}.{function} 被拒绝 (需要 {required_perm})")
        raise HTTPException(
            status_code=403,
            detail=f"权限不足: 需要 {required_perm}"
        )

@app.post("/api/account")
async def account_endpoint(
    request_data: ModuleRequest = Body(..., examples=ACCOUNT_EXAMPLES),
    http_request: Request = None,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    账号模块统一接口
    """
    check_function_permission(current_user, "account", request_data.function)
    
    # 记录操作日志
    AuditLog.create(
        user_id=current_user.id,
        action="ACCOUNT_OPERATION",
        resource="account",
        details=f"{current_user.username} 执行 {request_data.function}",
        ip_address=http_request.client.host if http_request and http_request.client else None
    )
    return await handle_service_request(account_service, request_data)

@app.post("/api/pet")
async def pet_endpoint(
    request_data: ModuleRequest = Body(..., examples=PET_EXAMPLES),
    http_request: Request = None,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    宝宝模块统一接口
    """
    check_function_permission(current_user, "pet", request_data.function)
    
    AuditLog.create(
        user_id=current_user.id,
        action="PET_OPERATION",
        resource="pet",
        details=f"{current_user.username} 执行 {request_data.function}",
        ip_address=http_request.client.host if http_request and http_request.client else None
    )
    return await handle_service_request(pet_service, request_data)

@app.post("/api/equipment")
async def equipment_endpoint(
    request_data: ModuleRequest = Body(..., examples=EQUIPMENT_EXAMPLES),
    http_request: Request = None,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    装备模块统一接口
    """
    check_function_permission(current_user, "equipment", request_data.function)
    
    AuditLog.create(
        user_id=current_user.id,
        action="EQUIPMENT_OPERATION",
        resource="equipment",
        details=f"{current_user.username} 执行 {request_data.function}",
        ip_address=http_request.client.host if http_request and http_request.client else None
    )
    return await handle_service_request(equipment_service, request_data)

@app.post("/api/gift")
async def gift_endpoint(
    request_data: ModuleRequest = Body(..., examples=GIFT_EXAMPLES),
    http_request: Request = None,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    物品赠送模块统一接口
    """
    check_function_permission(current_user, "gift", request_data.function)
    
    AuditLog.create(
        user_id=current_user.id,
        action="GIFT_OPERATION",
        resource="gift",
        details=f"{current_user.username} 执行 {request_data.function}",
        ip_address=http_request.client.host if http_request and http_request.client else None
    )
    return await handle_service_request(gift_service, request_data)

@app.post("/api/character")
async def character_endpoint(
    request_data: ModuleRequest = Body(..., examples=CHARACTER_EXAMPLES),
    http_request: Request = None,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    角色管理模块统一接口
    """
    check_function_permission(current_user, "character", request_data.function)
    
    AuditLog.create(
        user_id=current_user.id,
        action="CHARACTER_OPERATION",
        resource="character",
        details=f"{current_user.username} 执行 {request_data.function}",
        ip_address=http_request.client.host if http_request and http_request.client else None
    )
    return await handle_service_request(character_service, request_data)

@app.post("/api/game")
async def game_endpoint(
    request_data: ModuleRequest = Body(..., examples=GAME_EXAMPLES),
    http_request: Request = None,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    游戏模块统一接口
    """
    check_function_permission(current_user, "game", request_data.function)
    
    # 记录操作日志
    AuditLog.create(
        user_id=current_user.id,
        action="GAME_OPERATION",
        resource="game",
        details=f"{current_user.username} 执行 {request_data.function}",
        ip_address=http_request.client.host if http_request and http_request.client else None
    )
    return await handle_service_request(game_service, request_data)


@app.post("/api/activation/generate")
async def generate_activation_codes(
    level: int = Body(..., embed=True),
    count: int = Body(default=1, embed=True),
    expires_days: int = Body(default=30, embed=True),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    生成激活码
    """
    # 只有管理员和超级管理员可以生成激活码
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="权限不足")
    
    codes = ActivationCode.create(level, expires_days, count)
    return {
        "status": "success",
        "data": [code.to_dict() for code in codes],
        "message": f"成功生成 {count} 个激活码"
    }


@app.get("/api/activation/list")
async def get_activation_codes(
    page: int = 1,
    limit: int = 20,
    level: int = None,
    is_used: bool = None,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    获取激活码列表
    """
    # 只有管理员和超级管理员可以查看激活码列表
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="权限不足")
    
    offset = (page - 1) * limit
    codes = ActivationCode.get_all(limit, offset)
    
    # 过滤条件
    if level is not None:
        codes = [code for code in codes if code.level == level]
    if is_used is not None:
        codes = [code for code in codes if code.is_used == is_used]
    
    # 为每个激活码添加用户名和权限等级信息
    codes_with_user_info = []
    for code in codes:
        code_dict = code.to_dict()
        if code.is_used and code.used_by:
            # 查询使用该激活码的用户信息
            user = AuthUser.get_by_id(code.used_by)
            if user:
                code_dict["used_username"] = user.username
                code_dict["used_user_level"] = user.level
            else:
                code_dict["used_username"] = "未知用户"
                code_dict["used_user_level"] = 0
        else:
            code_dict["used_username"] = None
            code_dict["used_user_level"] = None
        codes_with_user_info.append(code_dict)
    
    total = ActivationCode.count()
    return {
        "status": "success",
        "data": {
            "codes": codes_with_user_info,
            "total": total,
            "page": page,
            "limit": limit
        }
    }


@app.post("/api/activation/use")
async def use_activation_code(
    code: str = Body(..., embed=True),
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    使用激活码
    """
    # 禁止管理员使用激活码，避免权限被意外降低
    if current_user.role in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="管理员无需使用激活码")
    
    new_level = ActivationCode.activate(code, current_user.id)
    
    if new_level is None:
        raise HTTPException(status_code=400, detail="激活码无效或已过期")
    
    # 更新用户等级
    user = User.get_by_id(current_user.id)
    if user:
        user.level = new_level
        user.update()
    
    return {
        "status": "success",
        "message": f"激活成功，您的等级已提升至 {new_level}",
        "data": {"new_level": new_level}
    }


@app.delete("/api/activation/{code}")
async def delete_activation_code(
    code: str,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    删除激活码
    """
    # 只有管理员和超级管理员可以删除激活码
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="权限不足")
    
    success = ActivationCode.delete(code)
    if not success:
        raise HTTPException(status_code=400, detail="删除失败")
    
    return {
        "status": "success",
        "message": "激活码删除成功"
    }


@app.get("/api/permissions/all")
async def get_all_permissions(
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    获取所有权限列表
    """
    permissions = Permission.get_all()
    return {
        "status": "success",
        "data": [perm.to_dict() for perm in permissions]
    }


@app.get("/api/permissions/level/{level}")
async def get_level_permissions(
    level: int,
    current_user: AuthUser = Depends(get_current_active_user)
):
    """
    获取指定level的权限
    """
    # 验证level范围
    if level < 1 or level > 10:
        raise HTTPException(status_code=400, detail="level必须在1-10之间")
    
    permissions = LevelPermission.get_level_permissions(level)
    return {
        "status": "success",
        "data": permissions
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GMTools API Service")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()
    
    uvicorn.run("api_main:app", host=args.host, port=args.port, reload=False, log_level="info")
