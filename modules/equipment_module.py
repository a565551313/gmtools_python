#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定制装备模块 - 序号=4,5,8,10 Discord风格
实现装备定制、灵饰定制、宝宝装备定制、定制词条功能

序号说明:
- 4: 装备定制 (6种装备类型: 武器, 衣服, 头盔, 项链, 腰带, 鞋子)
- 5: 灵饰定制 (4种部位: 戒指, 手镯, 佩饰, 耳饰)
- 8: 宝宝装备定制 (3种部位: 护腕, 项圈, 铠甲)
- 10: 定制词条 (4个境界: 优秀, 稀有, 传说, 神话)
"""

from typing import Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFrame,
    QGridLayout,
    QScrollArea,
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


class DiscordComboBox(QComboBox):
    """Discord风格下拉框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont("Microsoft YaHei", 10))
        self.setMinimumHeight(28)
        self.setStyleSheet(
            """
            QComboBox {
                background-color: #202225;
                color: white;
                border: 1px solid #202225;
                border-radius: 4px;
                padding: 2px 6px;
            }
            QComboBox:focus {
                border: 1px solid #5865F2;
            }
            QComboBox QLineEdit {
                background-color: transparent;
                color: white;
                border: none;
                padding: 0;
            }
            QComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: none;
                border-left: 4px solid #72767D;
                border-bottom: 4px solid #72767D;
                margin-right: 4px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background-color: transparent;
            }
            QComboBox QAbstractItemView {
                background-color: #202225;
                color: white;
                border: 1px solid #5865F2;
                selection-background-color: #5865F2;
                selection-color: white;
            }
        """
        )


