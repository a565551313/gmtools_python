#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
赠送道具模块 - 序号=9 Discord风格
实现给予道具、给予宝石、CDK卡号管理等功能

本次调整说明：
- 道具给予区域：3个标签+3个输入框+1个按钮，改为4列布局，输入框宽度-30%
- 宝石给予区域：控件（标签/输入框/选择框/按钮）整体移动到道具给予区域，且输入框/选择框宽度-30%，并移除该卡片
- CDK管理：将“获取卡号”和“写出本地”按钮移动到“获取充值类型”按钮旁，三列排布
- CDK卡片“多一层背景”修复：限制卡片样式作用范围、分区容器透明、标签透明、滚动视口透明
"""

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
    QTextEdit,
    QScrollArea,
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
        elif self.color_type == "warning":
            bg, hover, pressed = "#FEE75C", "#E6D056", "#CDB84E"
        else:  # secondary
            bg, hover, pressed = "#4F545C", "#5D6269", "#484C54"

        text_color = "#313338" if self.color_type == "warning" else "white"

        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg};
                color: {text_color};
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


class SectionCard(QFrame):
    """区域卡片"""

    def __init__(self, title="", subtitle="", icon="", parent=None):
        super().__init__(parent)
        # 关键：仅给本卡片着色，不影响子QFrame，避免“多一层背景”
        self.setObjectName("SectionCard")
        self.setStyleSheet(
            """
            #SectionCard {
                background-color: #2B2D31;
                border-radius: 8px;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # 标题栏
        if title:
            header = QHBoxLayout()
            header.setSpacing(10)

            title_label = QLabel(f"{icon} {title}" if icon else title)
            title_label.setStyleSheet(
                """
                QLabel {
                    color: #F2F3F5;
                    font-size: 18px;
                    font-weight: 700;
                    background: transparent;
                    border: none;
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
                        background: transparent;
                        border: none;
                    }
                """
                )
                header.addWidget(sub_label)

            header.addStretch()
            layout.addLayout(header)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        layout.addLayout(self.content_layout)


