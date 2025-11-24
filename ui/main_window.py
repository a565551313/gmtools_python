#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口 - 功能模块管理
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QStatusBar,
    QMenuBar,
    QMenu,
    QLabel,
    QMessageBox,
    QLineEdit,
    QPushButton,
    QDialog,
)
from PyQt6.QtCore import Qt, pyqtSignal, QMetaObject, Q_ARG, pyqtSlot
from PyQt6.QtGui import QAction, QIcon, QFont

from modules.account_recharge_module import AccountRechargeModule
from modules.game_module import GameModule
from modules.character_module import CharacterModule
from modules.pet_module import PetModule
from modules.gift_module import GiftModule
from modules.equipment_module import EquipmentModule


class MainWindow(QMainWindow):
    """主窗口类"""

    # 信号定义
    logout_signal = pyqtSignal()  # 登出信号

    def __init__(self, client=None, parent=None):
        super().__init__(parent)
        self.client = client  # 网络客户端
        self.current_account = ""  # 当前登录账号
        self.init_ui()  # 初始化界面
        self.setup_menu()  # 设置菜单
        self.setup_status_bar()  # 设置状态栏

    def init_ui(self):
        """初始化主窗口界面"""
        self.setWindowTitle("GMTools Python - 梦江南超级GM工具")
        self.setMinimumSize(900, 650)

        # 创建中央Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建主布局
        main_layout = QVBoxLayout(central_widget)

        # 创建全局玩家ID输入区域
        self.create_global_id_input(main_layout)

        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)

        # 添加功能模块选项卡
        self.create_module_tabs()

    def create_global_id_input(self, parent_layout):
        """创建全局玩家ID输入区域"""
        id_group_widget = QWidget()
        id_group_layout = QHBoxLayout(id_group_widget)
        id_group_layout.setContentsMargins(10, 10, 10, 5)

        # 添加标签
        id_label = QLabel("玩家ID:")
        id_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        id_group_layout.addWidget(id_label)

        # 添加输入框
        self.player_id_input = QLineEdit()
        self.player_id_input.setPlaceholderText("请输入玩家ID（纯数字）")
        self.player_id_input.setMinimumWidth(200)
        self.player_id_input.setMaximumWidth(300)
        id_group_layout.addWidget(self.player_id_input)

        # 添加说明标签
        id_help = QLabel("所有功能共用此ID")
        id_help.setStyleSheet("color: gray; font-size: 9px;")
        id_group_layout.addWidget(id_help)

        id_group_layout.addStretch()

        parent_layout.addWidget(id_group_widget)

    def get_player_id(self) -> str:
        """获取玩家ID"""
        return self.player_id_input.text().strip()

    def validate_player_id(self) -> bool:
        """验证玩家ID"""
        player_id = self.get_player_id()
        if not player_id:
            return False
        if not player_id.isdigit():
            return False
        return True

    def create_module_tabs(self):
        """创建功能模块选项卡"""
        # 账号充值组合模块
        self.account_recharge_module = AccountRechargeModule(self.client)
        self._setup_module(self.account_recharge_module, "账号充值")

        # 游戏管理模块
        self.game_module = GameModule(self.client)
        self._setup_module(self.game_module, "游戏管理")

        # 角色管理模块
        self.character_module = CharacterModule(self.client)
        self._setup_module(self.character_module, "角色管理")

        # 宝宝管理模块
        self.pet_module = PetModule(self.client)
        self._setup_module(self.pet_module, "宝宝管理")

        # 赠送道具模块
        self.gift_module = GiftModule(self.client)
        self._setup_module(self.gift_module, "赠送道具")

        # 定制装备模块
        self.equipment_module = EquipmentModule(self.client)
        self._setup_module(self.equipment_module, "定制装备")

    def _setup_module(self, module, tab_name):
        """
        设置模块UI并添加到标签页

        Args:
            module: 模块实例
            tab_name: 标签页名称
        """
        # 先设置UI，让模块创建自己的布局
        module.setup_ui()
        # 设置主窗口引用
        if hasattr(module, "set_main_window"):
            module.set_main_window(self)
        # 然后添加到标签页，QTabWidget会管理布局
        self.tab_widget.addTab(module, tab_name)
        # 设置客户端
        module.set_client(self.client)

    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 不再自动获取数据，由用户手动操作
        # self.refresh_data()

    def refresh_data(self):
        """
        刷新数据 - 手动获取各种信息
        注意：此方法目前未使用，保留以备将来扩展
        """
        if not self.client:
            print("[主窗口] 客户端未初始化")
            return

        print("[主窗口] 开始手动刷新数据...")
        # 用户可以按需调用此方法，或通过各模块的按钮手动获取数据

    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 操作菜单
        file_menu = menubar.addMenu("操作")

        # 登出动作
        logout_action = QAction("登出", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)

        file_menu.addSeparator()

        # 退出动作
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        # 关于动作
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 账号信息
        self.account_label = QLabel("当前账号: 未登录")
        self.account_label.setFont(QFont("Arial", 9))
        self.status_bar.addWidget(self.account_label)

        # 连接状态
        self.connection_label = QLabel("未连接")
        self.connection_label.setFont(QFont("Arial", 9))
        self.status_bar.addPermanentWidget(self.connection_label)

    def set_client(self, client):
        """设置网络客户端 - 重构后的简化版本"""
        self.client = client

        # 获取所有模块并设置客户端
        module_attrs = [
            "account_recharge_module",
            "game_module",
            "character_module",
            "pet_module",
            "gift_module",
            "equipment_module",
        ]

        for module_attr in module_attrs:
            module = getattr(self, module_attr, None)
            if module:
                module.set_client(client)

        # 设置全局消息处理函数
        if self.client:
            self.client.on_receive = self.handle_global_receive

    def set_account(self, account: str):
        """设置当前登录账号"""
        self.current_account = account
        self.account_label.setText(f"当前账号: {account}")

        # 在所有模块中设置当前账号，供发送命令时使用
        for i in range(self.tab_widget.count()):
            module = self.tab_widget.widget(i)
            if module and hasattr(module, "_current_account"):
                module._current_account = account

    def handle_global_receive(self, data: dict):
        """
        全局接收消息处理函数
        根据序号决定处理方式：
        - 序号=7：显示信息框
        - 其他序号：添加到游戏管理模块的操作日志

        Args:
            data: 接收到的数据字典，包含seq_no、content等字段
        """
        if not data:
            return

        seq_no = data.get("seq_no")
        content = data.get("content", "")

        if seq_no is None:
            return

        print(f"[全局处理] 收到序号: {seq_no}, 内容: {content}")

        # 将UI操作切换到GUI线程执行
        if seq_no == 7:
            # 序号=7：显示信息框提示
            QMetaObject.invokeMethod(
                self,
                "show_info_dialog",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(str, content),
            )
        else:
            # 其他序号：添加到游戏管理模块的操作日志
            QMetaObject.invokeMethod(
                self,
                "add_operation_log",
                Qt.ConnectionType.QueuedConnection,
                Q_ARG(int, seq_no),
                Q_ARG(str, content),
            )

    @pyqtSlot(str)
    def show_info_dialog(self, content: str):
        """
        在GUI线程中显示信息框

        Args:
            content: 要显示的内容
        """
        print(f"[信息框] 准备显示: {content}")
        try:
            try:
                from ui.discord_messagebox import DiscordMessageBox

                result = DiscordMessageBox.show_info(self, "服务器消息", content)
                print(f"[信息框] 用户已关闭信息框 (结果: {result})")
            except ImportError:
                result = QMessageBox.information(self, "服务器消息", content)
                print(f"[信息框] 用户已关闭信息框 (结果: {result})")
        except Exception as e:
            print(f"[信息框] 显示失败: {e}")
            import traceback

            traceback.print_exc()

    @pyqtSlot(int, str)
    def add_operation_log(self, seq_no: int, content: str):
        """
        在GUI线程中添加操作日志

        Args:
            seq_no: 序号
            content: 内容
        """
        print(f"[日志] 准备添加: 序号={seq_no}, 内容={content}")
        try:
            if hasattr(self, "game_module") and self.game_module:
                # 使用游戏管理模块的add_log方法添加日志
                if hasattr(self.game_module, "add_log"):
                    self.game_module.add_log(f"[序号{seq_no}] {content}")
                    print(f"[日志] 已添加到操作日志")
                else:
                    print(f"[警告] 游戏管理模块没有add_log方法")
            else:
                print(f"[警告] 游戏管理模块未初始化")
        except Exception as e:
            print(f"[日志] 添加失败: {e}")
            import traceback

            traceback.print_exc()

    def update_connection_status(self, connected: bool):
        """更新连接状态"""
        if connected:
            self.connection_label.setText("已连接")
            self.connection_label.setStyleSheet("color: green;")
        else:
            self.connection_label.setText("未连接")
            self.connection_label.setStyleSheet("color: red;")

    def send_command(self, seq_no: int, command: str, data: dict = None) -> bool:
        """
        发送命令到服务器

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

        # 格式化为Lua代码字符串
        content = f'do local ret={{["文本"]="{command}"'
        for key, value in data.items():
            content += f',["{key}"]="{value}"'
        content += "} return ret end"

        return self.client.send(seq_no, content, "")

    def logout(self):
        """登出操作"""
        try:
            from ui.discord_messagebox import DiscordMessageBox

            reply = DiscordMessageBox.show_warning(
                self, "确认登出", "确定要登出吗？", DiscordMessageBox.BUTTON_YES_NO
            )
            if reply == QDialog.DialogCode.Accepted:
                self.logout_signal.emit()
                self.close()
        except ImportError:
            reply = QMessageBox.question(
                self,
                "确认登出",
                "确定要登出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.logout_signal.emit()
                self.close()

    def show_about(self):
        """显示关于对话框"""
        about_content = (
            "<h3>GMTools Python 移植版</h3>"
            "<p>版本: 1.0</p>"
            "<p>移植自: 梦江南超级GM工具 Lua版</p>"
            "<p>功能: 充值、账号管理、游戏管理</p>"
            "<p>技术: Python + PyQt6 + MessagePack</p>"
        )

        try:
            from ui.discord_messagebox import DiscordMessageBox

            DiscordMessageBox.show_info(
                self,
                "关于 GMTools Python",
                about_content.replace("<", "&lt;").replace(">", "&gt;"),
            )
        except ImportError:
            QMessageBox.about(self, "关于 GMTools Python", about_content)

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 如果客户端存在，先断开连接
        if self.client:
            self.client.disconnect()

        event.accept()