class CompactInput(QWidget):
    """紧凑型输入组件"""

    def __init__(self, label="", placeholder="", width=100, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        if label:
            lbl = QLabel(label)
            lbl.setStyleSheet(
                """
                QLabel {
                    color: #B5BAC1;
                    font-size: 12px;
                    font-weight: 600;
                }
            """
            )
            layout.addWidget(lbl)

        self.input = DiscordLineEdit(placeholder)
        if width:
            self.input.setMaximumWidth(width)
        layout.addWidget(self.input)

    def text(self):
        return self.input.text()

    def setText(self, text):
        self.input.setText(text)

    def clear(self):
        self.input.clear()


class SectionCard(QFrame):
    """区域卡片"""

    def __init__(self, title="", subtitle="", parent=None):
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
            header = QHBoxLayout()
            header.setSpacing(10)

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
            header.addWidget(title_label)

            if subtitle:
                sub_label = QLabel(subtitle)
                sub_label.setStyleSheet(
                    """
                    QLabel {
                        color: #949BA4;
                        font-size: 12px;
                    }
                """
                )
                header.addWidget(sub_label)

            header.addStretch()
            layout.addLayout(header)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        layout.addLayout(self.content_layout)


class EquipmentModule(BaseModule):
    """定制装备模块 - Discord风格重新设计"""

    def __init__(self, client=None):
        super().__init__(client)
        self.main_window = None

        # 装备类型
        self.equipment_types = ["武器", "衣服", "头盔", "项链", "腰带", "鞋子"]
        self.equipment_fields = [
            "等级",
            "气血",
            "魔法",
            "命中",
            "伤害",
            "防御",
            "速度",
            "灵力",
            "体质",
            "魔力",
            "力量",
            "耐力",
            "敏捷",
            "特效",
            "特效2",
            "特技",
            "制造",
            "专用",
        ]

        # 灵饰
        self.ornament_parts = ["戒指", "手镯", "佩饰", "耳饰"]
        self.ornament_fields = [
            "等级",
            "主属",
            "属性",
            "附加1",
            "附加2",
            "附加3",
            "附加4",
            "数值1",
            "数值2",
            "数值3",
            "数值4",
            "特效",
            "制造",
        ]
        self.ornament_attr_map = {
            "戒指": {
                "主属": ["伤害", "防御"],
                "附加": [
                    "固定伤害",
                    "法术伤害",
                    "伤害",
                    "封印命中等级",
                    "法术暴击等级",
                    "物理暴击等级",
                    "狂暴等级",
                    "穿刺等级",
                    "法术伤害结果",
                    "治疗能力",
                    "速度",
                ],
            },
            "手镯": {
                "主属": ["封印命中等级", "抵抗封印等级"],
                "附加": [
                    "气血回复效果",
                    "气血",
                    "防御",
                    "抗法术暴击等级",
                    "格挡值",
                    "法术防御",
                    "抗物理暴击等级",
                ],
            },
            "佩饰": {
                "主属": ["速度"],
                "附加": [
                    "气血回复效果",
                    "气血",
                    "防御",
                    "抗法术暴击等级",
                    "格挡值",
                    "法术防御",
                    "抗物理暴击等级",
                ],
            },
            "耳饰": {
                "主属": ["法术伤害", "法术防御"],
                "附加": [
                    "固定伤害",
                    "法术伤害",
                    "伤害",
                    "封印命中等级",
                    "法术暴击等级",
                    "物理暴击等级",
                    "狂暴等级",
                    "穿刺等级",
                    "法术伤害结果",
                    "治疗能力",
                    "速度",
                ],
            },
        }

        # 宝宝装备
        self.pet_equip_types = ["护腕", "项圈", "铠甲"]
        self.pet_equip_fields = ["等级", "属性", "属性1", "属性2", "特效"]
        self.sub_attrs = [
            "伤害",
            "灵力",
            "敏捷",
            "耐力",
            "体质",
            "力量",
            "魔力",
            "气血",
            "魔法",
        ]

        # 词条
        self.affix_fields = ["境界", "词条1", "词条2", "词条3"]
        self.affix_value_fields = ["数值1", "数值2", "数值3"]

    def set_main_window(self, main_window):
        self.main_window = main_window

    def get_character_id(self) -> str:
        if self.main_window and hasattr(self.main_window, "get_player_id"):
            return self.main_window.get_player_id()
        return ""

    def validate_character_id(self) -> bool:
        if self.main_window and hasattr(self.main_window, "validate_player_id"):
            result = self.main_window.validate_player_id()
            if not result:
                player_id = self.main_window.get_player_id()
                if not player_id:
                    self.show_error_message("请输入玩家ID")
                else:
                    self.show_error_message("玩家ID必须为纯数字")
            return result
        self.show_error_message("无法获取玩家ID")
        return False

    def init_ui(self):
        """初始化界面"""
        self.setStyleSheet("background-color: #202225; border-radius: 4px;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # 标题
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(16)

        title = QLabel("⚔️ 装备定制中心")
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

        subtitle = QLabel("定制装备、灵饰、宝宝装备和词条")
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

        # 选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                background-color: #2B2D31;
                border: 1px solid #1E1F22;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #2F3136;
                color: #8E9297;
                padding: 10px 20px;
                margin-right: 6px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #2B2D31;
                color: #FFFFFF;
                border-bottom: 2px solid #5865F2;
            }
            QTabBar::tab:hover:!selected {
                background-color: #32353B;
                color: #DCDDDE;
            }
        """
        )

        # 创建各选项卡
        self._create_equipment_tab()
        self._create_ornament_tab()
        self._create_pet_equip_tab()
        self._create_affix_tab()

        main_layout.addWidget(self.tab_widget)

    def _make_scroll(self, inner: QWidget) -> QScrollArea:
        """创建滚动区域"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #2B2D31;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #1A1B1E;
                border-radius: 6px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #232428; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """
        )
        scroll.setWidget(inner)
        return scroll

    def _create_equipment_tab(self):
        """创建装备定制选项卡"""
        tab = QWidget()
        tab.setStyleSheet("QWidget { background-color: #2B2D31; }")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 顶部操作栏
        action_bar = QWidget()
        action_bar.setStyleSheet("QWidget { background-color: transparent; }")
        action_layout = QHBoxLayout(action_bar)
        action_layout.setSpacing(12)

        get_btn = DiscordButton("📥 获取装备", "secondary")
        get_btn.clicked.connect(self.get_equipment)
        action_layout.addWidget(get_btn)

        send_btn = DiscordButton("📤 发送装备", "success")
        send_btn.clicked.connect(self.send_equipment)
        action_layout.addWidget(send_btn)
        action_layout.addStretch()

        layout.addWidget(action_bar)

        # 内容区域
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)

        # 装备类型选择
        type_card = SectionCard("装备类型")
        type_row = QHBoxLayout()
        type_row.setSpacing(10)

        type_lbl = QLabel("选择类型")
        type_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; }"
        )
        type_row.addWidget(type_lbl)

        self.equipment_type_combo = DiscordComboBox()
        # 移除可编辑属性，变为纯下拉选择框
        self.equipment_type_combo.setEditable(False)  # 改为False，不允许编辑
        # 添加装备类型选项
        self.equipment_type_combo.addItems(
            ["武器", "衣服", "头盔", "项链", "腰带", "鞋子"]
        )
        self.equipment_type_combo.setMinimumWidth(150)
        # 可选：设置默认选中第一项
        self.equipment_type_combo.setCurrentIndex(0)  # 默认选中"武器"
        type_row.addWidget(self.equipment_type_combo)
        type_row.addStretch()

        type_card.content_layout.addLayout(type_row)
        content_layout.addWidget(type_card)

        # 装备属性
        attr_card = SectionCard("装备属性")
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setHorizontalSpacing(16)

        self.equipment_inputs = {}
        for i, field in enumerate(self.equipment_fields):
            r, c = divmod(i, 9)
            inp = CompactInput(field, f"{field}", 85)
            grid.addWidget(inp, r, c)
            self.equipment_inputs[field] = inp

        attr_card.content_layout.addLayout(grid)
        content_layout.addWidget(attr_card)

        # 提示信息
        tip = QLabel("💡 等级和类型必填，其他字段可选。特效、特技、制造、专用支持粘贴")
        tip.setWordWrap(True)
        tip.setStyleSheet(
            """
            QLabel {
                color: #949BA4;
                font-size: 11px;
                background-color: #1E1F22;
                border-radius: 4px;
                padding: 8px;
            }
        """
        )
        content_layout.addWidget(tip)

        scroll = self._make_scroll(content)
        layout.addWidget(scroll)

        self.tab_widget.addTab(tab, "⚔️ 装备定制")

    def _create_ornament_tab(self):
        """创建灵饰定制选项卡"""
        tab = QWidget()
        tab.setStyleSheet("QWidget { background-color: #2B2D31; }")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 操作栏
        action_bar = QWidget()
        action_layout = QHBoxLayout(action_bar)
        action_layout.setSpacing(12)

        get_btn = DiscordButton("📥 获取灵饰", "secondary")
        get_btn.clicked.connect(self.get_ornament)
        action_layout.addWidget(get_btn)

        send_btn = DiscordButton("📤 发送灵饰", "success")
        send_btn.clicked.connect(self.send_ornament)
        action_layout.addWidget(send_btn)
        action_layout.addStretch()

        layout.addWidget(action_bar)

        # 内容
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)

        # 灵饰部位
        part_card = SectionCard("灵饰部位")
        part_row = QHBoxLayout()
        part_row.setSpacing(10)

        part_lbl = QLabel("选择部位")
        part_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; }"
        )
        part_row.addWidget(part_lbl)

        self.ornament_part_combo = DiscordComboBox()
        # 设置为不可编辑的下拉选择框
        self.ornament_part_combo.setEditable(False)  # 禁止编辑
        # 添加灵饰部位选项（不带图标）
        self.ornament_part_combo.addItems(["戒指", "手镯", "佩饰", "耳饰"])
        self.ornament_part_combo.currentTextChanged.connect(
            self.on_ornament_part_changed
        )
        self.ornament_part_combo.setMinimumWidth(150)
        # 默认选中第一项
        self.ornament_part_combo.setCurrentIndex(0)
        part_row.addWidget(self.ornament_part_combo)
        part_row.addStretch()

        part_card.content_layout.addLayout(part_row)
        content_layout.addWidget(part_card)

        # 灵饰属性 - 调整为8列布局，输入框宽度90
        attr_card = SectionCard("灵饰属性")
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setHorizontalSpacing(16)

        self.ornament_inputs = {}
        # 只创建数值相关的输入框（等级、属性、数值1-4、特效、制造）
        display_fields = [
            "等级",
            "属性",
            "数值1",
            "数值2",
            "数值3",
            "数值4",
            "特效",
            "制造",
        ]
        for i, field in enumerate(display_fields):
            # 8列布局
            r, c = divmod(i, 8)
            inp = CompactInput(field, f"{field}", 90)  # 宽度调整为90
            grid.addWidget(inp, r, c)
            self.ornament_inputs[field] = inp

        attr_card.content_layout.addLayout(grid)

        # 主属和附加属性选择 - 调整为5列布局，输入框宽度90
        select_grid = QGridLayout()
        select_grid.setSpacing(10)
        select_grid.setHorizontalSpacing(16)

        # 创建主属和4个附加属性的组合框
        attr_combos = []

        # 主属
        main_lbl = QLabel("主属")
        main_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 12px; font-weight: 600; }"
        )
        self.main_attr_combo = DiscordComboBox()
        self.main_attr_combo.setMaximumWidth(130)  # 宽度设置为90
        select_grid.addWidget(main_lbl, 0, 0)
        select_grid.addWidget(self.main_attr_combo, 1, 0)

        # 附加1-4 - 5列布局
        self.add_attr_combos = []
        for i in range(1, 5):
            lbl = QLabel(f"附加{i}")
            lbl.setStyleSheet(
                "QLabel { color: #B5BAC1; font-size: 12px; font-weight: 600; }"
            )
            combo = DiscordComboBox()
            combo.setMaximumWidth(170)  # 宽度设置为90
            select_grid.addWidget(lbl, 0, i)  # 第0行，第i列
            select_grid.addWidget(combo, 1, i)  # 第1行，第i列
            self.add_attr_combos.append(combo)
            setattr(self, f"add_attr{i}_combo", combo)

        attr_card.content_layout.addLayout(select_grid)
        content_layout.addWidget(attr_card)

        # 提示
        tip = QLabel("💡 等级、部位和主属数值必填。附加属性根据选择的部位自动更新")
        tip.setWordWrap(True)
        tip.setStyleSheet(
            """
            QLabel {
                color: #949BA4;
                font-size: 11px;
                background-color: #1E1F22;
                border-radius: 4px;
                padding: 8px;
            }
        """
        )
        content_layout.addWidget(tip)

        scroll = self._make_scroll(content)
        layout.addWidget(scroll)

        self.tab_widget.addTab(tab, "💍 灵饰定制")

        # 手动触发一次部位选择事件，确保初始状态正确
        self.on_ornament_part_changed(self.ornament_part_combo.currentText())

    def _create_pet_equip_tab(self):
        """创建宝宝装备选项卡"""
        tab = QWidget()
        tab.setStyleSheet("QWidget { background-color: #2B2D31; }")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 操作栏
        action_bar = QWidget()
        action_layout = QHBoxLayout(action_bar)
        action_layout.setSpacing(12)

        get_btn = DiscordButton("📥 获取装备", "secondary")
        get_btn.clicked.connect(self.get_pet_equipment)
        action_layout.addWidget(get_btn)

        send_btn = DiscordButton("📤 发送装备", "success")
        send_btn.clicked.connect(self.send_pet_equipment)
        action_layout.addWidget(send_btn)
        action_layout.addStretch()

        layout.addWidget(action_bar)

        # 内容
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)

        # 装备类型
        type_card = SectionCard("装备类型")
        type_row = QHBoxLayout()
        type_row.setSpacing(10)

        type_lbl = QLabel("选择类型")
        type_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; }"
        )
        type_row.addWidget(type_lbl)

        self.pet_equip_type_combo = DiscordComboBox()
        # 设置为不可编辑的下拉选择框
        self.pet_equip_type_combo.setEditable(False)  # 禁止编辑
        # 添加宝宝装备选项（不带图标）
        self.pet_equip_type_combo.addItems(["护腕", "项圈", "铠甲"])
        self.pet_equip_type_combo.currentTextChanged.connect(
            self.on_pet_equip_type_changed
        )
        self.pet_equip_type_combo.setMinimumWidth(150)
        # 默认选中第一项
        self.pet_equip_type_combo.setCurrentIndex(0)
        type_row.addWidget(self.pet_equip_type_combo)
        type_row.addStretch()

        type_card.content_layout.addLayout(type_row)
        content_layout.addWidget(type_card)

        # 装备属性 - 调整为7列布局，输入框宽度100
        attr_card = SectionCard("装备属性")
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setHorizontalSpacing(16)

        self.pet_equip_inputs = {}
        # 5个基本字段 + 2个副属性 = 7个字段
        for i, field in enumerate(self.pet_equip_fields):
            inp = CompactInput(field, f"{field}", 100)  # 宽度调整为100
            r, c = divmod(i, 7)  # 7列布局
            grid.addWidget(inp, r, c)
            self.pet_equip_inputs[field] = inp

        attr_card.content_layout.addLayout(grid)

        # 副属性选择
        sub_row = QHBoxLayout()
        sub_row.setSpacing(12)

        sub_lbl1 = QLabel("副属性1")
        sub_lbl1.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 12px; font-weight: 600; }"
        )
        self.sub_attr1_combo = DiscordComboBox()
        self.sub_attr1_combo.addItems(self.sub_attrs)
        self.sub_attr1_combo.setMaximumWidth(100)  # 宽度100
        sub_row.addWidget(sub_lbl1)
        sub_row.addWidget(self.sub_attr1_combo)

        sub_lbl2 = QLabel("副属性2")
        sub_lbl2.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 12px; font-weight: 600; }"
        )
        self.sub_attr2_combo = DiscordComboBox()
        self.sub_attr2_combo.addItems(self.sub_attrs)
        self.sub_attr2_combo.setMaximumWidth(100)  # 宽度100
        sub_row.addWidget(sub_lbl2)
        sub_row.addWidget(self.sub_attr2_combo)
        sub_row.addStretch()

        # 将副属性作为第二行添加到grid
        grid.addLayout(sub_row, 1, 0, 1, 7)  # 占据第2行的全部7列

        attr_card.content_layout.addLayout(grid)
        content_layout.addWidget(attr_card)

        # 提示
        tip = QLabel(
            "💡 护腕主属性:命中 | 项圈主属性:速度 | 铠甲主属性:防御\n"
            "副属性可选2项且不可重复。特效说明：<1或无级别>=无级别 <2>=绑定 <3>=绑定+无级别 其他=无级别+强化打造"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(
            """
            QLabel {
                color: #949BA4;
                font-size: 11px;
                background-color: #1E1F22;
                border-radius: 4px;
                padding: 8px;
            }
        """
        )
        content_layout.addWidget(tip)

        scroll = self._make_scroll(content)
        layout.addWidget(scroll)

        self.tab_widget.addTab(tab, "🐾 宝宝装备")

    def _create_affix_tab(self):
        """创建定制词条选项卡"""
        tab = QWidget()
        tab.setStyleSheet("QWidget { background-color: #2B2D31; }")
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        # 操作栏
        action_bar = QWidget()
        action_layout = QHBoxLayout(action_bar)
        action_layout.setSpacing(12)

        get_btn = DiscordButton("📥 获取词条", "secondary")
        get_btn.clicked.connect(self.get_affix)
        action_layout.addWidget(get_btn)

        send_btn = DiscordButton("📤 修改词条", "success")
        send_btn.clicked.connect(self.send_affix)
        action_layout.addWidget(send_btn)
        action_layout.addStretch()

        layout.addWidget(action_bar)

        # 内容
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)

        # 装备选择
        select_card = SectionCard("选择装备")
        select_row = QHBoxLayout()
        select_row.setSpacing(10)

        select_lbl = QLabel("装备类型")
        select_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; }"
        )
        select_row.addWidget(select_lbl)

        self.affix_equip_type_combo = DiscordComboBox()
        # 设置为不可编辑的下拉选择框
        self.affix_equip_type_combo.setEditable(False)  # 禁止编辑
        # 添加装备选项（不带图标）
        self.affix_equip_type_combo.addItems(
            ["武器", "铠甲", "项链", "头盔", "腰带", "鞋子"]
        )
        self.affix_equip_type_combo.setMinimumWidth(150)
        # 默认选中第一项
        self.affix_equip_type_combo.setCurrentIndex(0)
        select_row.addWidget(self.affix_equip_type_combo)
        select_row.addStretch()

        select_card.content_layout.addLayout(select_row)
        content_layout.addWidget(select_card)

        # 词条设置 - 调整为8列布局，输入框宽度90
        affix_card = SectionCard("词条设置")
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setHorizontalSpacing(16)

        self.affix_inputs = {}

        # 所有词条字段（境界、词条1-3、数值1-3）一共7个
        all_affix_fields = self.affix_fields + self.affix_value_fields

        # 8列布局
        for i, field in enumerate(all_affix_fields):
            inp = CompactInput(field, f"{field}", 90)  # 宽度调整为90
            r, c = divmod(i, 8)  # 8列布局
            grid.addWidget(inp, r, c)
            self.affix_inputs[field] = inp

        affix_card.content_layout.addLayout(grid)

        # 神话词条 - 单独一行
        mythic_row = QHBoxLayout()
        mythic_row.setSpacing(10)

        mythic_lbl = QLabel("神话词条")
        mythic_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 12px; font-weight: 600; }"
        )
        mythic_row.addWidget(mythic_lbl)

        self.mythic_affix_input = DiscordLineEdit("神话词条")
        self.mythic_affix_input.setMaximumWidth(200)
        mythic_row.addWidget(self.mythic_affix_input)
        mythic_row.addStretch()

        affix_card.content_layout.addLayout(mythic_row)
        content_layout.addWidget(affix_card)

        # 提示
        tip = QLabel(
            "💡 玩家必须佩戴对应装备。境界：优秀、稀有、传说、神话\n"
            "词条2、3输入数值会除2。输入3个相同词条为三同词条（境界需为传说或神话）\n"
            "数值1必填，其他可选"
        )
        tip.setWordWrap(True)
        tip.setStyleSheet(
            """
            QLabel {
                color: #949BA4;
                font-size: 11px;
                background-color: #1E1F22;
                border-radius: 4px;
                padding: 8px;
            }
        """
        )
        content_layout.addWidget(tip)

        scroll = self._make_scroll(content)
        layout.addWidget(scroll)

        self.tab_widget.addTab(tab, "✨ 定制词条")

    # ========== 事件处理 ==========
    def on_ornament_part_changed(self, part):
        """灵饰部位改变"""
        if part in self.ornament_attr_map:
            self.main_attr_combo.clear()
            self.main_attr_combo.addItems(self.ornament_attr_map[part]["主属"])

            for combo in self.add_attr_combos:
                combo.clear()
                combo.addItems(self.ornament_attr_map[part]["附加"])

    def on_pet_equip_type_changed(self, equip_type):
        """宝宝装备类型改变"""
        pass  # 副属性列表已预设，无需动态更新

    # ========== 业务逻辑 ==========
    def get_equipment(self):
        """获取装备"""
        if not self.validate_character_id():
            return
        self.send_command(4, "获取角色装备", {"玩家id": self.get_character_id()})

    def _validate_equipment_inputs(
        self, level: str, equip_type: str
    ) -> tuple[str, str]:
        """验证装备输入

        Returns:
            元组(等级, 装备类型)

        Raises:
            ValueError: 当输入无效时
        """
        if not level or not level.isdigit():
            raise ValueError("请输入有效的装备等级")
        if not equip_type:
            raise ValueError("请选择装备类型")
        return level, equip_type

    def _collect_equipment_data(self, level: str, equip_type: str) -> dict:
        """收集装备数据"""
        equipment_data = {"等级": level, "类型": equip_type}
        for field in self.equipment_fields:
            if field == "等级":
                continue
            value = self.equipment_inputs[field].text().strip()
            if value:
                equipment_data[field] = value
        return equipment_data

    def send_equipment(self):
        """发送装备 - 重构后的简化版本"""
        if not self.validate_character_id():
            return

        level = self.equipment_inputs["等级"].text().strip()
        equip_type = self.equipment_type_combo.currentText()

        try:
            level, equip_type = self._validate_equipment_inputs(level, equip_type)
            equipment_data = self._collect_equipment_data(level, equip_type)

            self.send_command(
                4,
                "发送装备",
                {"玩家id": self.get_character_id(), "装备数据": equipment_data},
            )

            for inp in self.equipment_inputs.values():
                inp.clear()

        except ValueError as e:
            self.show_error_message(str(e))

    def get_ornament(self):
        """获取灵饰"""
        if not self.validate_character_id():
            return
        self.send_command(5, "获取角色灵饰", {"玩家id": self.get_character_id()})

    def _validate_ornament_inputs(
        self, level: str, part: str, attr_value: str
    ) -> tuple[str, str, str]:
        """
        验证灵饰输入

        Returns:
            元组(等级, 部位, 属性值)

        Raises:
            ValueError: 当输入无效时
        """
        if not level or not level.isdigit():
            raise ValueError("请输入有效的灵饰等级")
        if not part:
            raise ValueError("请选择灵饰部位")
        if not attr_value or not attr_value.isdigit():
            raise ValueError("请输入有效的主属数值")
        return level, part, attr_value

    def _collect_main_attr(self) -> Optional[str]:
        """收集主属性"""
        main_attr = self.main_attr_combo.currentText()
        return main_attr if main_attr else None

    def _collect_other_fields(self) -> dict:
        """收集其他字段数据"""
        data = {}
        for field in self.ornament_fields:
            if field in ["部位"]:
                continue
            value = self.ornament_inputs.get(field, CompactInput()).text().strip()
            if value:
                data[field] = value
        return data

    def _collect_additional_attrs(self) -> dict:
        """收集附加属性"""
        data = {}
        for i, combo in enumerate(self.add_attr_combos, 1):
            attr = combo.currentText()
            if attr:
                data[f"附加{i}"] = attr
        return data

    def _collect_ornament_data(self, part: str, level: str) -> dict:
        """收集灵饰数据 - 重构后的简化版本"""
        ornament_data = {"部位": part, "等级": level}

        # 主属
        main_attr = self._collect_main_attr()
        if main_attr:
            ornament_data["主属"] = main_attr

        # 其他属性字段
        ornament_data.update(self._collect_other_fields())

        # 附加属性
        ornament_data.update(self._collect_additional_attrs())

        return ornament_data

    def send_ornament(self):
        """发送灵饰 - 重构后的简化版本"""
        if not self.validate_character_id():
            return

        level = self.ornament_inputs["等级"].text().strip()
        part = self.ornament_part_combo.currentText()
        attr_value = self.ornament_inputs["属性"].text().strip()

        try:
            # 验证输入
            level, part, attr_value = self._validate_ornament_inputs(
                level, part, attr_value
            )

            # 收集数据
            ornament_data = self._collect_ornament_data(part, level)

            # 发送命令
            self.send_command(
                5,
                "发送灵饰",
                {"玩家id": self.get_character_id(), "灵饰数据": ornament_data},
            )

            # 清空输入
            for inp in self.ornament_inputs.values():
                inp.clear()

        except ValueError as e:
            self.show_error_message(str(e))

    def get_pet_equipment(self):
        """获取宝宝装备"""
        if not self.validate_character_id():
            return
        self.send_command(8, "获取宝宝装备", {"玩家id": self.get_character_id()})

    def _validate_pet_equipment_inputs(
        self, level: str, equip_type: str, attr_value: str
    ) -> tuple[str, str, str]:
        """
        验证宝宝装备输入

        Returns:
            元组(等级, 装备类型, 属性值)

        Raises:
            ValueError: 当输入无效时
        """
        if not level or not level.isdigit():
            raise ValueError("请输入有效的等级")
        if not equip_type:
            raise ValueError("请选择装备类型")
        if not attr_value or not attr_value.isdigit():
            raise ValueError("请输入有效的主属数值")
        return level, equip_type, attr_value

    def _collect_pet_equipment_data(self, equip_type: str, level: str) -> dict:
        """收集宝宝装备数据"""
        pet_equip_data = {"类型": equip_type, "等级": level}

        # 收集基本字段
        for field in self.pet_equip_fields:
            value = self.pet_equip_inputs[field].text().strip()
            if value:
                pet_equip_data[field] = value

        # 收集附加属性
        sub1 = self.sub_attr1_combo.currentText()
        sub2 = self.sub_attr2_combo.currentText()
        if sub1:
            pet_equip_data["属性1"] = sub1
        if sub2:
            pet_equip_data["属性2"] = sub2

        return pet_equip_data

    def send_pet_equipment(self):
        """发送宝宝装备 - 重构后的简化版本"""
        if not self.validate_character_id():
            return

        level = self.pet_equip_inputs["等级"].text().strip()
        equip_type = self.pet_equip_type_combo.currentText()
        attr_value = self.pet_equip_inputs["属性"].text().strip()

        try:
            # 验证输入
            level, equip_type, attr_value = self._validate_pet_equipment_inputs(
                level, equip_type, attr_value
            )

            # 收集数据
            pet_equip_data = self._collect_pet_equipment_data(equip_type, level)

            # 发送命令
            self.send_command(
                8,
                "定制宝宝装备",
                {"玩家id": self.get_character_id(), "装备数据": pet_equip_data},
            )

            # 清空输入
            for inp in self.pet_equip_inputs.values():
                inp.clear()

        except ValueError as e:
            self.show_error_message(str(e))

    def get_affix(self):
        """获取词条"""
        if not self.validate_character_id():
            return
        self.send_command(10, "获取装备词条", {"玩家id": self.get_character_id()})

    def _validate_character_for_affix(self) -> str:
        """验证角色ID并返回
        
        Returns:
            str: 角色ID
            
        Raises:
            ValueError: 当角色ID无效时
        """
        if not self.validate_character_id():
            raise ValueError("角色ID验证失败")
        return self.get_character_id()

    def _collect_affix_data(self) -> dict:
        """收集词条数据
        
        Returns:
            dict: 词条数据字典
            
        Raises:
            ValueError: 当装备类型未选择时
        """
        equip_type = self.affix_equip_type_combo.currentText()
        if not equip_type:
            raise ValueError("请选择装备类型")

        affix_data = {"类型": equip_type}

        # 收集常规词条
        for field in self.affix_fields + self.affix_value_fields:
            value = self.affix_inputs[field].text().strip()
            if value:
                affix_data[field] = value

        # 收集神话词条
        mythic = self.mythic_affix_input.text().strip()
        if mythic:
            affix_data["神话词条"] = mythic

        return affix_data

    def _clear_affix_inputs(self):
        """清空词条输入框"""
        for inp in self.affix_inputs.values():
            inp.clear()
        self.mythic_affix_input.clear()

    def send_affix(self):
        """修改词条 - 优化版本"""
        try:
            char_id = self._validate_character_for_affix()
            affix_data = self._collect_affix_data()

            self.send_command(
                10, "装备词条", {"玩家id": char_id, "修改数据": affix_data}
            )
            self._clear_affix_inputs()

        except ValueError as e:
            self.show_error_message(str(e))
