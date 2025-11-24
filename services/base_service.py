#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础服务类
封装通用的业务逻辑，如Lua命令构建和发送
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)


class BaseService:
    """基础服务类"""

    def __init__(self, client, dispatcher=None):
        """
        初始化服务
        :param client: GMToolsClient 实例
        :param dispatcher: 响应分发器 (可选)
        """
        self.client = client
        self.dispatcher = dispatcher
        self._current_account = ""  # 当前操作账号，可由上层设置

    def set_current_account(self, account: str):
        """设置当前操作账号"""
        self._current_account = account

    def _dict_to_lua_table(self, data: Dict[str, Any]) -> str:
        """
        将Python字典转换为Lua表格式

        Args:
            data: Python字典

        Returns:
            str: Lua表格式的字符串
        """
        parts = []
        for key, value in data.items():
            # 处理键：整数用[1]格式，字符串用["key"]格式
            if isinstance(key, int):
                key_str = f"[{key}]"
            else:
                key_str = f'["{key}"]'
            
            # 处理值
            if isinstance(value, dict):
                # 嵌套字典，递归处理
                parts.append(f'{key_str}={{{self._dict_to_lua_table(value)}}}')
            elif isinstance(value, bool):
                # 布尔值转换为Lua格式（小写）
                parts.append(f'{key_str}={str(value).lower()}')
            elif isinstance(value, (int, float)):
                # 数值类型不加引号
                parts.append(f'{key_str}={value}')
            elif isinstance(value, (list, tuple)):
                # 列表转换为Lua数组（键为1-based索引）
                # 将列表转换为字典：{1: val1, 2: val2, ...}
                list_dict = {i + 1: v for i, v in enumerate(value)}
                parts.append(f'{key_str}={{{self._dict_to_lua_table(list_dict)}}}')
            else:
                # 其他类型（主要是字符串）加引号
                parts.append(f'{key_str}="{value}"')
        
        return ",".join(parts)

    def _format_lua_value(self, key: str, value: Any) -> str:
        """格式化单个键值对为Lua格式"""
        # 特殊处理"修改数据"键：如果已经是Lua格式的字符串，直接使用
        if (
            key == "修改数据"
            and isinstance(value, str)
            and (value.strip().startswith("{") or value.strip().startswith("["))
        ):
            return f',["{key}"]={value}'
        elif isinstance(value, dict):
            # 字典类型，递归格式化为Lua表
            return f',["{key}"]={{{self._dict_to_lua_table(value)}}}'
        elif isinstance(value, bool):
             return f',["{key}"]={str(value).lower()}'
        elif isinstance(value, (int, float)):
             return f',["{key}"]={value}'
        else:
            return f',["{key}"]="{value}"'

    def _build_lua_command(self, command: str, data: Dict[str, Any]) -> str:
        """构建Lua命令字符串"""
        content = f'do local ret={{["文本"]="{command}"'
        for key, value in data.items():
            content += self._format_lua_value(key, value)
        content += "} return ret end"
        return content

    async def send_command(
        self, 
        seq_no: int, 
        command: str, 
        data: Dict[str, Any] = None,
        wait_for_seq: Optional[int] = None,
        timeout: float = 3.0
    ) -> Union[bool, Dict[str, Any], list]:
        """
        发送命令到服务器并收集所有响应
        :param seq_no: 命令序号
        :param command: 命令文本
        :param data: 命令数据
        :param wait_for_seq: 已废弃，保留用于兼容性
        :param timeout: 等待响应的超时时间（秒）
        :return: 成功返回响应列表，失败返回 False
        """
        if not self.client:
            logger.error("未设置网络客户端")
            return False

        if data is None:
            data = {}

        content = self._build_lua_command(command, data)
        try:
            # 生成唯一的请求ID
            import uuid
            request_id = str(uuid.uuid4())
            
            # 注册响应收集器
            if self.dispatcher:
                self.dispatcher.register_collector(request_id)

            # 使用 asyncio.to_thread 将阻塞的 send 调用放入线程池
            result = await asyncio.to_thread(self.client.send, seq_no, content, self._current_account)
            
            if not result:
                if self.dispatcher:
                    self.dispatcher.cancel_collector(request_id)
                return False

            # 等待响应收集
            if self.dispatcher:
                try:
                    # 获取事件对象
                    event = self.dispatcher.get_collector_event(request_id)
                    if not event:
                        logger.error("无法获取收集器事件对象")
                        return False

                    # 等待第一个响应（带超时）
                    try:
                        await asyncio.wait_for(event.wait(), timeout=timeout)
                        
                        # 收到第一个响应后，稍微等待一小会儿以收集可能的后续分包（针对多包响应）
                        # 对于大多数单包响应，这只会增加极小的延迟(0.1s)
                        await asyncio.sleep(0.1)
                        
                    except asyncio.TimeoutError:
                        # 超时未收到任何响应
                        logger.warning(f"在 {timeout} 秒内未收到任何响应 (seq_no={seq_no})")
                        self.dispatcher.cancel_collector(request_id)
                        return {"status": "no_response", "message": "Command sent but no response received"}

                    # 获取收集到的所有响应
                    responses = self.dispatcher.get_collected_responses(request_id)
                    
                    if responses:
                        # 返回所有响应
                        return responses
                    else:
                        # 理论上不应执行到这里，除非 event 被错误触发
                        return {"status": "no_response", "message": "Event triggered but no responses found"}
                        
                except Exception as e:
                    logger.error(f"收集响应异常: {e}")
                    self.dispatcher.cancel_collector(request_id)
                    return {"status": "error", "message": str(e)}
            
            return True
        except Exception as e:
            logger.exception(f"发送命令失败: {e}")
            return False
