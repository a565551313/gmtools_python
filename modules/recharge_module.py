#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
充值操作模块
移植自功能界面.lua - 充值操作部分
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


class RechargeModule(BaseModule):
    """充值操作模块"""

    def init_ui(self):
        """初始化充值操作界面"""
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

        # 充值金额输入
        amount_layout = QHBoxLayout()
        self.amount_label = QLabel("充值金额:")
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("请输入充值金额")
        amount_layout.addWidget(self.amount_label)
        amount_layout.addWidget(self.amount_input)
        main_layout.addLayout(amount_layout)

        # 充值操作按钮组
        recharge_group = QGroupBox("充值操作")
        recharge_layout = QGridLayout()
        recharge_group.setLayout(recharge_layout)

        # 充值按钮列表
        self.recharge_buttons = [
            ("充值仙玉", self.on_recharge_xy),
            ("充值点卡", self.on_recharge_dk),
            ("充值银子", self.on_recharge_yz),
            ("充值储备", self.on_recharge_cc),
            ("充值经验", self.on_recharge_jy),
            ("充值累充", self.on_recharge_lc),
            ("充值帮贡", self.on_recharge_bg),
            ("充值门贡", self.on_recharge_mg),
            ("打造熟练", self.on_recharge_dz),
            ("裁缝熟练", self.on_recharge_cf),
            ("炼金熟练", self.on_recharge_lj),
            ("淬灵熟练", self.on_recharge_cl),
            ("活跃积分", self.on_recharge_hy),
            ("比武积分", self.on_recharge_bi),
            ("充值记录", self.on_recharge_record),
        ]

        # 创建按钮 (4列布局)
        for idx, (text, callback) in enumerate(self.recharge_buttons):
            row = idx // 4
            col = idx % 4
            button = QPushButton(text)
            button.clicked.connect(callback)
            recharge_layout.addWidget(button, row, col)

        main_layout.addWidget(recharge_group)

        # 八卦设置按钮组
        bagua_group = QGroupBox("八卦设置")
        bagua_layout = QHBoxLayout()
        bagua_group.setLayout(bagua_layout)

        # 8个卦象按钮
        self.bagua_buttons = [
            ("乾", self.on_bagua_qian),
            ("巽", self.on_bagua_xun),
            ("坎", self.on_bagua_kan),
            ("艮", self.on_bagua_gen),
            ("坤", self.on_bagua_kun),
            ("震", self.on_bagua_zhen),
            ("离", self.on_bagua_li),
            ("兑", self.on_bagua_dui),
        ]

        for text, callback in self.bagua_buttons:
            button = QPushButton(text)
            button.setFixedWidth(50)
            button.clicked.connect(callback)
            bagua_layout.addWidget(button)

        main_layout.addWidget(bagua_group)
        bagua_layout.addStretch()

        # 消息显示区域
        self.message_label = QLabel("准备就绪")
        self.message_label.setStyleSheet("color: blue;")
        main_layout.addWidget(self.message_label)

    # ========== 充值操作处理方法 ==========

    def on_recharge_xy(self):
        """充值仙玉"""
        self._send_recharge("充值仙玉")

    def on_recharge_dk(self):
        """充值点卡"""
        self._send_recharge("充值点卡")

    def on_recharge_yz(self):
        """充值银子"""
        self._send_recharge("充值银子")

    def on_recharge_cc(self):
        """充值储备"""
        self._send_recharge("充值储备")

    def on_recharge_jy(self):
        """充值经验"""
        self._send_recharge("充值经验")

    def on_recharge_lc(self):
        """充值累充"""
        self._send_recharge("充值累充")

    def on_recharge_bg(self):
        """充值帮贡"""
        self._send_recharge("充值帮贡")

    def on_recharge_mg(self):
        """充值门贡"""
        self._send_recharge("充值门贡")

    def on_recharge_dz(self):
        """打造熟练"""
        self._send_recharge("打造熟练")

    def on_recharge_cf(self):
        """裁缝熟练"""
        self._send_recharge("裁缝熟练")

    def on_recharge_lj(self):
        """炼金熟练"""
        self._send_recharge("炼金熟练")

    def on_recharge_cl(self):
        """淬灵熟练"""
        self._send_recharge("淬灵熟练")

    def on_recharge_hy(self):
        """活跃积分"""
        self._send_recharge("活跃积分")

    def on_recharge_bi(self):
        """比武积分"""
        self._send_recharge("比武积分")

    def on_recharge_record(self):
        """充值记录"""
        account_id = self.account_input.text().strip()

        if not account_id:
            self.show_error("请输入角色ID")
            return

        # 发送充值命令 (序号=2)
        success = self.send_command(
            2, "充值记录", {"玩家id": account_id, "数额": ""}  # 充值记录不需要金额
        )

        if success:
            self.message_label.setText(f"正在执行: 充值记录")
        else:
            self.show_error("发送命令失败")

    # ========== 八卦设置处理方法 ==========

    def on_bagua_qian(self):
        """设置乾卦"""
        self._send_bagua("乾")

    def on_bagua_xun(self):
        """设置巽卦"""
        self._send_bagua("巽")

    def on_bagua_kan(self):
        """设置坎卦"""
        self._send_bagua("坎")

    def on_bagua_gen(self):
        """设置艮卦"""
        self._send_bagua("艮")

    def on_bagua_kun(self):
        """设置坤卦"""
        self._send_bagua("坤")

    def on_bagua_zhen(self):
        """设置震卦"""
        self._send_bagua("震")

    def on_bagua_li(self):
        """设置离卦"""
        self._send_bagua("离")

    def on_bagua_dui(self):
        """设置兑卦"""
        self._send_bagua("兑")

    def _send_bagua(self, bagua_name: str):
        """发送八卦设置"""
        # 发送八卦设置命令 (序号=2)
        success = self.send_command(2, "八卦设置", {"数额": bagua_name})

        if success:
            self.message_label.setText(f"已设置八卦: {bagua_name}")
        else:
            self.show_error("发送八卦设置失败")

    def _send_recharge(self, command: str):
        """
        发送充值命令

        Args:
            command: 充值类型
        """
        account_id = self.account_input.text().strip()
        amount = self.amount_input.text().strip()

        if not account_id:
            self.show_error("请输入角色ID")
            return

        if not amount:
            self.show_error("请输入充值金额")
            return

        # 发送充值命令 (序号=2)
        success = self.send_command(2, command, {"玩家id": account_id, "数额": amount})

        if success:
            self.message_label.setText(f"正在执行: {command}")
        else:
            self.show_error("发送命令失败")

    def show_error(self, message: str):
        """显示错误信息"""
        self.show_error_message(message)
