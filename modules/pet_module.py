#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
宝宝管理模块 - 序号=8 Discord风格
实现召唤兽信息获取、属性修改、技能修改、天生技能修改、坐骑管理、功德录、宝宝装备等
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
        # 简化风格逻辑
        styles = {
            "primary": ("#5865F2", "#4752C4", "#3C45A5"),
            "success": ("#3BA55C", "#2D7D46", "#276D3D"),
            "danger": ("#ED4245", "#C03537", "#A22C2E"),
            "secondary": ("#4F545C", "#5D6269", "#484C54"),
        }
        bg, hover, pressed = styles.get(self.color_type, styles["secondary"])

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


class SectionCard(QFrame):
    """区域卡片"""

    def __init__(self, title="", subtitle="", icon="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #2B2D31;
                border-radius: 8px;
                padding: 0px;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        if title:
            header_layout = QHBoxLayout()
            header_layout.setSpacing(10)

            title_label = QLabel(f"{icon} {title}" if icon else title)
            title_label.setStyleSheet(
                """
                QLabel {
                    color: #F2F3F5;
                    font-size: 18px;
                    font-weight: 700;
                }
            """
            )
            header_layout.addWidget(title_label)

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
                header_layout.addWidget(sub_label)

            header_layout.addStretch()
            layout.addLayout(header_layout)

        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(10)
        layout.addLayout(self.content_layout)


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
                    background: transparent;
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


class PetModule(BaseModule):
    """宝宝管理模块 - Discord风格重新设计"""

    def __init__(self, client=None):
        super().__init__(client)
        self.main_window = None
        self.pet_data = {}
        self.ui_inputs = {}  # 集中管理所有UI输入控件
        self._updating_attrs = False  # 防止无限递归的标志位

        # 定义常用字段，方便复用和管理
        self.pet_attr_fields = [
            ("等级", "0"),
            ("模型", ""),
            ("种类", ""),
            ("潜力", ""),
            ("寿命", ""),
            ("成长", ""),
            ("攻击资质", "0"),
            ("防御资质", "0"),
            ("体力资质", "0"),
            ("法力资质", "0"),
            ("速度资质", "0"),
            ("躲闪资质", "0"),
        ]
        self.pet_skill_fields = [f"技能{i:02d}" for i in range(1, 21)]
        self.innate_fields = [f"天生{i:02d}" for i in range(1, 5)]
        self.mount_skills_list = [
            "反震",
            "吸血",
            "反击",
            "连击",
            "飞行",
            "感知",
            "再生",
            "冥思",
            "慧根",
            "必杀",
            "幸运",
            "神迹",
            "招架",
            "永恒",
            "偷袭",
            "毒",
            "驱鬼",
            "鬼魂术",
            "魔之心",
            "神佑复生",
            "精神集中",
            "法术连击",
            "法术暴击",
            "法术波动",
            "土属性吸收",
            "火属性吸收",
            "水属性吸收",
        ]
        self.merit_types_list = [
            "气血",
            "伤害",
            "防御",
            "速度",
            "穿刺等级",
            "治疗能力",
            "固定伤害",
            "法术伤害",
            "法术防御",
            "气血回复效果",
            "封印命中等级",
            "抵抗封印等级",
            "法术暴击等级",
            "物理暴击等级",
            "抗法术暴击等级",
            "抗物理暴击等级",
        ]
        self.common_attrs_list = [
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

    def set_main_window(self, main_window):
        self.main_window = main_window

    def set_pet_data(self, pet_list):
        """设置宝宝数据列表

        Args:
            pet_list: 宝宝数据列表，每个元素是一个宝宝的属性字典
        """
        print(f"[DEBUG] PetModule.set_pet_data被调用，收到 {len(pet_list)} 个宝宝")

        self.pet_data = {}

        # 存储所有宝宝数据
        for i, pet_info in enumerate(pet_list):
            pet_index = i + 1  # 使用1-based索引

            # 清理字符串值中的引号
            cleaned_pet_info = {}
            for key, value in pet_info.items():
                if isinstance(value, str):
                    cleaned_value = value.strip("\"'")
                    cleaned_pet_info[key] = cleaned_value
                else:
                    cleaned_pet_info[key] = value

            self.pet_data[pet_index] = cleaned_pet_info
            pet_name = cleaned_pet_info.get("名称", "未知名称")
            pet_level = cleaned_pet_info.get("等级", 0)
            pet_model = cleaned_pet_info.get("模型", "")
            print(
                f"[DEBUG] 保存宝宝 {pet_index}: {pet_name} (Lv.{pet_level}, {pet_model})"
            )

        # 检查UI是否存在
        print(f"[DEBUG] 检查UI组件存在情况:")
        print(
            f"  - 'pet_selector' in self.ui_inputs: {'pet_selector' in self.ui_inputs}"
        )
        if "pet_selector" in self.ui_inputs:
            pet_selector = self.ui_inputs["pet_selector"]
            print(f"  - pet_selector类型: {type(pet_selector)}")
            print(f"  - pet_selector状态: {pet_selector.isVisible()}")

        # 触发UI更新显示宝宝列表
        self._update_pet_list_display()

        print(f"[DEBUG] PetModule.set_pet_data完成，已保存 {len(self.pet_data)} 只宝宝")

    def _update_pet_list_display(self):
        """更新宝宝列表显示"""
        print(f"[DEBUG] _update_pet_list_display被调用")

        if "pet_selector" not in self.ui_inputs:
            print(f"[DEBUG] 未找到pet_selector组件")
            return

        # 获取宝宝选择器
        pet_selector = self.ui_inputs["pet_selector"]
        print(f"[DEBUG] 找到pet_selector: {type(pet_selector)}")

        try:
            # 清空现有列表
            pet_selector.clear()
            print(f"[DEBUG] 已清空选择器")

            # 添加每个宝宝的选项
            added_count = 0
            for pet_index, pet_info in self.pet_data.items():
                pet_name = pet_info.get("名称", f"宝宝{pet_index}")
                pet_level = pet_info.get("等级", 0)
                pet_model = pet_info.get("模型", "")
                display_text = f"{pet_name} - Lv.{pet_level} ({pet_model})"
                pet_selector.addItem(display_text, pet_index)  # 使用索引作为用户数据
                added_count += 1
                print(
                    f"[DEBUG] 添加选项 {added_count}: {display_text} (索引: {pet_index})"
                )

            print(
                f"[DEBUG] 已更新宝宝选择器，成功添加 {added_count} 只宝宝，当前选择器项目数: {pet_selector.count()}"
            )

        except Exception as e:
            print(f"[ERROR] 更新宝宝选择器失败: {e}")
            import traceback

            traceback.print_exc()

    def get_character_id(self) -> str:
        if self.main_window and hasattr(self.main_window, "get_player_id"):
            return self.main_window.get_player_id()
        return ""

    def validate_character_id(self) -> bool:
        if self.main_window and hasattr(self.main_window, "validate_player_id"):
            return self.main_window.validate_player_id()
        self.show_error("无法获取玩家ID")
        return False

    def _create_input_widgets(
        self, parent_layout, fields_info, input_dict_key, columns=1, input_width=180
    ):
        """
        辅助方法，用于在网格布局中批量创建 CompactInput 控件。
        fields_info: 列表，每个元素可以是字符串 (label) 或元组 (label, placeholder)。
        input_dict_key: 用于在 self.ui_inputs 中存储这些控件的键名。
        """
        if input_dict_key not in self.ui_inputs:
            self.ui_inputs[input_dict_key] = {}

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.setHorizontalSpacing(16)

        for i, field_data in enumerate(fields_info):
            label = field_data[0] if isinstance(field_data, tuple) else field_data
            placeholder = field_data[1] if isinstance(field_data, tuple) else label

            r, c = divmod(i, columns)
            inp = CompactInput(label, placeholder, input_width)
            grid_layout.addWidget(inp, r, c)
            self.ui_inputs[input_dict_key][label] = inp  # 以label作为子键名存储

        parent_layout.addLayout(grid_layout)

    def init_ui(self):
        """初始化界面"""
        self.setStyleSheet("background-color: #202225; border-radius: 4px;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ========== 宝宝选择栏 ==========
        select_bar = SectionCard()
        select_bar.setStyleSheet(
            """QFrame { border-radius: 8px; border: 2px solid #5865F2; }"""
        )

        select_widgets_layout = QHBoxLayout()
        select_widgets_layout.setSpacing(12)

        select_label = QLabel("当前宝宝")
        select_label.setStyleSheet(
            "QLabel { color: #B5BAC1; font-size: 13px; font-weight: 600; }"
        )
        select_widgets_layout.addWidget(select_label)

        self.ui_inputs["pet_selector"] = DiscordComboBox()
        self.ui_inputs["pet_selector"].setEditable(False)
        self.ui_inputs["pet_selector"].setPlaceholderText("请先获取宝宝信息")
        self.ui_inputs["pet_selector"].setMinimumWidth(250)
        self.ui_inputs["pet_selector"].currentTextChanged.connect(self.on_pet_selected)
        select_widgets_layout.addWidget(self.ui_inputs["pet_selector"])

        self.get_pet_btn = DiscordButton("📥 获取宝宝", "secondary")
        self.get_pet_btn.clicked.connect(self.get_pet_info)
        select_widgets_layout.addWidget(self.get_pet_btn)

        self.modify_pet_btn = DiscordButton("✅ 确定修改", "success")
        self.modify_pet_btn.clicked.connect(self.modify_pet)
        select_widgets_layout.addWidget(self.modify_pet_btn)

        select_widgets_layout.addStretch()
        select_bar.content_layout.addLayout(select_widgets_layout)
        main_layout.addWidget(select_bar)

        # ========== 滚动区域 ==========
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(
            """
            QScrollArea { background: transparent; border: none; }
            QScrollBar:vertical { background: #2B2D31; width: 12px; border-radius: 6px; }
            QScrollBar::handle:vertical { background: #1A1B1E; border-radius: 6px; min-height: 30px; }
            QScrollBar::handle:vertical:hover { background: #232428; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """
        )

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(16)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # 两列布局
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(16)

        # 左列
        left_col_layout = QVBoxLayout()
        left_col_layout.setSpacing(16)
        left_col_layout.addWidget(self._create_pet_attr_card())
        left_col_layout.addWidget(self._create_pet_skill_card())
        left_col_layout.addStretch()

        # 右列
        right_col_layout = QVBoxLayout()
        right_col_layout.setSpacing(16)
        right_col_layout.addWidget(self._create_innate_card())
        right_col_layout.addWidget(self._create_merit_card())
        right_col_layout.addWidget(self._create_equip_card())
        right_col_layout.addStretch()

        columns_layout.addLayout(left_col_layout, 1)
        columns_layout.addLayout(right_col_layout, 1)
        content_layout.addLayout(columns_layout)

        content_layout.addWidget(self._create_mount_card())  # 全宽

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_pet_attr_card(self):
        """创建召唤兽属性卡片"""
        card = SectionCard("召唤兽属性", "修改宝宝的基础属性", "⚔️")
        # 修改为4列布局，宽度减少50%（180 -> 90）
        self._create_input_widgets(
            card.content_layout,
            self.pet_attr_fields,
            "pet_attrs",
            columns=4,
            input_width=90,
        )
        return card

    def _create_pet_skill_card(self):
        """创建召唤兽技能卡片"""
        card = SectionCard("召唤兽技能", "最多20个技能位", "📜")
        # 修改为3列布局，宽度减少40%+（180 -> 126 -> 112）
        self._create_input_widgets(
            card.content_layout,
            self.pet_skill_fields,
            "pet_skills",
            columns=4,
            input_width=112,
        )
        return card

    def _create_innate_card(self):
        """创建天生技能卡片"""
        card = SectionCard("天生技能", "宝宝的天生技能", "✨")
        # 修改为4列布局，宽度减少40%+（180 -> 126 -> 114）
        self._create_input_widgets(
            card.content_layout,
            self.innate_fields,
            "innate_skills",
            columns=4,
            input_width=114,
        )
        return card

    def _create_merit_card(self):
        """创建功德录卡片 - 重新设计为2列布局"""
        card = SectionCard("功德录", "提升宝宝战力", "📖")

        # 操作按钮
        btn_row_layout = QHBoxLayout()
        btn_row_layout.setSpacing(8)
        self.get_merit_btn = DiscordButton("激活", "secondary")
        self.get_merit_btn.clicked.connect(self.activate_merit)
        btn_row_layout.addWidget(self.get_merit_btn)

        self.modify_merit_btn = DiscordButton("修改", "success")
        self.modify_merit_btn.clicked.connect(self.modify_merit)
        btn_row_layout.addWidget(self.modify_merit_btn)
        btn_row_layout.addStretch()
        card.content_layout.addLayout(btn_row_layout)

        # 功德录词条 - 2列布局
        self.ui_inputs["merit_types_combos"] = {}
        self.ui_inputs["merit_values_inputs"] = {}

        grid_layout = QGridLayout()
        grid_layout.setSpacing(10)
        grid_layout.setHorizontalSpacing(16)

        for i in range(6):
            row = i // 2  # 2列布局
            col = i % 2

            # 创建一个水平容器来放置词条组件
            merit_widget = QWidget()
            merit_layout = QHBoxLayout(merit_widget)
            merit_layout.setContentsMargins(0, 0, 0, 0)
            merit_layout.setSpacing(5)  # 固定间距5

            lbl = QLabel(f"词条{i+1}")
            lbl.setStyleSheet(
                """
                QLabel { 
                    color: #B5BAC1; 
                    font-size: 12px; 
                    min-width: 40px;
                    background: transparent;
                }
            """
            )
            merit_layout.addWidget(lbl)

            combo = DiscordComboBox()
            combo.setEditable(False)
            combo.addItems(self.merit_types_list)
            combo.setMinimumWidth(70)  # 减少50%宽度（140 -> 70）
            combo.setMaximumWidth(70)
            self.ui_inputs["merit_types_combos"][i] = combo
            merit_layout.addWidget(combo)

            # 添加数值标签
            value_lbl = QLabel("数值")
            value_lbl.setStyleSheet(
                """
                QLabel { 
                    color: #B5BAC1; 
                    font-size: 12px;
                    background: transparent;
                }
            """
            )
            merit_layout.addWidget(value_lbl)

            value_input = DiscordLineEdit("0")
            value_input.setMaximumWidth(40)  # 减少50%宽度（80 -> 40）
            self.ui_inputs["merit_values_inputs"][i] = value_input
            merit_layout.addWidget(value_input)

            merit_layout.addStretch()

            grid_layout.addWidget(merit_widget, row, col)

        card.content_layout.addLayout(grid_layout)
        return card

    def _create_equip_card(self):
        """创建宝宝装备卡片 - 三行布局"""
        card = SectionCard("装备定制", "定制宝宝专属装备", "🛡️")

        # 第一行：类型选择 + 主属性值输入 + 动态属性显示 + 发送按钮
        first_row_layout = QHBoxLayout()
        first_row_layout.setSpacing(10)

        # 类型选择
        type_lbl = QLabel("类型")
        type_lbl.setStyleSheet(
            """
            QLabel { 
                color: #B5BAC1; 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
            }
        """
        )
        first_row_layout.addWidget(type_lbl)

        self.ui_inputs["equip_type"] = DiscordComboBox()
        self.ui_inputs["equip_type"].addItems(["护腕", "项圈", "铠甲"])
        self.ui_inputs["equip_type"].setMaximumWidth(100)
        self.ui_inputs["equip_type"].currentTextChanged.connect(
            self._on_equip_type_changed
        )
        first_row_layout.addWidget(self.ui_inputs["equip_type"])

        # 属性值输入
        attr_value_lbl = QLabel("属性值")
        attr_value_lbl.setStyleSheet(
            """
            QLabel { 
                color: #B5BAC1; 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
            }
        """
        )
        first_row_layout.addWidget(attr_value_lbl)

        self.ui_inputs["main_attr_value"] = DiscordLineEdit("0")
        self.ui_inputs["main_attr_value"].setMaximumWidth(80)
        first_row_layout.addWidget(self.ui_inputs["main_attr_value"])

        # 动态属性名称标签
        self.dynamic_attr_label = QLabel("(命中)")
        self.dynamic_attr_label.setStyleSheet(
            """
            QLabel { 
                color: #5865F2; 
                font-size: 12px; 
                font-weight: bold;
                background: transparent;
            }
        """
        )
        first_row_layout.addWidget(self.dynamic_attr_label)

        # 发送装备按钮
        self.custom_equip_btn = DiscordButton("📤 发送装备", "primary")
        self.custom_equip_btn.clicked.connect(self.custom_equip)
        first_row_layout.addWidget(self.custom_equip_btn)

        first_row_layout.addStretch()
        card.content_layout.addLayout(first_row_layout)

        # 第二行：等级 + 属性1 + 属性值1
        second_row_layout = QHBoxLayout()
        second_row_layout.setSpacing(10)

        # 等级
        level_lbl = QLabel("等级")
        level_lbl.setStyleSheet(
            """
            QLabel { 
                color: #B5BAC1; 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
            }
        """
        )
        second_row_layout.addWidget(level_lbl)

        self.ui_inputs["equip_level"] = DiscordLineEdit("0")
        self.ui_inputs["equip_level"].setMaximumWidth(60)
        second_row_layout.addWidget(self.ui_inputs["equip_level"])

        # 属性1
        attr1_lbl = QLabel("属性1")
        attr1_lbl.setStyleSheet(
            """
            QLabel { 
                color: #B5BAC1; 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
            }
        """
        )
        second_row_layout.addWidget(attr1_lbl)

        self.ui_inputs["sub_attr1"] = DiscordComboBox()
        self.ui_inputs["sub_attr1"].setEditable(False)
        self.ui_inputs["sub_attr1"].addItems(self.common_attrs_list)
        self.ui_inputs["sub_attr1"].setMaximumWidth(100)
        self.ui_inputs["sub_attr1"].currentTextChanged.connect(self._on_attr1_changed)
        second_row_layout.addWidget(self.ui_inputs["sub_attr1"])

        # 属性值1
        self.ui_inputs["sub_attr1_value"] = DiscordLineEdit("0")
        self.ui_inputs["sub_attr1_value"].setMaximumWidth(80)
        second_row_layout.addWidget(self.ui_inputs["sub_attr1_value"])

        second_row_layout.addStretch()
        card.content_layout.addLayout(second_row_layout)

        # 第三行：属性2 + 属性值2 + 特效
        third_row_layout = QHBoxLayout()
        third_row_layout.setSpacing(10)

        # 属性2
        attr2_lbl = QLabel("属性2")
        attr2_lbl.setStyleSheet(
            """
            QLabel { 
                color: #B5BAC1; 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
            }
        """
        )
        third_row_layout.addWidget(attr2_lbl)

        self.ui_inputs["sub_attr2"] = DiscordComboBox()
        self.ui_inputs["sub_attr2"].setEditable(False)
        self.ui_inputs["sub_attr2"].addItems(self.common_attrs_list)
        self.ui_inputs["sub_attr2"].setMaximumWidth(100)

        # 设置属性2默认选择索引1（灵力），避免与属性1默认值（伤害）冲突
        if len(self.common_attrs_list) > 1:
            self.ui_inputs["sub_attr2"].setCurrentIndex(1)

        self.ui_inputs["sub_attr2"].currentTextChanged.connect(self._on_attr2_changed)
        third_row_layout.addWidget(self.ui_inputs["sub_attr2"])

        # 属性值2
        self.ui_inputs["sub_attr2_value"] = DiscordLineEdit("0")
        self.ui_inputs["sub_attr2_value"].setMaximumWidth(80)
        third_row_layout.addWidget(self.ui_inputs["sub_attr2_value"])

        # 特效
        effect_lbl = QLabel("特效")
        effect_lbl.setStyleSheet(
            """
            QLabel { 
                color: #B5BAC1; 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
            }
        """
        )
        third_row_layout.addWidget(effect_lbl)

        self.ui_inputs["equip_effect"] = DiscordLineEdit("")
        self.ui_inputs["equip_effect"].setMaximumWidth(120)
        third_row_layout.addWidget(self.ui_inputs["equip_effect"])

        third_row_layout.addStretch()
        card.content_layout.addLayout(third_row_layout)

        return card

    def _on_equip_type_changed(self, equip_type):
        """当装备类型改变时更新动态属性显示"""
        type_attr_map = {"护腕": "命中", "项圈": "速度", "铠甲": "防御"}
        attr_name = type_attr_map.get(equip_type, "")
        self.dynamic_attr_label.setText(f"({attr_name})")

    def _update_attr_combo(self, combo, excluded_attr: str, current_value: str):
        """更新属性下拉框，排除已选的属性

        Args:
            combo: 要更新的下拉框
            excluded_attr: 要排除的属性
            current_value: 当前选择的值
        """
        combo.blockSignals(True)

        combo.clear()
        available_attrs = [
            attr for attr in self.common_attrs_list if attr != excluded_attr
        ]
        combo.addItems(available_attrs)

        if current_value in available_attrs:
            index = combo.findText(current_value)
            if index >= 0:
                combo.setCurrentIndex(index)

        combo.blockSignals(False)

    def _on_attr1_changed(self, attr1_text):
        """当属性1改变时，更新属性2的可选项 - 重构后的简化版本"""
        if self._updating_attrs or not attr1_text:
            return

        self._updating_attrs = True

        try:
            attr2_combo = self.ui_inputs["sub_attr2"]
            current_attr2 = attr2_combo.currentText()
            self._update_attr_combo(attr2_combo, attr1_text, current_attr2)

        finally:
            self._updating_attrs = False

    def _on_attr2_changed(self, attr2_text):
        """当属性2改变时，更新属性1的可选项 - 重构后的简化版本"""
        if self._updating_attrs or not attr2_text:
            return

        self._updating_attrs = True

        try:
            attr1_combo = self.ui_inputs["sub_attr1"]
            current_attr1 = attr1_combo.currentText()
            self._update_attr_combo(attr1_combo, attr2_text, current_attr1)

        finally:
            self._updating_attrs = False

    def _create_mount_card(self):
        """创建坐骑管理卡片"""
        card = SectionCard("坐骑管理", "管理你的专属坐骑", "🐴")

        # 操作栏
        mount_action_row_layout = QHBoxLayout()
        mount_action_row_layout.setSpacing(10)

        # 修复：为"选择坐骑"标签添加样式
        mount_select_label = QLabel("选择坐骑")
        mount_select_label.setStyleSheet(
            """
            QLabel { 
                color: #B5BAC1; 
                font-size: 12px; 
                font-weight: 600;
                background: transparent;
            }
        """
        )
        mount_action_row_layout.addWidget(mount_select_label)

        self.ui_inputs["mount_selector"] = DiscordComboBox()
        self.ui_inputs["mount_selector"].setEditable(False)
        self.ui_inputs["mount_selector"].setPlaceholderText("获取坐骑后操作")
        self.ui_inputs["mount_selector"].setMinimumWidth(200)
        mount_action_row_layout.addWidget(self.ui_inputs["mount_selector"])

        self.get_mount_btn = DiscordButton("📥 获取坐骑", "secondary")
        self.get_mount_btn.clicked.connect(self.get_mount)
        mount_action_row_layout.addWidget(self.get_mount_btn)

        self.modify_mount_btn = DiscordButton("✅ 修改坐骑", "success")
        self.modify_mount_btn.clicked.connect(self.modify_mount)
        mount_action_row_layout.addWidget(self.modify_mount_btn)
        mount_action_row_layout.addStretch()
        card.content_layout.addLayout(mount_action_row_layout)

        # 基础属性
        base_mount_attr_row_layout = QHBoxLayout()
        base_mount_attr_row_layout.setSpacing(12)

        self.ui_inputs["mount_attrs"] = {}
        self.ui_inputs["mount_attrs"]["等级"] = CompactInput("等级", "等级", 80)
        base_mount_attr_row_layout.addWidget(self.ui_inputs["mount_attrs"]["等级"])
        self.ui_inputs["mount_attrs"]["成长"] = CompactInput("成长", "成长", 80)
        base_mount_attr_row_layout.addWidget(self.ui_inputs["mount_attrs"]["成长"])
        self.ui_inputs["mount_attrs"]["技能点"] = CompactInput("技能点", "技能点", 80)
        base_mount_attr_row_layout.addWidget(self.ui_inputs["mount_attrs"]["技能点"])
        base_mount_attr_row_layout.addStretch()
        card.content_layout.addLayout(base_mount_attr_row_layout)

        # 坐骑技能选择 - 使用下拉框
        skill_row_layout = QHBoxLayout()
        skill_row_layout.setSpacing(8)
        
        self.ui_inputs["mount_skills"] = {}
        for i in range(1, 6):
            skill_combo = DiscordComboBox()
            skill_combo.setEditable(False)
            skill_combo.addItem("")  # 空选项
            skill_combo.addItems(self.mount_skills_list)
            skill_combo.setMinimumWidth(112)
            self.ui_inputs["mount_skills"][f"技能{i}"] = skill_combo
            skill_row_layout.addWidget(skill_combo)
        
        skill_row_layout.addStretch()
        card.content_layout.addLayout(skill_row_layout)

        # 提示信息
        tip = QLabel("💡 可用技能: " + "、".join(self.mount_skills_list[:10]) + "...")
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
        card.content_layout.addWidget(tip)
        return card

    # ========== 业务逻辑保持不变 ==========
    def get_pet_info(self):
        char_id = self.get_character_id()
        if not char_id or not char_id.isdigit():
            self.show_error("请输入有效的角色ID")
            return
        self.send_command(8, "获取宝宝信息", {"玩家id": char_id})
        self.add_log(f"已发送获取宝宝信息请求: {char_id}")

    def on_pet_selected(self, pet_name: str):
        """当选择宝宝时触发的事件"""
        if not pet_name:
            return

        # 获取选择框
        pet_selector = self.ui_inputs["pet_selector"]
        current_index = pet_selector.currentIndex()

        if current_index >= 0:
            # 获取用户数据（pet_index）
            pet_index = pet_selector.itemData(current_index)
            if pet_index:
                print(f"[DEBUG] 选择宝宝: {pet_name}, 索引: {pet_index}")
                self.load_pet_data(pet_index)
        else:
            # 兼容旧版本：通过文本解析索引
            if "-" in pet_name:
                try:
                    pet_index = int(pet_name.split("-")[0])
                    self.load_pet_data(pet_index)
                except ValueError:
                    pass  # 忽略无效的宠物选择格式

    def set_mount_data(self, data: dict):
        """设置坐骑数据"""
        self.mount_data = data
        self.ui_inputs["mount_selector"].clear()
        
        if not data:
            return

        # 排序坐骑数据 - 提取[1], [2]等格式的键
        def get_sort_key(k):
            s = str(k)
            if s.startswith("[") and s.endswith("]"):
                s = s[1:-1]
            return int(s) if s.isdigit() else 0

        sorted_keys = sorted(data.keys(), key=get_sort_key)
        
        for key in sorted_keys:
            mount_info = data[key]
            name = self._clean_value(mount_info.get("名称", "未知坐骑"))
            self.ui_inputs["mount_selector"].addItem(f"{name}", key)

        # 默认选中第一个并填充数据
        if self.ui_inputs["mount_selector"].count() > 0:
            self.ui_inputs["mount_selector"].setCurrentIndex(0)
            self.ui_inputs["mount_selector"].currentIndexChanged.connect(self.on_mount_selected)
            self.on_mount_selected(0)

    def on_mount_selected(self, index):
        """当选择坐骑时触发"""
        if index < 0:
            return
            
        mount_key = self.ui_inputs["mount_selector"].itemData(index)
        if not mount_key or mount_key not in self.mount_data:
            return
            
        mount_info = self.mount_data[mount_key]
        
        # 填充基础属性
        if "等级" in self.ui_inputs["mount_attrs"]:
            self.ui_inputs["mount_attrs"]["等级"].setText(str(mount_info.get("等级", 0)))
        if "成长" in self.ui_inputs["mount_attrs"]:
            self.ui_inputs["mount_attrs"]["成长"].setText(str(mount_info.get("成长", 0)))
        if "技能点" in self.ui_inputs["mount_attrs"]:
            self.ui_inputs["mount_attrs"]["技能点"].setText(str(mount_info.get("技能点", 0)))
            
        # 填充技能 - 重置所有下拉框到空选项
        for i in range(1, 6):
            if f"技能{i}" in self.ui_inputs["mount_skills"]:
                self.ui_inputs["mount_skills"][f"技能{i}"].setCurrentIndex(0)
                
        # 填充现有技能
        skills = mount_info.get("技能", {})
        if isinstance(skills, dict):
            for key, skill_name in skills.items():
                # 提取 [1] 格式中的数字
                idx_str = str(key).strip("[]")
                if idx_str.isdigit():
                    idx = int(idx_str)
                    field_key = f"技能{idx}"
                    if field_key in self.ui_inputs["mount_skills"]:
                        cleaned_skill = self._clean_value(skill_name)
                        # 在下拉框中查找并设置对应的技能
                        combo = self.ui_inputs["mount_skills"][field_key]
                        skill_index = combo.findText(cleaned_skill)
                        if skill_index >= 0:
                            combo.setCurrentIndex(skill_index)

    @staticmethod
    def _clean_value(value):
        """清理字符串值，去除引号

        Args:
            value: 要清理的值

        Returns:
            清理后的字符串
        """
        if isinstance(value, str):
            return value.strip("\"'")
        return str(value)

    def _load_pet_attributes(self, pet_info: dict):
        """
        加载宝宝属性到UI

        Args:
            pet_info: 宝宝信息字典
        """
        for field_label, _ in self.pet_attr_fields:
            if field_label in self.ui_inputs["pet_attrs"]:
                value = pet_info.get(field_label, "")
                cleaned_value = self._clean_value(value)
                self.ui_inputs["pet_attrs"][field_label].setText(cleaned_value)

    def _load_skills_from_dict(
        self, skills_data: dict, field_labels: list, ui_section: str
    ):
        """
        从字典格式加载技能数据

        Args:
            skills_data: 技能数据字典 {[1]="技能1", [2]="技能2"}
            field_labels: 字段标签列表
            ui_section: UI输入区域名称
        """
        for i, field_label in enumerate(field_labels):
            if field_label in self.ui_inputs[ui_section]:
                skill_key = f"[{i + 1}]"
                skill_name = skills_data.get(skill_key, "")
                cleaned_name = self._clean_value(skill_name)
                self.ui_inputs[ui_section][field_label].setText(cleaned_name)

    def _load_skills_from_list(
        self, skills_data: list, field_labels: list, ui_section: str
    ):
        """
        从列表格式加载技能数据

        Args:
            skills_data: 技能数据列表
            field_labels: 字段标签列表
            ui_section: UI输入区域名称
        """
        for i, field_label in enumerate(field_labels):
            if field_label in self.ui_inputs[ui_section]:
                skill_name = skills_data[i] if i < len(skills_data) else ""
                cleaned_name = self._clean_value(skill_name)
                self.ui_inputs[ui_section][field_label].setText(cleaned_name)

    def _load_skill_data(
        self, pet_info: dict, data_key: str, field_labels: list, ui_section: str
    ):
        """
        通用技能数据加载方法（支持字典和列表格式）

        Args:
            pet_info: 宝宝信息字典
            data_key: 数据键名（如"技能"、"天生技能"）
            field_labels: 字段标签列表
            ui_section: UI输入区域名称
        """
        skills_data = pet_info.get(data_key, {})

        if isinstance(skills_data, dict):
            self._load_skills_from_dict(skills_data, field_labels, ui_section)
        elif isinstance(skills_data, list):
            self._load_skills_from_list(skills_data, field_labels, ui_section)

    def load_pet_data(self, pet_index: int):
        """
        加载指定宝宝的数据到UI界面 - 重构后的简化版本

        Args:
            pet_index: 宝宝索引
        """
        # 验证数据存在
        if pet_index not in self.pet_data:
            self.add_log(f"宝宝索引 {pet_index} 没有缓存数据。请先从游戏内获取。")
            return

        pet_info = self.pet_data[pet_index]
        self.add_log(f"已加载宝宝: {pet_info.get('名称', '未知')} (索引: {pet_index})")

        # 加载各类数据
        self._load_pet_attributes(pet_info)
        self._load_skill_data(pet_info, "技能", self.pet_skill_fields, "pet_skills")
        self._load_skill_data(pet_info, "天生技能", self.innate_fields, "innate_skills")

        # 功德录、装备、坐骑的加载逻辑类似，需根据实际数据结构实现。

    def _collect_pet_modify_data(
        self, fields, ui_section: str, use_index: bool = False
    ) -> dict:
        """
        收集宝宝修改数据的通用方法

        Args:
            fields: 字段列表
            ui_section: UI输入区域名称
            use_index: 是否使用索引作为键（技能用True，属性用False）

        Returns:
            收集到的修改数据字典
        """
        data = {}
        for i, field_label in enumerate(fields, 1):
            # 处理元组格式（属性字段）和普通字符串（技能字段）
            label = field_label[0] if isinstance(field_label, tuple) else field_label
            input_widget = self.ui_inputs[ui_section].get(label)

            if input_widget:
                value = input_widget.text().strip()
                if value:
                    key = i if use_index else label
                    data[key] = value
                    input_widget.clear()

        return data

    def _validate_character_id(self) -> str:
        """验证并返回角色ID
        
        Returns:
            str: 有效的角色ID
            
        Raises:
            ValueError: 当角色ID无效时
        """
        char_id = self.get_character_id()
        if not char_id or not char_id.isdigit():
            raise ValueError("请输入有效的角色ID")
        return char_id

    def _get_selected_pet_index(self) -> int:
        """获取选中的宝宝索引
        
        Returns:
            int: 宝宝索引
            
        Raises:
            ValueError: 当宝宝选择无效时
        """
        selected_text = self.ui_inputs["pet_selector"].currentText()
        if not selected_text or "-" not in selected_text:
            raise ValueError("请选择要修改的宝宝")
        
        # 使用 currentData() 获取存储的索引
        pet_index = self.ui_inputs["pet_selector"].currentData()
        if pet_index is None:
             # 如果没有 user data，尝试回退到旧的解析方式（兼容性）
            try:
                return int(selected_text.split("-")[0])
            except (ValueError, IndexError):
                raise ValueError("宝宝选择格式错误")
        return int(pet_index)

    def _collect_all_pet_data(self) -> dict:
        """收集所有宝宝修改数据
        
        Returns:
            dict: 修改数据字典
            
        Raises:
            ValueError: 当没有输入数据时
        """
        modify_data = {
            "属性": self._collect_pet_modify_data(
                self.pet_attr_fields, "pet_attrs", False
            ),
            "技能": self._collect_pet_modify_data(
                self.pet_skill_fields, "pet_skills", True
            ),
            "天生": self._collect_pet_modify_data(
                self.innate_fields, "innate_skills", True
            ),
        }
        
        if not any(modify_data.values()):
            raise ValueError("没有输入任何修改数据")
        
        return modify_data

    def modify_pet(self):
        """修改宝宝 - 进一步优化版本"""
        try:
            char_id = self._validate_character_id()
            pet_index = self._get_selected_pet_index()
            modify_data = self._collect_all_pet_data()
            
            self.send_command(
                8,
                "确定修改",
                {"玩家id": char_id, "修改数据": modify_data, "召唤兽编号": pet_index},
            )
            self.add_log(f"已发送宝宝修改请求: 索引{pet_index}")
            
        except ValueError as e:
            self.show_error(str(e))

    def activate_merit(self):
        char_id = self.get_character_id()
        if not char_id or not char_id.isdigit():
            self.show_error("请输入有效的角色ID")
            return
        self.send_command(8, "激活功德录", {"玩家id": char_id})
        self.add_log(f"已发送激活功德录请求: {char_id}")

    def _collect_single_merit_entry(self, index: int):
        """收集单个功德录条目
        
        Args:
            index: 词条索引 (0-5)
        
        Returns:
            dict: 功德录条目字典，如果没有数据则返回None
        
        Raises:
            ValueError: 当数额不是纯数字时
        """
        combo = self.ui_inputs["merit_types_combos"].get(index)
        value_input = self.ui_inputs["merit_values_inputs"].get(index)
        
        if not combo or not value_input:
            return None
        
        merit_type = combo.currentText().strip()
        merit_value_str = value_input.text().strip()
        
        if not merit_type or not merit_value_str:
            return None
        
        if not merit_value_str.isdigit():
            raise ValueError(f"词条{index+1}数额必须为纯数字")
        
        value_input.clear()
        return {
            "类型": merit_type,
            "数额": int(merit_value_str),
        }

    def _collect_merit_data(self) -> dict:
        """收集功德录数据 - 优化版本

        Returns:
            功德录数据字典

        Raises:
            ValueError: 当数额不是纯数字时
        """
        modify_data = {}
        
        for i in range(6):
            merit_entry = self._collect_single_merit_entry(i)
            if merit_entry:
                modify_data[i + 1] = merit_entry
        
        return modify_data

    def modify_merit(self):
        """修改功德录 - 重构后的简化版本"""
        char_id = self.get_character_id()
        if not char_id or not char_id.isdigit():
            self.show_error("请输入有效的角色ID")
            return

        try:
            modify_data = self._collect_merit_data()

            if not modify_data:
                self.show_error("没有输入任何功德录数据")
                return

            self.send_command(
                8, "修改功德录", {"玩家id": char_id, "修改数据": modify_data}
            )
            self.add_log(f"已发送修改功德录请求: {char_id}, 数据: {modify_data}")

        except ValueError as e:
            self.show_error(str(e))

    def _validate_pet_equip_data(self, equip_data: dict):
        """验证宝宝装备数据

        Raises:
            ValueError: 当验证失败时
        """
        if not equip_data["属性值"] or not equip_data["等级"]:
            raise ValueError("请填写属性值和等级")

        if not equip_data["等级"].isdigit():
            raise ValueError("装备等级必须为纯数字")

        if equip_data["类型1"] == equip_data["类型2"]:
            raise ValueError("属性1和属性2不能相同")

    def _clear_pet_equip_inputs(self):
        """清空宝宝装备输入框"""
        self.ui_inputs["main_attr_value"].clear()
        self.ui_inputs["equip_level"].clear()
        self.ui_inputs["sub_attr1_value"].clear()
        self.ui_inputs["sub_attr2_value"].clear()
        self.ui_inputs["equip_effect"].clear()

    def custom_equip(self):
        """发送宝宝装备 - 重构后的简化版本"""
        char_id = self.get_character_id()
        if not char_id or not char_id.isdigit():
            self.show_error("请输入有效的角色ID")
            return

        equip_data = {
            "主类型": self.ui_inputs["equip_type"].currentText(),
            "属性值": self.ui_inputs["main_attr_value"].text().strip(),
            "等级": self.ui_inputs["equip_level"].text().strip(),
            "属性值1": self.ui_inputs["sub_attr1_value"].text().strip(),
            "属性值2": self.ui_inputs["sub_attr2_value"].text().strip(),
            "特效": self.ui_inputs["equip_effect"].text().strip(),
            "类型1": self.ui_inputs["sub_attr1"].currentText(),
            "类型2": self.ui_inputs["sub_attr2"].currentText(),
        }

        try:
            self._validate_pet_equip_data(equip_data)

            self.send_command(
                8, "定制宝宝装备", {"玩家id": char_id, "装备数据": equip_data}
            )
            self.add_log(f"已发送宝宝装备定制请求: {char_id}, 数据: {equip_data}")

            self._clear_pet_equip_inputs()

        except ValueError as e:
            self.show_error(str(e))

    def get_mount(self):
        char_id = self.get_character_id()
        if not char_id or not char_id.isdigit():
            self.show_error("请输入有效的角色ID")
            return
        self.send_command(8, "获取坐骑", {"玩家id": char_id})
        self.add_log(f"已发送获取坐骑请求: {char_id}")

    def _validate_mount_attrs(
        self, level: str, growth: str, skill_point: str
    ) -> tuple[int, float, int]:
        """
        验证坐骑基础属性

        Returns:
            元组(等级, 成长, 技能点)

        Raises:
            ValueError: 当属性值无效时
        """
        if not all([level, growth, skill_point]):
            raise ValueError("请输入完整的坐骑基础属性")

        if not level.isdigit() or not skill_point.isdigit():
            raise ValueError("等级和技能点必须为数字")

        try:
            growth_float = float(growth)
        except ValueError:
            raise ValueError("成长必须为数字")

        return int(level), growth_float, int(skill_point)

    def _collect_mount_skills(self) -> list:
        """收集坐骑技能数据"""
        skill_data = []
        for i in range(1, 6):  # 坐骑技能从1到5
            field_label = f"技能{i}"
            skill_input = self.ui_inputs["mount_skills"].get(field_label)
            if skill_input:
                skill_name = skill_input.currentText().strip()
                if skill_name:
                    if skill_name in self.mount_skills_list:
                        skill_data.append(skill_name)
                    else:
                        self.add_log(
                            f"警告: {field_label}的技能'{skill_name}'无效或不在已知列表中"
                        )
                    skill_input.setCurrentIndex(0)  # 使用后重置为空选项
        return skill_data

    def _get_mount_basic_attrs(self) -> tuple[str, str, str]:
        """获取坐骑基础属性输入值
        
        Returns:
            tuple: (等级, 成长, 技能点)
        """
        level_input = self.ui_inputs["mount_attrs"].get("等级")
        growth_input = self.ui_inputs["mount_attrs"].get("成长")
        skill_point_input = self.ui_inputs["mount_attrs"].get("技能点")
        
        return (
            level_input.text().strip() if level_input else "",
            growth_input.text().strip() if growth_input else "",
            skill_point_input.text().strip() if skill_point_input else "",
        )

    def _collect_all_mount_data(self) -> dict:
        """收集所有坐骑数据
        
        Returns:
            dict: 坐骑修改数据
            
        Raises:
            ValueError: 当验证失败时
        """
        level, growth, skill_point = self._get_mount_basic_attrs()
        level_val, growth_val, skill_point_val = self._validate_mount_attrs(
            level, growth, skill_point
        )
        skill_data = self._collect_mount_skills()
        
        return {
            "等级": level_val,
            "成长": growth_val,
            "技能点": skill_point_val,
            "技能数据": skill_data,
        }

    def _clear_mount_inputs(self):
        """清空坐骑输入框"""
        for field in ["等级", "成长", "技能点"]:
            if field in self.ui_inputs["mount_attrs"]:
                self.ui_inputs["mount_attrs"][field].clear()

    def modify_mount(self):
        """修改坐骑 - 进一步优化版本"""
        try:
            char_id = self._validate_character_id()
            
            # 获取选中的坐骑编号
            current_index = self.ui_inputs["mount_selector"].currentIndex()
            if current_index < 0:
                raise ValueError("请选择要修改的坐骑")
            
            mount_key = self.ui_inputs["mount_selector"].itemData(current_index)
            if not mount_key:
                raise ValueError("无法获取坐骑编号")
            
            # 提取编号（从 [1], [2] 等格式中提取数字）
            mount_index_str = str(mount_key).strip("[]")
            if not mount_index_str.isdigit():
                raise ValueError("坐骑编号格式错误")
            mount_index = int(mount_index_str)
            
            modify_data = self._collect_all_mount_data()
            
            # 转换技能数据为 Lua 格式 {[1]="技能1", [2]="技能2"}
            skill_list = modify_data.get("技能数据", [])
            if skill_list:
                lua_skills = {i: skill for i, skill in enumerate(skill_list, 1)}
                modify_data["技能数据"] = lua_skills
            else:
                modify_data["技能数据"] = {}
            
            # 添加坐骑编号
            modify_data["编号"] = mount_index
            
            self.send_command(
                8, "坐骑修改", {"玩家id": char_id, "修改数据": modify_data}
            )
            self.add_log(f"已发送修改坐骑请求: {char_id}, 坐骑编号: {mount_index}")
            
            self._clear_mount_inputs()
            
        except ValueError as e:
            self.show_error(str(e))

    def add_log(self, message: str):
        print(f"[宝宝管理] {message}")

    def show_error(self, message: str):
        self.show_error_message(message)

    def set_client(self, client):
        super().set_client(client)
