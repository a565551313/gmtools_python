#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMTools API 服务入口
使用 FastAPI 提供 RESTful API 接口
"""

import sys
import os
import asyncio
import argparse
import logging
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Body, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import uvicorn

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from network.client import GMToolsClient
from services.account_service import AccountService
from services.pet_service import PetService
from services.equipment_service import EquipmentService
from services.gift_service import GiftService
from services.character_service import CharacterService
from services.game_service import GameService
from api_examples import (
    ACCOUNT_EXAMPLES, PET_EXAMPLES, EQUIPMENT_EXAMPLES, 
    GIFT_EXAMPLES, CHARACTER_EXAMPLES, GAME_EXAMPLES
)
from config.settings import SERVER_HOST, SERVER_PORT, GM_ACCOUNT, GM_PASSWORD

# 配置日志
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

# Token authentication
security = HTTPBearer()
from config.settings import AUTH_TOKEN

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证 Bearer Token"""
    if credentials.scheme.lower() != "bearer" or credentials.credentials != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid authentication token")
    return True

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
    # 确保 dispatcher 获取到正确的 loop
    dispatcher.loop = asyncio.get_running_loop()
    
    logger.info("正在初始化 GMTools API 服务...")
    
    if shared_client:
        logger.info("使用共享的 GameClient 实例")
        client = shared_client
        # 注册分发器到共享客户端
        # 注意：这里我们需要一种方式不覆盖原有的 on_receive
        # 我们假设调用者已经处理好了多播，或者我们在这里做一个简单的链式调用
        original_on_receive = client.on_receive
        
        def multicast_on_receive(data):
            if original_on_receive:
                original_on_receive(data)
            dispatcher.dispatch(data)
            
        client.on_receive = multicast_on_receive
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

@app.post("/api/account")
async def account_endpoint(
    request: ModuleRequest = Body(..., examples=ACCOUNT_EXAMPLES),
    token: bool = Depends(verify_token)
):
    """账号模块统一接口"""
    return await handle_service_request(account_service, request)

@app.post("/api/pet")
async def pet_endpoint(
    request: ModuleRequest = Body(..., examples=PET_EXAMPLES),
    token: bool = Depends(verify_token)
):
    """宝宝模块统一接口"""
    return await handle_service_request(pet_service, request)

@app.post("/api/equipment")
async def equipment_endpoint(
    request: ModuleRequest = Body(..., examples=EQUIPMENT_EXAMPLES),
    token: bool = Depends(verify_token)
):
    """装备模块统一接口"""
    return await handle_service_request(equipment_service, request)

@app.post("/api/gift")
async def gift_endpoint(
    request: ModuleRequest = Body(..., examples=GIFT_EXAMPLES),
    token: bool = Depends(verify_token)
):
    """物品赠送模块统一接口"""
    return await handle_service_request(gift_service, request)

@app.post("/api/character")
async def character_endpoint(
    request: ModuleRequest = Body(..., examples=CHARACTER_EXAMPLES),
    token: bool = Depends(verify_token)
):
    """角色管理模块统一接口"""
    return await handle_service_request(character_service, request)

@app.post("/api/game")
async def game_endpoint(
    request: ModuleRequest = Body(..., examples=GAME_EXAMPLES),
    token: bool = Depends(verify_token)
):
    """游戏管理模块统一接口"""
    return await handle_service_request(game_service, request)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GMTools API Service")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind")
    args = parser.parse_args()
    
    uvicorn.run("api_main:app", host=args.host, port=args.port, reload=False, log_level="info")
