#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色管理模块 - 序号=7 Discord风格（自然高度版）
实现角色修炼、生活技能、强化技能、召唤兽修炼管理
- 无滚动，内容全部显示
- 每个卡片保持自然高度，不强制拉伸
"""

from typing import Tuple, List
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QGridLayout,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from .base_module import BaseModule


class DiscordButton(QPushButton):
    """Discord风格按钮"""

    def __init__(self, text, color_type="primary", parent=None):
        super().__init__(text, parent)
        self.color_type = color_type
        self.setFont(QFont("Segoe UI", 10))
        self.setMinimumHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_style()

    def update_style(self):
        """更新样式"""
        if self.color_type == "primary":
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #5865F2;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #4752C4;
                }
                QPushButton:pressed {
                    background-color: #3C45A5;
                }
            """
            )
        elif self.color_type == "success":
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #3BA55C;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #2D7D46;
                }
                QPushButton:pressed {
                    background-color: #276D3D;
                }
            """
            )
        elif self.color_type == "secondary":
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #4F545C;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #5D6269;
                }
                QPushButton:pressed {
                    background-color: #484C54;
                }
            """
            )


class DiscordCard(QFrame):
    """Discord风格卡片"""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(
            """
            QFrame {
                background-color: #2B2D31;
                border: 1px solid #1E1F22;
                border-radius: 6px;
                padding: 10px;
            }
        """
        )

        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(8)
        self.layout.setContentsMargins(0, 0, 0, 0)

        if self.title:
            title_label = QLabel(self.title)
            title_label.setStyleSheet(
                """
                QLabel {
                    color: #F2F3F5;
                    font-size: 14px;
                    font-weight: 600;
                    padding-bottom: 4px;
                }
            """
            )
            self.layout.addWidget(title_label)

            # 添加分割线
            line = QFrame()
            line.setFrameShape(QFrame.Shape.HLine)
            line.setStyleSheet("QFrame { background-color: #3F4147; max-height: 1px; }")
            self.layout.addWidget(line)


