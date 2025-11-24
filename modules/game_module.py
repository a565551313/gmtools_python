#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏管理模块 - 序号=6 Discord风格
实现49项游戏控制功能
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFrame,
    QGridLayout,
    QTabWidget,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .base_module import BaseModule


class DiscordButton(QPushButton):
    """Discord风格按钮"""

    def __init__(self, text, color_type="primary", parent=None):
        super().__init__(text, parent)
        self.color_type = color_type
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
        self.setMinimumHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def update_style(self):
        if self.color_type == "primary":
            bg, hover, pressed = "#5865F2", "#4752C4", "#3C45A5"
        elif self.color_type == "success":
            bg, hover, pressed = "#3BA55C", "#2D7D46", "#276D3D"
        elif self.color_type == "danger":
            bg, hover, pressed = "#ED4245", "#C03537", "#A22C2E"
        else:  # secondary
            bg, hover, pressed = "#4F545C", "#5D6269", "#484C54"

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: 500;
            }}
            QPushButton:hover {{ background-color: {hover}; }}
            QPushButton:pressed {{ background-color: {pressed}; }}
        """
        )


class GridButton(QPushButton):
    """用于活动网格的紧凑型按钮"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Microsoft YaHei", 9))
        self.setMinimumHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            """
            GridButton {
                background-color: #40444B;
                color: #DCDDDE;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-weight: 500;
            }
            GridButton:hover {
                background-color: #5865F2;
                color: white;
            }
            GridButton:pressed {
                background-color: #4752C4;
            }
        """
        )


class DiscordLineEdit(QLineEdit):
    """Discord风格输入框"""

    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setMinimumHeight(32)
        self.setStyleSheet(
            """
            QLineEdit {
                background-color: #1E1F22;
                color: #F2F3F5;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 10px;
            }
            QLineEdit:hover { border: 1px solid #3F4147; }
            QLineEdit:focus { border: 1px solid #5865F2; }
            QLineEdit::placeholder { color: #5C5F66; }
        """
        )


class SectionCard(QFrame):
    """区域卡片"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #2B2D31;
                border-radius: 8px;
            }
        """
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        if title:
            title_label = QLabel(title)
            title_label.setStyleSheet(
                """
                QLabel {
                    color: #F2F3F5;
                    font-size: 16px;
                    font-weight: 700;
                }
            """
            )
            layout.addWidget(title_label)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        layout.addLayout(self.content_layout)


