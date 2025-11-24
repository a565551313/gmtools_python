#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号操作模块
移植自功能界面.lua - 账号操作部分
"""

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QGroupBox,
)
from .base_module import BaseModule


class AccountModule(BaseModule):
    """账号操作模块"""

    def init_ui(self):
        """初始化账号操作界面"""
        self.setWindowTitle("账号操作")

        # 主布局
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # 角色ID输入
        id_layout = QHBoxLayout()
        self.account_label = QLabel("角色ID:")
        self.account_input = QLineEdit()
        self.account_input.setPlaceholderText("请输入角色ID")
        id_layout.addWidget(self.account_label)
        id_layout.addWidget(self.account_input)
        main_layout.addLayout(id_layout)

        # 账号信息输入 (用于封禁/解封等)
        account_layout = QHBoxLayout()
        self.account_name_label = QLabel("账号:")
        self.account_name_input = QLineEdit()
        self.account_name_input.setPlaceholderText("请输入要操作的账号")
        account_layout.addWidget(self.account_name_label)
        account_layout.addWidget(self.account_name_input)
        main_layout.addLayout(account_layout)

        # 密码修改输入
        pwd_layout = QHBoxLayout()
        self.pwd_label = QLabel("新密码:")
        self.pwd_input = QLineEdit()
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setPlaceholderText("请输入新密码")
        pwd_layout.addWidget(self.pwd_label)
        pwd_layout.addWidget(self.pwd_input)
        main_layout.addLayout(pwd_layout)

        # 坐骑/称谓输入
        mount_layout = QHBoxLayout()
        self.mount_label = QLabel("称谓:")
        self.mount_input = QLineEdit()
        self.mount_input.setPlaceholderText("请输入称谓名称")
        mount_layout.addWidget(self.mount_label)
        mount_layout.addWidget(self.mount_input)
        main_layout.addLayout(mount_layout)

        # 账号操作按钮组
        account_group = QGroupBox("账号操作")
        account_layout = QGridLayout()
        account_group.setLayout(account_layout)

        # 账号操作按钮列表
        self.account_buttons = [
            ("玩家信息", self.on_player_info),
            ("踢出战斗", self.on_kick_battle),
            ("强制下线", self.on_force_offline),
            ("封禁账号", self.on_ban_account),
            ("解封账号", self.on_unban_account),
            ("封禁IP", self.on_ban_ip),
            ("解封IP", self.on_unban_ip),
            ("开通管理", self.on_open_admin),
            ("关闭管理", self.on_close_admin),
        ]

        # 创建按钮 (3列布局)
        for idx, (text, callback) in enumerate(self.account_buttons):
            row = idx // 3
            col = idx % 3
            button = QPushButton(text)
            button.clicked.connect(callback)
            account_layout.addWidget(button, row, col)

        main_layout.addWidget(account_group)

        # 其他操作按钮组
        other_group = QGroupBox("其他操作")
        other_layout = QGridLayout()
        other_group.setLayout(other_layout)

        # 其他操作按钮
        button1 = QPushButton("修改密码")
        button1.clicked.connect(self.on_change_password)
        other_layout.addWidget(button1, 0, 0)

        button2 = QPushButton("给予称谓")
        button2.clicked.connect(self.on_give_title)
        other_layout.addWidget(button2, 0, 1)

        main_layout.addWidget(other_group)

        # 消息显示区域
        self.message_label = QLabel("准备就绪")
        self.message_label.setStyleSheet("color: blue;")
        main_layout.addWidget(self.message_label)

    # ========== 账号操作处理方法 ==========

    def on_player_info(self):
        """获取玩家信息"""
        self._send_account_cmd("玩家信息", "角色ID")

    def on_kick_battle(self):
        """踢出战斗"""
        self._send_account_cmd("踢出战斗", "角色ID")

    def on_force_offline(self):
        """强制下线"""
        self._send_account_cmd("强制下线", "角色ID")

    def on_ban_account(self):
        """封禁账号"""
        self._send_account_cmd("封禁账号", "账号")

    def on_unban_account(self):
        """解封账号"""
        self._send_account_cmd("解封账号", "账号")

    def on_ban_ip(self):
        """封禁IP"""
        self._send_account_cmd("封禁IP", "账号")

    def on_unban_ip(self):
        """解封IP"""
        self._send_account_cmd("解封IP", "账号")

    def on_open_admin(self):
        """开通管理"""
        self._send_account_cmd("开通管理", "账号")

    def on_close_admin(self):
        """关闭管理"""
        self._send_account_cmd("关闭管理", "账号")

    def on_change_password(self):
        """修改密码"""
        account = self.account_name_input.text().strip()
        password = self.pwd_input.text().strip()

        if not account:
            self.show_message("请输入账号", "error")
            return

        if not password:
            self.show_message("请输入新密码", "error")
            return

        success = self.send_command(3, "修改密码", {"账号": account, "密码": password})

        if success:
            self.show_message("已发送修改密码命令", "info")
        else:
            self.show_message("发送命令失败", "error")

    def on_give_title(self):
        """给予称谓"""
        account_id = self.account_input.text().strip()
        title = self.mount_input.text().strip()

        if not account_id:
            self.show_message("请输入角色ID", "error")
            return

        if not title:
            self.show_message("请输入称谓名称", "error")
            return

        success = self.send_command(
            3, "给予称谓", {"玩家id": account_id, "坐骑名称": title}
        )

        if success:
            self.show_message("已发送给予称谓命令", "info")
        else:
            self.show_message("发送命令失败", "error")

    def _send_account_cmd(self, command: str, id_type: str):
        """
        发送账号操作命令

        Args:
            command: 操作类型
            id_type: ID类型 ("角色ID" 或 "账号")
        """
        if id_type == "角色ID":
            value = self.account_input.text().strip()
        else:
            value = self.account_name_input.text().strip()

        if not value:
            self.show_message(f"请输入{id_type}", "error")
            return

        # 根据命令类型选择使用哪个ID
        data_key = "玩家id" if id_type == "角色ID" else "账号"
        data = {data_key: value}

        # 发送命令 (序号=3)
        success = self.send_command(3, command, data)

        if success:
            self.show_message(f"已发送 {command} 命令", "info")
            self.message_label.setText(f"正在执行: {command}")
        else:
            self.show_message("发送命令失败", "error")
