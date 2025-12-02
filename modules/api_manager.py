#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 服务管理器
负责管理 API 服务的生命周期（启动、停止、监控）和配置
使用 QThread 在主进程中运行 FastAPI，以共享 GameClient 连接
"""

import sys
import os
import logging
import uvicorn
from PyQt6.QtCore import QObject, QThread, pyqtSignal
from config.config_manager import ConfigManager
import api_main  # 导入 API 主模块

logger = logging.getLogger(__name__)

class QtLogHandler(logging.Handler):
    """将日志转发到 Qt 信号的 LogHandler"""
    def __init__(self, signal):
        super().__init__()
        self.signal = signal
        self.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    def emit(self, record):
        try:
            msg = self.format(record)
            self.signal.emit(msg)
        except Exception:
            self.handleError(record)

class APIThread(QThread):
    """运行 uvicorn 服务的线程"""
    def __init__(self, app, host, port):
        super().__init__()
        self.app = app
        self.host = host
        self.port = port
        self.server = None

    def run(self):
        # 配置 uvicorn
        # loop="asyncio" 确保使用标准 asyncio 循环，与 api_main 中的 dispatcher 兼容
        config = uvicorn.Config(self.app, host=self.host, port=self.port, log_level="info", loop="asyncio")
        self.server = uvicorn.Server(config)
        # 运行服务 (阻塞直到 should_exit 被设置)
        self.server.run()

    def stop(self):
        if self.server:
            self.server.should_exit = True
        # 等待线程结束
        self.wait()

class APIManager(QObject):
    """API 服务管理器"""
    
    # 信号定义
    service_started = pyqtSignal()
    service_stopped = pyqtSignal()
    log_received = pyqtSignal(str)
    status_changed = pyqtSignal(bool, str) # is_running, message
    
    def __init__(self, game_client=None):
        super().__init__()
        self.thread = None
        self.game_client = game_client
        self.log_handler = QtLogHandler(self.log_received)
        
        self.config_manager = ConfigManager()
        self._load_config()
        
        # 如果传入了 game_client，设置给 api_main
        if self.game_client:
            api_main.set_shared_client(self.game_client)
        
    def _load_config(self):
        """加载配置"""
        self.host = self.config_manager.get("api_host", "127.0.0.1")
        self.port = self.config_manager.get("api_port", 8000)
        self.auto_start = self.config_manager.get("api_auto_start", False)
        self.known_hosts = self.config_manager.get("api_known_hosts", ["127.0.0.1", "0.0.0.0"])
        
    def save_config(self, host, port, auto_start):
        """保存配置"""
        self.host = host
        self.port = port
        self.auto_start = auto_start
        
        # 更新已知主机列表
        if host not in self.known_hosts:
            self.known_hosts.append(host)
            
        self.config_manager.set("api_host", host)
        self.config_manager.set("api_port", port)
        self.config_manager.set("api_auto_start", auto_start)
        self.config_manager.set("api_known_hosts", self.known_hosts)
        self.config_manager.save_config()
        
    def restart_service(self):
        """重启 API 服务"""
        if self.is_running():
            self.stop_service()
            # 简单的重启逻辑：停止后立即启动
            # 由于 stop_service 是阻塞等待线程结束的，所以可以直接调用 start
            self.start_service()
        else:
            self.start_service()
        
    def start_service(self):
        """启动 API 服务"""
        if self.is_running():
            self.log_received.emit("API 服务已经在运行中")
            return
            
        # 设置日志捕获
        self._setup_logging()
        
        # 更新共享客户端（以防重新连接后实例变化）
        if self.game_client:
            api_main.set_shared_client(self.game_client)
            
        self.log_received.emit(f"正在启动 API 服务: {self.host}:{self.port}")
        
        # 创建并启动线程
        self.thread = APIThread(api_main.app, self.host, self.port)
        self.thread.started.connect(self._on_started)
        self.thread.finished.connect(self._on_finished)
        self.thread.start()
        
    def stop_service(self):
        """停止 API 服务"""
        if not self.is_running():
            return
            
        self.log_received.emit("正在停止 API 服务...")
        if self.thread:
            self.thread.stop()
            self.thread = None
            
    def _setup_logging(self):
        """设置日志捕获"""
        # 获取相关 logger
        loggers = [
            logging.getLogger("uvicorn"),
            logging.getLogger("uvicorn.error"),
            logging.getLogger("uvicorn.access"),
            logging.getLogger("api_main"),
            logging.getLogger("fastapi")
        ]
        
        for l in loggers:
            # 避免重复添加
            if self.log_handler not in l.handlers:
                l.addHandler(self.log_handler)
            l.setLevel(logging.INFO)
            
    def _on_started(self):
        """服务启动回调"""
        self.service_started.emit()
        self.status_changed.emit(True, f"运行中 ({self.host}:{self.port})")
        self.log_received.emit("API 服务已启动")
        
    def _on_finished(self):
        """服务结束回调"""
        self.service_stopped.emit()
        self.status_changed.emit(False, "已停止")
        self.log_received.emit(f"API 服务已停止")

    def is_running(self):
        return self.thread is not None and self.thread.isRunning()
    
    def open_user_management(self):
        """在浏览器中打开用户管理页面"""
        import webbrowser
        url = f"http://{self.host}:{self.port}/user-management"
        try:
            webbrowser.open(url)
            self.log_received.emit(f"正在打开用户管理页面: {url}")
            return True
        except Exception as e:
            self.log_received.emit(f"打开用户管理页面失败: {e}")
            return False