class GameModule(BaseModule):
    """游戏管理模块 - Discord风格重新设计"""

    def __init__(self, client=None):
        super().__init__(client)

    def init_ui(self):
        """初始化界面"""
        self.setStyleSheet("background-color: #202225; border-radius: 4px;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ========== 顶部标题栏 ==========
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(16)

        title = QLabel("⚙️ 游戏管理中心")
        title.setStyleSheet(
            """
            QLabel {
                color: #F2F3F5;
                font-size: 24px;
                font-weight: 700;
            }
        """
        )
        title_layout.addWidget(title)

        subtitle = QLabel("控制游戏全局设置、活动和公告")
        subtitle.setStyleSheet(
            """
            QLabel {
                color: #949BA4;
                font-size: 14px;
            }
        """
        )
        title_layout.addWidget(subtitle)
        title_layout.addStretch()

        main_layout.addWidget(title_bar)

        # 创建两列布局
        columns = QHBoxLayout()
        columns.setSpacing(20)

        # 左列：快捷操作
        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        left_col.addWidget(self._create_broadcast_card())
        left_col.addWidget(self._create_settings_card())
        left_col.addWidget(self._create_log_card())
        left_col.setStretch(2, 1)  # 让日志区域可伸缩

        # 右列：活动控制
        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        right_col.addWidget(self._create_activity_card())

        columns.addLayout(left_col, 1)
        columns.addLayout(right_col, 2)  # 右列更宽

        main_layout.addLayout(columns)

    def _create_broadcast_card(self):
        """创建广播公告卡片"""
        card = SectionCard("📢 广播 & 公告")

        self.announcement_input = DiscordLineEdit("输入广播或公告内容")
        card.content_layout.addWidget(self.announcement_input)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        send_broadcast_btn = DiscordButton("发送广播", "primary")
        send_broadcast_btn.clicked.connect(self.send_broadcast)
        btn_row.addWidget(send_broadcast_btn)

        send_announcement_btn = DiscordButton("发送公告", "primary")
        send_announcement_btn.clicked.connect(self.send_announcement)
        btn_row.addWidget(send_announcement_btn)

        card.content_layout.addLayout(btn_row)
        return card

    def _create_settings_card(self):
        """创建全局数值设置卡片"""
        card = SectionCard("🔧 全局数值设置")

        input_row = QHBoxLayout()
        input_row.setSpacing(10)

        rate_label = QLabel("数值:")
        rate_label.setStyleSheet("color: #B5BAC1; font-size: 13px; font-weight: 600;")
        input_row.addWidget(rate_label)

        self.rate_input = DiscordLineEdit("输入数值")
        self.rate_input.setMaximumWidth(120)
        input_row.addWidget(self.rate_input)
        input_row.addStretch()

        card.content_layout.addLayout(input_row)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        exp_rate_btn = DiscordButton("经验倍率", "secondary")
        exp_rate_btn.clicked.connect(self.set_exp_rate)
        btn_row.addWidget(exp_rate_btn)

        difficulty_btn = DiscordButton("游戏难度", "secondary")
        difficulty_btn.clicked.connect(self.set_difficulty)
        btn_row.addWidget(difficulty_btn)

        level_cap_btn = DiscordButton("等级上限", "secondary")
        level_cap_btn.clicked.connect(self.set_level_cap)
        btn_row.addWidget(level_cap_btn)

        card.content_layout.addLayout(btn_row)
        return card

    def _create_log_card(self):
        """创建日志卡片"""
        card = SectionCard("📝 操作日志")

        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #1E1F22;
                color: #B5BAC1;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """
        )
        card.content_layout.addWidget(self.log_display)
        return card

    def _create_activity_card(self):
        """创建活动开关控制卡片"""
        card = SectionCard("🎮 活动开关控制")

        tab_widget = QTabWidget()
        tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                background-color: #2B2D31;
                border: none;
                padding: 10px 0 0 0;
            }
            QTabBar::tab {
                background-color: #2F3136;
                color: #8E9297;
                padding: 8px 16px;
                margin-right: 4px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #40444B;
                color: #FFFFFF;
            }
            QTabBar::tab:hover:!selected {
                background-color: #32353B;
                color: #DCDDDE;
            }
        """
        )

        # 分类活动按钮
        categories = {
            "常规活动": [
                "四墓灵鼠",
                "天降灵猴",
                "皇宫飞贼",
                "门派入侵",
                "长安保卫",
                "新春活动",
                "嘉年华",
                "天降辰星",
                "彩虹争霸",
                "糖果派对",
                "知了先锋",
                "小小盲僧",
            ],
            "BOSS & 挑战": [
                "刷出妖魔",
                "二八星宿",
                "天庭叛逆",
                "刷出星宿",
                "刷出星官",
                "刷出天罡",
                "刷出地煞",
                "圣兽残魂",
                "刷出知了",
                "世界挑战",
                "混世魔王",
                "刷出桐人",
                "魔化桐人",
                "创世佛屠",
                "善恶如来",
            ],
            "系统开关": [
                "开启异界",
                "开启经宝",
                "开启万象",
                "开启生肖",
                "门派开关",
                "宝藏开关",
                "镖王开关",
                "游泳开关",
                "开启病毒",
            ],
            "PVP 对战": [
                "开启帮战",
                "结束帮战",
                "开启比武",
                "比武入场",
                "结束比武",
                "开启剑会",
                "结束剑会",
            ],
            "系统维护": ["假人走动", "假人摆摊", "假人聊天", "保存数据", "关闭游戏"],
        }

        all_buttons = [btn for sublist in categories.values() for btn in sublist]

        for category_name, buttons in categories.items():
            tab = QWidget()
            tab_layout = QGridLayout(tab)
            tab_layout.setSpacing(8)

            for i, btn_text in enumerate(buttons):
                row, col = divmod(i, 4)  # 4列
                btn = GridButton(btn_text)
                btn.setToolTip(f"序号={all_buttons.index(btn_text) + 1}: {btn_text}")
                btn.clicked.connect(
                    lambda checked, t=btn_text: self.trigger_activity(t)
                )
                tab_layout.addWidget(btn, row, col)

            tab_layout.setRowStretch(tab_layout.rowCount(), 1)
            tab_widget.addTab(tab, category_name)

        card.content_layout.addWidget(tab_widget)
        return card

    # ========== 业务逻辑 ==========
    def send_broadcast(self):
        """发送广播"""
        content = self.announcement_input.text().strip()
        if not content:
            self.show_error("请输入广播内容")
            return
        self.send_command(6, "发送广播", {"数据": content})
        self.add_log(f"已发送广播: {content}")

    def send_announcement(self):
        """发送公告"""
        content = self.announcement_input.text().strip()
        if not content:
            self.show_error("请输入公告内容")
            return
        self.send_command(6, "发送公告", {"数据": content})
        self.add_log(f"已发送公告: {content}")

    def set_exp_rate(self):
        """设置经验倍率"""
        rate = self.rate_input.text().strip()
        if not rate or not rate.isdigit():
            self.show_error("请输入有效的数值倍率")
            return
        self.send_command(6, "经验倍率", {"数据": rate})
        self.add_log(f"已设置经验倍率: {rate}")

    def set_difficulty(self):
        """设置游戏难度"""
        rate = self.rate_input.text().strip()
        if not rate or not rate.isdigit():
            self.show_error("请输入有效的数值")
            return
        self.send_command(6, "游戏难度", {"数据": rate})
        self.add_log(f"已设置游戏难度: {rate}")

    def set_level_cap(self):
        """设置等级上限"""
        rate = self.rate_input.text().strip()
        if not rate or not rate.isdigit():
            self.show_error("请输入有效的数值")
            return
        self.send_command(6, "等级上限", {"数据": rate})
        self.add_log(f"已设置等级上限: {rate}")

    def trigger_activity(self, activity_name: str):
        """触发活动"""
        self.send_command(6, activity_name)
        self.add_log(f"已触发: {activity_name}")

    def add_log(self, message: str):
        """添加日志"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.append(f"[{timestamp}] {message}")

    def show_error(self, message: str):
        """显示错误信息框"""
        self.show_error_message(message)
