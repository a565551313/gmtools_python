#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
功能模块基类
所有GM功能模块继承此基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Tuple
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QMessageBox,
)
from PyQt6.QtGui import QFont


class BaseModuleMeta(type(QWidget), type(ABC)):
    """元类解决QWidget和ABC的冲突"""

    pass


class BaseModule(QWidget, ABC, metaclass=BaseModuleMeta):
    """功能模块基类"""

    def __init__(self, client=None, parent=None):
        super().__init__(parent)
        self.client = client  # 网络客户端
        self.account_id = ""  # 当前选中的角色ID
        self._current_account = ""  # 当前登录账号
        # 移除自动调用 init_ui()，改为手动调用 setup_ui()

    @abstractmethod
    def init_ui(self):
        """初始化界面 - 子类实现"""
        pass

    def setup_ui(self):
        """设置UI - 在模块添加到父窗口后调用"""
        self.init_ui()

    def set_client(self, client):
        """设置网络客户端"""
        self.client = client

    def set_account_id(self, account_id: str):
        """设置当前角色ID"""
        self.account_id = account_id

    def _format_lua_value(self, key: str, value: Any) -> str:
        """格式化单个键值对为Lua格式

        Args:
            key: 数据键名
            value: 数据值

        Returns:
            str: Lua格式的键值对字符串
        """
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
        else:
            return f',["{key}"]="{value}"'

    def _build_lua_command(self, command: str, data: Dict[str, Any]) -> str:
        """构建Lua命令字符串

        Args:
            command: 命令名称
            data: 命令数据

        Returns:
            str: Lua命令字符串
        """
        content = f'do local ret={{["文本"]="{command}"'
        for key, value in data.items():
            content += self._format_lua_value(key, value)
        content += "} return ret end"
        return content

    def send_command(
        self, seq_no: int, command: str, data: Dict[str, Any] = None
    ) -> bool:
        """发送命令到服务器 - 重构后的简化版本

        Args:
            seq_no: 消息序号
            command: 命令名称
            data: 命令数据

        Returns:
            bool: 发送是否成功
        """
        if not self.client:
            print("[错误] 未设置网络客户端")
            return False

        if data is None:
            data = {}

        content = self._build_lua_command(command, data)

        # 区别处理：序号=1（登录）不需要传递账号，其他序号需要
        # 注意：seq_no=1的情况在login_window中单独处理
        current_account = getattr(self, "_current_account", "")
        return self.client.send(seq_no, content, current_account)

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
                # 列表或元组，转为字符串（不推荐使用）
                parts.append(f'{key_str}="{str(value)}"')
            else:
                # 字符串类型加引号
                parts.append(f'{key_str}="{value}"')
        return ','.join(parts)

    def show_message(self, message: str, message_type: str = "info"):
        """
        显示消息

        将Python字典转换为Lua表格式

        Args:
            data: Python字典

        Returns:
            str: Lua表格式的字符串，例如：["key1"]="value1",["key2"]="value2"
        """
        parts = []
        for key, value in data.items():
            if isinstance(value, dict):
                # 嵌套字典，递归处理
                parts.append(f'["{key}"]={{{self._dict_to_lua_table(value)}}}')
            elif isinstance(value, (list, tuple)):
                # 列表或元组，转为字符串
                parts.append(f'["{key}"]="{str(value)}"')
            else:
                parts.append(f'["{key}"]="{value}"')
        return ','.join(parts)

    def show_message(self, message: str, message_type: str = "info"):
        """
        显示消息

        Args:
            message: 消息内容
            message_type: 消息类型 (info/success/error/warning)
        """
        from PyQt6.QtCore import QTimer

        # 标题映射
        title_map = {
            "info": "提示",
            "success": "成功",
            "warning": "警告",
            "error": "错误",
        }

        title = title_map.get(message_type, "提示")

        # 消息类型映射到DiscordMessageBox类型
        msg_type_map = {
            "info": "info",
            "success": "success",
            "warning": "warning",
            "error": "error",
        }

        discord_msg_type = msg_type_map.get(message_type, "info")

        def show_dialog():
            try:
                from ui.discord_messagebox import DiscordMessageBox

                if message_type == "error":
                    DiscordMessageBox.show_error(self, title, message)
                elif message_type == "warning":
                    DiscordMessageBox.show_warning(self, title, message)
                elif message_type == "success":
                    DiscordMessageBox.show_success(self, title, message)
                else:  # info
                    DiscordMessageBox.show_info(self, title, message)

            except ImportError:
                # 如果DiscordMessageBox不可用，回退到原来的QMessageBox
                QMessageBox(self).information(self, title, message)

        # 确保在主线程中显示对话框
        QTimer.singleShot(0, show_dialog)

    def show_error_message(self, message: str):
        """显示错误信息"""
        self.show_message(message, "error")


class FormField:
    """表单字段辅助类"""

    @staticmethod
    def create_input(
        label_text: str, default: str = "", width: int = 150
    ) -> Tuple[QLabel, QLineEdit]:
        """创建输入框"""
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setText(default)
        input_field.setFixedWidth(width)
        return label, input_field

    @staticmethod
    def create_button(
        text: str, callback: Callable = None, width: int = 100
    ) -> QPushButton:
        """创建按钮"""
        button = QPushButton(text)
        button.setFixedWidth(width)
        if callback:
            button.clicked.connect(callback)
        return button

    @staticmethod
    def create_text_area(
        label_text: str, height: int = 100
    ) -> Tuple[QLabel, QTextEdit]:
        """创建文本区域"""
        label = QLabel(label_text)
        text_area = QTextEdit()
        text_area.setFixedHeight(height)
        return label, text_area


class ButtonGroup:
    """按钮组辅助类"""

    def __init__(self, title: str = "", columns: int = 4):
        self.title = title
        self.columns = columns
        self.buttons = []
        self.callbacks = {}

    def add_button(self, text: str, callback: Callable) -> QPushButton:
        """添加按钮"""
        button = FormField.create_button(text, callback)
        self.buttons.append((text, button))
        self.callbacks[text] = callback
        return button

    def create_layout(self) -> QVBoxLayout:
        """创建布局"""
        layout = QVBoxLayout()

        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            layout.addWidget(title_label)

        # 创建按钮网格
        grid_layout = QGridLayout()
        for idx, (text, button) in enumerate(self.buttons):
            row = idx // self.columns
            col = idx % self.columns
            grid_layout.addWidget(button, row, col)

        layout.addLayout(grid_layout)
        return layout