class DiscordInput(QWidget):
    """Discord风格的标签+输入框组合"""

    def __init__(self, label_text="", placeholder="0", width=85, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QWidget { border: none; background: transparent; }")
        self.init_ui(label_text, placeholder, width)

    def init_ui(self, label_text, placeholder, width):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # 标签
        self.label = QLabel(label_text)
        self.label.setMinimumWidth(75)
        self.label.setStyleSheet(
            """
            QLabel {
                color: #B5BAC1;
                font-size: 12px;
                font-weight: 500;
                border: none;
                background: transparent;
                padding: 0px;
            }
        """
        )

        # 输入框
        self.input = QLineEdit()
        self.input.setPlaceholderText(placeholder)
        self.input.setMaximumWidth(width)
        self.input.setStyleSheet(
            """
            QLineEdit {
                background-color: #1E1F22;
                color: #F2F3F5;
                border: 1px solid transparent;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 12px;
                min-height: 24px;
            }
            QLineEdit:hover {
                background-color: #1E1F22;
                border: 1px solid #3F4147;
            }
            QLineEdit:focus {
                background-color: #1E1F22;
                border: 1px solid #5865F2;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #5C5F66;
            }
        """
        )

        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addStretch()

    def text(self):
        return self.input.text()

    def setText(self, text):
        self.input.setText(text)

    def clear(self):
        self.input.clear()


class CharacterModule(BaseModule):
    """角色管理模块 - Discord风格（自然高度版）"""

    def __init__(self, client=None):
        super().__init__(client)
        self.main_window = None
        self.character_data = {}

    def set_main_window(self, main_window):
        """设置主窗口引用"""
        self.main_window = main_window

    def get_character_id(self) -> str:
        """从主窗口获取玩家ID"""
        if self.main_window and hasattr(self.main_window, "get_player_id"):
            return self.main_window.get_player_id()
        else:
            return ""

    def validate_character_id(self) -> bool:
        """验证角色ID"""
        if self.main_window and hasattr(self.main_window, "validate_player_id"):
            return self.main_window.validate_player_id()
        else:
            return False

    def init_ui(self):
        """初始化界面 - 自然高度版本"""
        # 设置背景色
        self.setStyleSheet("background-color: #202225; border-radius: 4px;")

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # 内容容器
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)

        # 创建两列布局容器
        columns_widget = QWidget()
        columns_layout = QHBoxLayout(columns_widget)
        columns_layout.setSpacing(12)
        columns_layout.setContentsMargins(0, 0, 0, 0)
        columns_layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # 顶部对齐，不拉伸

        # ========== 左列 ==========
        left_widget = QWidget()
        left_column = QVBoxLayout(left_widget)
        left_column.setSpacing(12)
        left_column.setContentsMargins(0, 0, 0, 0)
        left_column.setAlignment(Qt.AlignmentFlag.AlignTop)  # 顶部对齐

        # 角色/召唤兽修炼卡片（合并）
        cultivation_card = DiscordCard("🛡️ 角色/召唤兽修炼")
        cultivation_layout = QVBoxLayout()
        cultivation_layout.setSpacing(8)

        # 角色修炼部分
        cult_content = QGridLayout()
        cult_content.setSpacing(6)
        cult_content.setHorizontalSpacing(10)

        self.cultivation_fields = ["攻击修炼", "法术修炼", "防御修炼", "抗法修炼"]
        self.cultivation_inputs = {}

        for i, field in enumerate(self.cultivation_fields):
            input_widget = DiscordInput(field, "0", width=85)
            row = i // 3
            col = i % 3
            cult_content.addWidget(input_widget, row, col)
            self.cultivation_inputs[field] = input_widget

        cultivation_layout.addLayout(cult_content)

        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet(
            """
            QFrame { 
                background-color: #3F4147; 
                max-height: 1px;
                margin: 6px 0;
            }
        """
        )
        cultivation_layout.addWidget(separator)

        # 召唤兽修炼部分
        pet_content = QGridLayout()
        pet_content.setSpacing(6)
        pet_content.setHorizontalSpacing(10)

        self.pet_cultivation_fields = [
            "攻击控制力",
            "法术控制力",
            "防御控制力",
            "抗法控制力",
            "玩家等级",
        ]
        self.pet_cultivation_inputs = {}

        # 4个控制力字段在前两行
        control_fields = ["攻击控制力", "法术控制力", "防御控制力", "抗法控制力"]
        for i, field in enumerate(control_fields):
            input_widget = DiscordInput(field, "0", width=85)
            row = i // 2  # 每行2个
            col = i % 2
            pet_content.addWidget(input_widget, row, col)
            self.pet_cultivation_inputs[field] = input_widget

        # 玩家等级字段在第三行单独一行居中
        player_level_widget = DiscordInput("玩家等级", "0", width=85)
        pet_content.addWidget(player_level_widget, 2, 0, 1, 2)  # 占两列居中
        self.pet_cultivation_inputs["玩家等级"] = player_level_widget

        cultivation_layout.addLayout(pet_content)
        cultivation_card.layout.addLayout(cultivation_layout)
        left_column.addWidget(cultivation_card)

        # 生活技能卡片
        life_card = DiscordCard("🎯 生活技能")
        life_content = QGridLayout()
        life_content.setSpacing(6)
        life_content.setHorizontalSpacing(10)

        self.life_fields = [
            "强身术",
            "冥想",
            "强壮",
            "暗器技巧",
            "中药医理",
            "烹饪技巧",
            "打造技巧",
            "裁缝技巧",
            "炼金术",
            "淬灵之术",
            "养生之道",
            "健身术",
        ]
        self.life_inputs = {}

        for i, field in enumerate(self.life_fields):
            input_widget = DiscordInput(field, "0", width=85)
            row = i // 3
            col = i % 3
            life_content.addWidget(input_widget, row, col)
            self.life_inputs[field] = input_widget

        life_card.layout.addLayout(life_content)
        left_column.addWidget(life_card)

        # ========== 右列 ==========
        right_widget = QWidget()
        right_column = QVBoxLayout(right_widget)
        right_column.setSpacing(12)
        right_column.setContentsMargins(0, 0, 0, 0)
        right_column.setAlignment(Qt.AlignmentFlag.AlignTop)  # 顶部对齐

        # 强化技能卡片
        enhance_card = DiscordCard("💪 强化技能")
        enhance_content = QGridLayout()
        enhance_content.setSpacing(6)
        enhance_content.setHorizontalSpacing(10)

        self.enhancement_fields = [
            "人物伤害",
            "人物防御",
            "人物气血",
            "人物法术",
            "人物速度",
            "人物固伤",
            "人物治疗",
            "宠物伤害",
            "宠物防御",
            "宠物气血",
            "宠物灵力",
            "宠物速度",
        ]
        self.enhancement_inputs = {}

        for i, field in enumerate(self.enhancement_fields):
            input_widget = DiscordInput(field, "0", width=85)
            row = i // 3
            col = i % 3
            enhance_content.addWidget(input_widget, row, col)
            self.enhancement_inputs[field] = input_widget

        enhance_card.layout.addLayout(enhance_content)
        right_column.addWidget(enhance_card)

        # 添加列到主布局
        columns_layout.addWidget(left_widget)
        columns_layout.addWidget(right_widget)

        content_layout.addWidget(columns_widget)

        # 添加内容到主布局
        main_layout.addWidget(content_widget)
        main_layout.addStretch()  # 底部弹性空间

        # 底部操作栏
        action_bar = QWidget()
        action_bar.setStyleSheet(
            """
            QWidget {
                background-color: #2B2D31;
                border-radius: 6px;
                padding: 10px;
            }
        """
        )
        action_layout = QHBoxLayout(action_bar)
        action_layout.setSpacing(10)

        # 操作按钮
        self.get_info_btn = DiscordButton("📥 获取", "secondary")
        self.get_info_btn.clicked.connect(self.get_character_info)

        self.recover_btn = DiscordButton("♻️ 恢复", "secondary")
        self.recover_btn.clicked.connect(self.recover_character_props)

        self.modify_btn = DiscordButton("✅ 修改", "success")
        self.modify_btn.clicked.connect(self.modify_character)

        action_layout.addWidget(self.get_info_btn)
        action_layout.addWidget(self.recover_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.modify_btn)

        main_layout.addWidget(action_bar)

    def get_character_info(self):
        """获取角色信息"""
        char_id = self.get_character_id()
        if not char_id:
            self.show_error("请输入角色ID")
            return
        if not char_id.isdigit():
            self.show_error("角色ID必须为纯数字")
            return

        self.send_command(7, "获取角色信息", {"玩家id": char_id})
        self.add_log(f"已发送获取角色信息请求: {char_id}")

    def recover_character_props(self):
        """恢复角色道具"""
        char_id = self.get_character_id()
        if not char_id:
            self.show_error("请输入角色ID")
            return
        if not char_id.isdigit():
            self.show_error("角色ID必须为纯数字")
            return

        self.send_command(7, "恢复角色道具", {"玩家id": char_id})
        self.add_log(f"已发送恢复角色道具请求: {char_id}")

    def _collect_field_data(
        self, fields: list, inputs: dict, clear_after: bool = True
    ) -> list:
        """
        收集字段数据并进行验证

        Args:
            fields: 字段名称列表
            inputs: 输入控件字典
            clear_after: 是否在收集后清空输入框

        Returns:
            Lua格式的字段数据列表

        Raises:
            ValueError: 当字段值不是纯数字时
        """
        parts = []
        for field in fields:
            value = inputs[field].text().strip()
            if value:
                if not value.isdigit():
                    raise ValueError(f"{field}必须为纯数字")
                parts.append(f'["{field}"]="{value}"')
                if clear_after:
                    inputs[field].clear()
        return parts

    def _get_field_groups(self) -> List[Tuple[str, List, dict]]:
        """获取字段组定义

        Returns:
            list: 字段组列表，每个元素为(组名, 字段列表, 输入框字典)
        """
        return [
            ("角色修炼", self.cultivation_fields, self.cultivation_inputs),
            ("角色生活", self.life_fields, self.life_inputs),
            ("角色强化", self.enhancement_fields, self.enhancement_inputs),
            (
                "召唤兽修炼",
                self.pet_cultivation_fields,
                self.pet_cultivation_inputs,
            ),
        ]

    def _collect_modification_data(self) -> str:
        """收集所有修改数据并构建Lua字符串

        Returns:
            str: Lua格式的修改数据字符串

        Raises:
            ValueError: 当没有输入任何数据时
        """
        field_groups = self._get_field_groups()

        modify_parts = []
        for group_name, fields, inputs in field_groups:
            parts = self._collect_field_data(fields, inputs)
            if parts:
                modify_parts.append(f'["{group_name}"]={{{",".join(parts)}}}')

        if not modify_parts:
            raise ValueError("没有输入任何修改数据")

        return "{" + ",".join(modify_parts) + "}"

    def _validate_character_id(self) -> str:
        """验证角色ID

        Returns:
            str: 有效的角色ID

        Raises:
            ValueError: 当角色ID无效时
        """
        char_id = self.get_character_id()
        if not char_id:
            raise ValueError("请输入角色ID")
        if not char_id.isdigit():
            raise ValueError("角色ID必须为纯数字")
        return char_id

    def modify_character(self):
        """修改角色属性 - 重构后的简化版本"""
        try:
            char_id = self._validate_character_id()
            modify_data_str = self._collect_modification_data()

            self.send_command(
                7, "确定修改", {"玩家id": char_id, "修改数据": modify_data_str}
            )
            self.add_log(f"已发送角色修改请求: {char_id}")

        except ValueError as e:
            self.show_error(str(e))

    def add_log(self, message: str):
        """添加日志"""
        print(f"[角色管理] {message}")

    def show_error(self, message: str):
        """显示错误信息框"""
        self.show_error_message(message)

    def set_client(self, client):
        """设置网络客户端"""
        super().set_client(client)