class InputField(QWidget):
    """输入字段组件（横向标签+输入框）"""

    def __init__(self, label="", placeholder="", width=None, parent=None):
        super().__init__(parent)
        # 关键：容器透明，避免继承背景
        self.setStyleSheet("background: transparent; border: none;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        if label:
            lbl = QLabel(label)
            lbl.setMinimumWidth(80)
            lbl.setStyleSheet(
                """
                QLabel {
                    color: #B5BAC1;
                    font-size: 13px;
                    font-weight: 600;
                    background: transparent;  /* 标签透明 */
                    border: none;
                }
            """
            )
            layout.addWidget(lbl)

        self.input = DiscordLineEdit(placeholder)
        if width:
            self.input.setMaximumWidth(width)
        layout.addWidget(self.input)
        layout.addStretch()

    def text(self):
        return self.input.text()

    def setText(self, text):
        self.input.setText(text)

    def clear(self):
        self.input.clear()


class GiftModule(BaseModule):
    """赠送道具模块 - Discord风格重新设计"""

    def __init__(self, client=None):
        super().__init__(client)
        self.main_window = None
        self.recharge_types = []
        self.card_numbers = []

    def set_main_window(self, main_window):
        self.main_window = main_window

    def get_character_id(self) -> str:
        if self.main_window and hasattr(self.main_window, "get_player_id"):
            return self.main_window.get_player_id()
        return ""

    def validate_character_id(self) -> bool:
        if self.main_window and hasattr(self.main_window, "validate_player_id"):
            return self.main_window.validate_player_id()
        self.show_error("无法获取玩家ID")
        return False

    def init_ui(self):
        """初始化界面"""
        self.setStyleSheet("background-color: #202225; border-radius: 4px;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ========== 滚动区域 ==========
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            """
            QScrollArea {
                background: transparent;
                border: none;
            }
            /* 关键：把视口容器也设为透明，避免额外底色 */
            QScrollArea > QWidget {
                background: transparent;
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

        content = QWidget()
        # 关键：内容容器透明
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 创建两列布局
        columns = QHBoxLayout()
        columns.setSpacing(16)

        # 左列：仅保留“道具给予”卡片（宝石给予控件已并入）
        left_col = QVBoxLayout()
        left_col.setSpacing(16)
        left_col.addWidget(self._create_item_card())  # 备注：宝石给予已移动至此
        left_col.addStretch()

        # 右列：CDK卡号管理
        right_col = QVBoxLayout()
        right_col.setSpacing(16)
        right_col.addWidget(self._create_cdk_card())
        right_col.addStretch()

        columns.addLayout(left_col, 1)
        columns.addLayout(right_col, 1)
        content_layout.addLayout(columns)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    def _create_item_card(self):
        """创建道具给予卡片（含宝石给予控件，4列布局）"""
        card = SectionCard("道具 / 宝石 给予", "赠送物品与宝石给玩家（统一入口）", "📦")

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setHorizontalSpacing(12)

        # 宽度基准与-30%后宽度（备注）
        base_item_width = 140
        item_width = int(base_item_width * 0.7)  # ≈98
        gem_combo_base = 150
        gem_combo_width = int(gem_combo_base * 0.7)  # 105
        gem_input_base = 120
        gem_input_width = int(gem_input_base * 0.7)  # 84

        # ========== 道具给予 ==========
        name_lbl = QLabel("名称")
        name_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; background: transparent; border: none; }"
        )
        self.item_name_input = DiscordLineEdit("道具名称")
        self.item_name_input.setMaximumWidth(item_width)

        count_lbl = QLabel("数量")
        count_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; background: transparent; border: none; }"
        )
        self.item_count_input = DiscordLineEdit("数量（默认1）")
        self.item_count_input.setMaximumWidth(item_width)

        grid.addWidget(name_lbl, 0, 0)
        grid.addWidget(self.item_name_input, 0, 1)
        grid.addWidget(count_lbl, 0, 2)
        grid.addWidget(self.item_count_input, 0, 3)

        param_lbl = QLabel("参数")
        param_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; background: transparent; border: none; }"
        )
        self.item_param_input = DiscordLineEdit("参数（可选）")
        self.item_param_input.setMaximumWidth(item_width)

        give_item_btn = DiscordButton("🎁 给予道具", "success")
        give_item_btn.clicked.connect(self.give_item)

        grid.addWidget(param_lbl, 1, 0)
        grid.addWidget(self.item_param_input, 1, 1)
        grid.addWidget(give_item_btn, 1, 2, 1, 2)

        # ========== 宝石给予 ==========
        gem_type_lbl = QLabel("宝石类型")
        gem_type_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; background: transparent; border: none; }"
        )
        self.gem_type = DiscordComboBox()
        self.gem_type.addItems(
            [
                "星辉石",
                "光芒石",
                "月亮石",
                "太阳石",
                "舍利子",
                "红玛瑙",
                "黑宝石",
                "神秘石",
            ]
        )
        self.gem_type.setMinimumWidth(gem_combo_width)

        min_lbl = QLabel("最低等级")
        min_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; background: transparent; border: none; }"
        )
        self.min_level_input = DiscordLineEdit("如：9")
        self.min_level_input.setMaximumWidth(gem_input_width)

        grid.addWidget(gem_type_lbl, 2, 0)
        grid.addWidget(self.gem_type, 2, 1)
        grid.addWidget(min_lbl, 2, 2)
        grid.addWidget(self.min_level_input, 2, 3)

        max_lbl = QLabel("最高等级")
        max_lbl.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; background: transparent; border: none; }"
        )
        self.max_level_input = DiscordLineEdit("可选")
        self.max_level_input.setMaximumWidth(gem_input_width)

        give_gem_btn = DiscordButton("💎 给予宝石", "success")
        give_gem_btn.clicked.connect(self.give_gem)

        grid.addWidget(max_lbl, 3, 0)
        grid.addWidget(self.max_level_input, 3, 1)
        grid.addWidget(give_gem_btn, 3, 2, 1, 2)

        card.content_layout.addLayout(grid)

        # 使用说明（道具 + 宝石）
        tip_item = QLabel("💡 提示：道具名称必填，数量和参数可选")
        tip_item.setWordWrap(True)
        tip_item.setStyleSheet(
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
        card.content_layout.addWidget(tip_item)

        tip_gem = QLabel("💡 提示：不填最高等级则只给予最低等级的宝石")
        tip_gem.setWordWrap(True)
        tip_gem.setStyleSheet(
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
        card.content_layout.addWidget(tip_gem)

        return card

    def _create_cdk_card(self):
        """创建CDK卡号管理卡片（调整按钮为三列）"""
        card = SectionCard("CDK卡号管理", "生成和管理充值卡号", "🎫")

        # 统一的标签样式（透明背景）
        label_style = (
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; "
            "background: transparent; border: none; }"
        )

        # 第一部分：获取和选择类型
        type_section = QWidget()
        type_section.setStyleSheet("background: transparent;")  # 关键：分区容器透明
        type_layout = QVBoxLayout(type_section)
        type_layout.setContentsMargins(0, 0, 0, 8)
        type_layout.setSpacing(8)

        # 顶部三列按钮
        top_grid = QGridLayout()
        top_grid.setSpacing(8)

        get_type_btn = DiscordButton("📥 获取充值类型", "secondary")
        get_type_btn.clicked.connect(self.get_recharge_types)
        top_grid.addWidget(get_type_btn, 0, 0)

        get_card_btn = DiscordButton("📥 获取卡号", "secondary")
        get_card_btn.clicked.connect(self.get_recharge_card)
        top_grid.addWidget(get_card_btn, 0, 1)

        write_btn = DiscordButton("💾 写出本地", "secondary")
        write_btn.clicked.connect(self.write_to_local)
        top_grid.addWidget(write_btn, 0, 2)

        type_layout.addLayout(top_grid)

        # 选择类型
        select_row = QHBoxLayout()
        select_row.setSpacing(10)

        select_lbl = QLabel("选择类型")
        select_lbl.setMinimumWidth(80)
        select_lbl.setStyleSheet(label_style)
        select_row.addWidget(select_lbl)

        self.recharge_type_selector = DiscordComboBox()
        self.recharge_type_selector.setPlaceholderText("请先获取充值类型")
        select_row.addWidget(self.recharge_type_selector)
        select_row.addStretch()

        type_layout.addLayout(select_row)
        card.content_layout.addWidget(type_section)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("QFrame { background-color: #3F4147; max-height: 1px; }")
        card.content_layout.addWidget(line)

        # 第三部分：生成CDK
        gen_section = QWidget()
        gen_section.setStyleSheet("background: transparent;")  # 关键：分区容器透明
        gen_layout = QVBoxLayout(gen_section)
        gen_layout.setContentsMargins(0, 8, 0, 8)
        gen_layout.setSpacing(8)

        # 生成按钮
        gen_btn_row = QHBoxLayout()
        gen_btn_row.setSpacing(8)

        gen_btn = DiscordButton("🎲 生成CDK", "primary")
        gen_btn.clicked.connect(self.generate_cdk)
        gen_btn_row.addWidget(gen_btn)

        gen_custom_btn = DiscordButton("✏️ 自定义CDK", "primary")
        gen_custom_btn.clicked.connect(self.generate_custom_cdk)
        gen_btn_row.addWidget(gen_custom_btn)

        gen_layout.addLayout(gen_btn_row)

        # 数量和位数
        param_grid = QGridLayout()
        param_grid.setSpacing(10)
        param_grid.setHorizontalSpacing(12)

        count_lbl = QLabel("数量")
        count_lbl.setStyleSheet(label_style)
        self.count_input = DiscordLineEdit("生成数量")
        self.count_input.setMaximumWidth(100)
        param_grid.addWidget(count_lbl, 0, 0)
        param_grid.addWidget(self.count_input, 0, 1)

        digits_lbl = QLabel("位数")
        digits_lbl.setStyleSheet(label_style)
        self.digits_input = DiscordLineEdit("位数")
        self.digits_input.setMaximumWidth(100)
        param_grid.addWidget(digits_lbl, 0, 2)
        param_grid.addWidget(self.digits_input, 0, 3)

        gen_layout.addLayout(param_grid)

        # 自定义内容
        custom_field = InputField("自定义内容", "输入自定义CDK内容")
        self.custom_input = custom_field.input
        gen_layout.addWidget(custom_field)

        card.content_layout.addWidget(gen_section)

        # 分隔线
        line3 = QFrame()
        line3.setFrameShape(QFrame.Shape.HLine)
        line3.setStyleSheet("QFrame { background-color: #3F4147; max-height: 1px; }")
        card.content_layout.addWidget(line3)

        # 第四部分：类型管理
        manage_section = QWidget()
        manage_section.setStyleSheet("background: transparent;")  # 关键：分区容器透明
        manage_layout = QVBoxLayout(manage_section)
        manage_layout.setContentsMargins(0, 8, 0, 0)
        manage_layout.setSpacing(8)

        manage_btn_row = QHBoxLayout()
        manage_btn_row.setSpacing(8)

        new_btn = DiscordButton("➕ 新建类型", "success")
        new_btn.clicked.connect(self.new_recharge_type)
        manage_btn_row.addWidget(new_btn)

        del_btn = DiscordButton("🗑️ 删除类型", "danger")
        del_btn.clicked.connect(self.del_recharge_type)
        manage_btn_row.addWidget(del_btn)

        manage_layout.addLayout(manage_btn_row)

        # 类型名称输入
        name_field = InputField("类型名称", "输入删除或新建的类型名称")
        self.type_name_input = name_field.input
        manage_layout.addWidget(name_field)

        card.content_layout.addWidget(manage_section)

        # 卡号显示区域
        display_label = QLabel("卡号显示")
        display_label.setStyleSheet(
            """
            QLabel {
                color: #B5BAC1;
                font-size: 13px;
                font-weight: 600;
                margin-top: 8px;
                background: transparent;
                border: none;
            }
        """
        )
        card.content_layout.addWidget(display_label)

        self.card_display = QTextEdit()
        self.card_display.setReadOnly(True)
        self.card_display.setMaximumHeight(120)
        self.card_display.setStyleSheet(
            """
            QTextEdit {
                background-color: #1E1F22;
                color: #F2F3F5;
                border: 1px solid #3F4147;
                border-radius: 6px;
                padding: 8px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
            }
        """
        )
        card.content_layout.addWidget(self.card_display)

        return card

    # ========== 业务逻辑 ==========
    def _validate_item_inputs(self, item_name: str, item_count: str) -> tuple[str, str]:
        """验证道具输入

        Raises:
            ValueError: 当输入无效时
        """
        if not item_name:
            raise ValueError("请输入道具名称")
        if item_count and not item_count.isdigit():
            raise ValueError("数量必须为纯数字")
        return item_name, item_count

    def _validate_gem_inputs(self, min_level: str, max_level: str) -> tuple[str, str]:
        """验证宝石输入

        Raises:
            ValueError: 当输入无效时
        """
        if not min_level or not min_level.isdigit():
            raise ValueError("请输入有效的最低等级")
        if max_level and not max_level.isdigit():
            raise ValueError("最高等级必须为纯数字")
        return min_level, max_level

    def give_item(self):
        """给予道具 - 重构后的简化版本"""
        char_id = self.get_character_id()
        if not char_id or not char_id.isdigit():
            self.show_error("请输入有效的角色ID")
            return

        item_name = self.item_name_input.text().strip()
        item_count = self.item_count_input.text().strip()
        item_params = self.item_param_input.text().strip()

        try:
            item_name, item_count = self._validate_item_inputs(item_name, item_count)

            give_data = {"名称": item_name}
            if item_count:
                give_data["数量"] = item_count
            if item_params:
                give_data["参数"] = item_params

            self.send_command(9, "给予道具", {"玩家id": char_id, "给予数据": give_data})
            self.add_log(f"已发送给予道具请求: {char_id} - {item_name}")

        except ValueError as e:
            self.show_error(str(e))

    def give_gem(self):
        """给予宝石 - 重构后的简化版本"""
        char_id = self.get_character_id()
        if not char_id or not char_id.isdigit():
            self.show_error("请输入有效的角色ID")
            return

        min_level = self.min_level_input.text().strip()
        max_level = self.max_level_input.text().strip()

        try:
            min_level, max_level = self._validate_gem_inputs(min_level, max_level)

            give_data = {"名称": self.gem_type.currentText(), "最小等级": min_level}
            if max_level:
                give_data["最大等级"] = max_level

            self.send_command(9, "给予宝石", {"玩家id": char_id, "给予数据": give_data})
            self.add_log(
                f"已发送给予宝石请求: {char_id} - {self.gem_type.currentText()}"
            )

        except ValueError as e:
            self.show_error(str(e))

    def get_recharge_types(self):
        """获取充值类型"""
        self.send_command(9, "获取充值类型")
        self.add_log("已发送获取充值类型请求")

    def get_recharge_card(self):
        """获取充值卡号"""
        selected_type = self.recharge_type_selector.currentText()
        if not selected_type:
            self.show_error("请先选择充值类型")
            return

        self.send_command(9, "获取充值卡号", {"生成文件": selected_type})
        self.add_log(f"已发送获取充值卡号请求: {selected_type}")

    def _validate_cdk_inputs(self, count: str, digits: str) -> tuple[str, str]:
        """验证CDK输入

        Raises:
            ValueError: 当输入无效时
        """
        if count and not count.isdigit():
            raise ValueError("数量必须为纯数字")
        if digits and not digits.isdigit():
            raise ValueError("位数必须为纯数字")
        return count, digits

    def generate_cdk(self):
        """生成CDK卡号 - 重构后的简化版本"""
        selected_type = self.recharge_type_selector.currentText()
        if not selected_type:
            self.show_error("请先选择充值类型")
            return

        count = self.count_input.text().strip()
        digits = self.digits_input.text().strip()

        try:
            count, digits = self._validate_cdk_inputs(count, digits)

            gen_data = {}
            if count:
                gen_data["数量"] = count
            if digits:
                gen_data["位数"] = digits

            self.send_command(
                9, "生成CDK卡号", {"生成数据": gen_data, "生成文件": selected_type}
            )
            self.add_log(f"已发送生成CDK请求: {selected_type}")

        except ValueError as e:
            self.show_error(str(e))

    def generate_custom_cdk(self):
        """生成自定义CDK"""
        selected_type = self.recharge_type_selector.currentText()
        if not selected_type:
            self.show_error("请先选择充值类型")
            return

        custom_content = self.custom_input.text().strip()
        if not custom_content:
            self.show_error("请输入自定义内容")
            return

        gen_data = {"自定义": custom_content}

        self.send_command(
            9, "生成自定义CDK卡号", {"生成数据": gen_data, "生成文件": selected_type}
        )
        self.add_log(f"已发送生成自定义CDK请求: {selected_type}")

    def new_recharge_type(self):
        """新建充值类型"""
        type_name = self.type_name_input.text().strip()
        if not type_name:
            self.show_error("请输入类型名称")
            return

        self.send_command(9, "新建充值类型", {"生成文件": type_name})
        self.add_log(f"已发送新建充值类型请求: {type_name}")

    def del_recharge_type(self):
        """删除充值类型"""
        type_name = self.type_name_input.text().strip()
        if not type_name:
            self.show_error("请输入类型名称")
            return

        selected_type = self.recharge_type_selector.currentText()
        if not selected_type:
            self.show_error("请先选择要删除的类型")
            return

        self.send_command(
            9, "删除充值卡号", {"生成文件": selected_type, "生成卡号": type_name}
        )
        self.add_log(f"已发送删除充值卡号请求: {selected_type}")

    def write_to_local(self):
        """写出到本地"""
        if not self.card_numbers:
            self.show_error("没有卡号数据可写出")
            return

        import os
        from datetime import datetime

        os.makedirs("卡号数据", exist_ok=True)

        filename = f"卡号数据/{datetime.now().strftime('%Y%m%d_%H%M%S')}_获取的CDK.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                for i, card in enumerate(self.card_numbers, 1):
                    f.write(f"第{i}个:{card}\n")
            self.add_log(f"已写出到本地: {filename}")
            self.card_display.append(
                f"\n✅ 成功写出 {len(self.card_numbers)} 个卡号到: {filename}"
            )
        except Exception as e:
            self.add_log(f"写出失败: {e}")
            self.show_error(f"写出失败: {e}")

    def add_log(self, message: str):
        print(f"[赠送道具] {message}")

    def show_error(self, message: str):
        self.show_error_message(message)

    def set_recharge_types(self, recharge_types: list):
        """设置充值类型到下拉框"""
        try:
            print(f"[DEBUG] GiftModule 接收到 {len(recharge_types)} 个充值类型")

            # 如果列表为空，不进行任何操作
            if not recharge_types:
                print("[DEBUG] 充值类型列表为空，保持当前下拉框内容")
                return

            # 保存当前选中的项
            current_text = self.recharge_type_selector.currentText()
            print(f"[DEBUG] 当前选中的充值类型: {current_text}")

            # 清空现有选项
            self.recharge_type_selector.clear()

            # 添加新的充值类型选项
            for recharge_type in recharge_types:
                self.recharge_type_selector.addItem(recharge_type)
                print(f"[DEBUG] 添加充值类型: {recharge_type}")

            # 恢复之前选中的项（如果还存在）
            if current_text:
                index = self.recharge_type_selector.findText(current_text)
                if index >= 0:
                    self.recharge_type_selector.setCurrentIndex(index)
                    print(f"[DEBUG] 恢复选中项: {current_text}")

            # 存储充值类型列表
            self.recharge_types = recharge_types

            # 显示成功消息
            self.card_display.append(f"\n✅ 成功加载 {len(recharge_types)} 个充值类型")

            print(f"[DEBUG] 充值类型填充完成")

        except Exception as e:
            print(f"[ERROR] 设置充值类型失败: {e}")
            import traceback

            traceback.print_exc()

    def set_card_numbers(self, card_numbers: list):
        """设置卡号数据到卡号显示区域"""
        try:
            print(f"[DEBUG] GiftModule 接收到 {len(card_numbers)} 个卡号")

            # 存储卡号列表
            self.card_numbers = card_numbers

            # 清空卡号显示区域
            self.card_display.clear()

            # 检查是否有有效数据
            if not card_numbers:
                self.card_display.append("❌ 没有获取到有效数据")
                print("[DEBUG] 卡号列表为空")
                return

            # 显示卡号数据
            self.card_display.append(f"📋 获取到 {len(card_numbers)} 个卡号：\n")
            for i, card_number in enumerate(card_numbers, 1):
                self.card_display.append(f"第{i}个: {card_number}")

            print(f"[DEBUG] 卡号数据填充完成")

        except Exception as e:
            print(f"[ERROR] 设置卡号失败: {e}")
            import traceback

            traceback.print_exc()

    def set_client(self, client):
        super().set_client(client)
