#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定制词条模块 - 序号=10
实现装备词条修改功能
"""

from typing import Optional, Tuple
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QComboBox,
    QGridLayout,
    QScrollArea,
)
from PyQt6.QtCore import Qt
from .base_module import BaseModule


class CustomAffixModule(BaseModule):
    """定制词条模块"""

    def __init__(self, client=None):
        super().__init__(client)
        # 移除 init_ui() 调用，改为在 setup_ui() 中调用

    def _get_combo_style(self) -> str:
        """获取组合框样式

        Returns:
            str: Discord风格的CSS样式字符串
        """
        return """
        QComboBox {
            background-color: #202225;
            color: white;
            border: 1px solid #202225;
            border-radius: 4px;
            padding: 2px 6px;
        }
        QComboBox:focus { border: 1px solid #5865F2; }
        QComboBox QLineEdit { background-color: transparent; color: white; border: none; padding: 0; }
        QComboBox::down-arrow { width: 12px; height: 12px; image: none; border-left: 4px solid #72767D; border-bottom: 4px solid #72767D; margin-right: 4px; }
        QComboBox::drop-down { border: none; width: 20px; background-color: transparent; }
        QComboBox QAbstractItemView { background-color: #202225; color: white; border: 1px solid #5865F2; selection-background-color: #5865F2; selection-color: white; }
    """

    def _create_combo_box(self, field: str, has_value: bool) -> QComboBox:
        """创建单个组合框

        Args:
            field: 字段名
            has_value: 是否有值输入框

        Returns:
            QComboBox: 配置好的组合框
        """
        combo = QComboBox()
        combo.setEditable(True)
        combo.setMinimumWidth(80 if has_value else 100)
        combo.setPlaceholderText(f"选择{field}")

        if has_value:
            combo.setStyleSheet(self._get_combo_style())

        return combo

    def _add_field_to_layout(
        self, layout: QGridLayout, field: str, row: int, col: int, has_value: bool
    ) -> Tuple[QComboBox, Optional[QLineEdit]]:
        """添加字段到布局

        Args:
            layout: 布局对象
            field: 字段名
            row: 行号
            col: 列号
            has_value: 是否包含值输入框

        Returns:
            tuple: (组合框, 值输入框)
        """
        label = QLabel(f"{field}:")
        combo = self._create_combo_box(field, has_value)
        value_input = None

        col_offset = col * (3 if has_value else 2)
        layout.addWidget(label, row, col_offset)
        layout.addWidget(combo, row, col_offset + 1)

        if has_value:
            value_input = QLineEdit()
            value_input.setPlaceholderText("数值")
            value_input.setMaximumWidth(80)
            layout.addWidget(value_input, row, col_offset + 2)

        return combo, value_input

    def _create_field_group(
        self, title: str, fields: list, cols_per_row: int, has_value: bool = False
    ) -> Tuple[QGroupBox, dict, dict]:
        """创建字段组控件（通用方法）- 重构后的简化版本

        Args:
            title: 组标题
            fields: 字段列表
            cols_per_row: 每行列数
            has_value: 是否包含数值输入框

        Returns:
            元组(组框, 下拉框字典, 输入框字典)
        """
        group = QGroupBox(title)
        layout = QGridLayout(group)

        combos = {}
        values = {} if has_value else None

        for i, field in enumerate(fields):
            row = i // cols_per_row
            col = i % cols_per_row

            combo, value_input = self._add_field_to_layout(
                layout, field, row, col, has_value
            )
            combos[field] = combo

            if has_value and value_input:
                values[field] = value_input

        return group, combos, values

    def init_ui(self):
        """初始化界面 - 重构后的简化版本"""
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # 角色ID输入
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("角色ID:"))
        self.character_id_input = QLineEdit()
        self.character_id_input.setPlaceholderText("请输入角色ID（纯数字）")
        id_layout.addWidget(self.character_id_input)

        self.get_info_btn = QPushButton("获取角色装备")
        self.get_info_btn.clicked.connect(self.get_character_equipment)
        id_layout.addWidget(self.get_info_btn)

        self.modify_btn = QPushButton("确定修改")
        self.modify_btn.clicked.connect(self.modify_affixes)
        id_layout.addWidget(self.modify_btn)

        self.layout.addLayout(id_layout)

        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container_layout = QVBoxLayout(container)

        # 词条选择组（装备部位）
        self.equip_slots = [
            "武器",
            "衣服",
            "帽子",
            "项链",
            "腰带",
            "鞋子",
            "手镯",
            "戒指",
            "护腕",
            "腰坠",
        ]
        equip_group, self.equip_slot_combos, _ = self._create_field_group(
            "选择装备", self.equip_slots, cols_per_row=5, has_value=False
        )
        container_layout.addWidget(equip_group)

        # 主属性组
        self.main_attr_fields = [
            "气血",
            "魔法",
            "伤害",
            "灵力",
            "防御",
            "敏捷",
            "力量",
            "耐力",
            "体质",
            "魔力",
        ]
        main_group, self.main_attr_combos, self.main_attr_values = (
            self._create_field_group(
                "主属性设置", self.main_attr_fields, cols_per_row=5, has_value=True
            )
        )
        container_layout.addWidget(main_group)

        # 绿字词条组
        self.green_affix_fields = [f"绿字{i+1}" for i in range(8)]
        green_group, self.green_combos, self.green_values = self._create_field_group(
            "绿字词条", self.green_affix_fields, cols_per_row=4, has_value=True
        )
        container_layout.addWidget(green_group)

        # 蓝字词条组
        self.blue_affix_fields = [f"蓝字{i+1}" for i in range(6)]
        blue_group, self.blue_combos, self.blue_values = self._create_field_group(
            "蓝字词条", self.blue_affix_fields, cols_per_row=3, has_value=True
        )
        container_layout.addWidget(blue_group)

        # 特效组
        self.special_fields = [
            "追加法术伤害",
            "追加物理伤害",
            "抗封印",
            "抗混乱",
            "抗毒",
            "抗昏睡",
            "反击",
            "反震",
            "再生",
            "再转",
        ]
        special_group, self.special_combos, self.special_values = (
            self._create_field_group(
                "特效设置", self.special_fields, cols_per_row=5, has_value=True
            )
        )
        container_layout.addWidget(special_group)

        scroll.setWidget(container)
        self.layout.addWidget(scroll)

    def get_character_equipment(self):
        """获取角色装备"""
        char_id = self.character_id_input.text().strip()
        if not char_id:
            self.show_error("请输入角色ID")
            return
        if not char_id.isdigit():
            self.show_error("角色ID必须为纯数字")
            return

        self.send_command(10, "获取角色装备", {"玩家id": char_id})
        self.add_log(f"已发送获取角色装备请求: {char_id}")

    def _validate_affix_value(
        self,
        field: str,
        value: str,
        error_prefix: str,
        index: int,
        use_field_as_key: bool,
    ) -> int:
        """验证词条数值

        Args:
            field: 字段名
            value: 数值字符串
            error_prefix: 错误提示前缀
            index: 字段索引
            use_field_as_key: 是否使用字段名作为键

        Returns:
            int: 转换后的整数数值

        Raises:
            ValueError: 当数值不是纯数字时
        """
        if not value.isdigit():
            field_id = field if use_field_as_key else index
            raise ValueError(f"{error_prefix}{field_id}数值必须为纯数字")
        return int(value)

    def _collect_single_affix(
        self,
        field: str,
        combos: dict,
        values: dict,
        key_name: str,
        error_prefix: str,
        index: int,
        use_field_as_key: bool,
    ) -> Optional[Tuple]:
        """收集单个词条数据

        Args:
            field: 字段名
            combos: 下拉框字典
            values: 输入框字典
            key_name: 数据键名
            error_prefix: 错误提示前缀
            index: 字段索引
            use_field_as_key: 是否使用字段名作为键

        Returns:
            tuple: (键, 数据字典) 或 None
        """
        name = combos[field].currentText().strip()
        value = values[field].text().strip()

        if name and value:
            validated_value = self._validate_affix_value(
                field, value, error_prefix, index, use_field_as_key
            )
            key = field if use_field_as_key else index
            data_dict = {key_name: name, "数值": validated_value}
            values[field].clear()
            return key, data_dict

        return None

    def _collect_affix_data(
        self,
        fields: list,
        combos: dict,
        values: dict,
        error_prefix: str,
        key_name: str,
        use_field_as_key: bool = False,
    ) -> dict:
        """收集词条数据的通用方法 - 重构后的简化版本

        Args:
            fields: 字段列表
            combos: 下拉框字典
            values: 输入框字典
            error_prefix: 错误提示前缀
            key_name: 数据键名（如"属性"、"词条"、"特效"）
            use_field_as_key: 是否使用字段名作为键（主属性用True，其他用索引）

        Returns:
            收集到的数据字典

        Raises:
            ValueError: 当数值不是纯数字时
        """
        data = {}
        for i, field in enumerate(fields, 1):
            result = self._collect_single_affix(
                field, combos, values, key_name, error_prefix, i, use_field_as_key
            )
            if result:
                key, data_dict = result
                data[key] = data_dict

        return data

    def modify_affixes(self):
        """修改词条 - 重构后的简化版本"""
        char_id = self.character_id_input.text().strip()
        if not char_id:
            self.show_error("请输入角色ID")
            return
        if not char_id.isdigit():
            self.show_error("角色ID必须为纯数字")
            return

        try:
            # 定义要收集的数据组
            affix_groups = [
                (
                    "主属性",
                    self.main_attr_fields,
                    self.main_attr_combos,
                    self.main_attr_values,
                    "主属性",
                    "属性",
                    True,
                ),
                (
                    "绿字",
                    self.green_affix_fields,
                    self.green_combos,
                    self.green_values,
                    "绿字",
                    "词条",
                    False,
                ),
                (
                    "蓝字",
                    self.blue_affix_fields,
                    self.blue_combos,
                    self.blue_values,
                    "蓝字",
                    "词条",
                    False,
                ),
                (
                    "特效",
                    self.special_fields,
                    self.special_combos,
                    self.special_values,
                    "特效",
                    "特效",
                    False,
                ),
            ]

            # 收集所有修改数据
            modify_data = {}
            for (
                group_name,
                fields,
                combos,
                values,
                prefix,
                key_name,
                use_field,
            ) in affix_groups:
                data = self._collect_affix_data(
                    fields, combos, values, prefix, key_name, use_field
                )
                modify_data[group_name] = data

            # 检查是否有数据要修改
            if not any(modify_data.values()):
                self.show_error("没有输入任何修改数据")
                return

            self.send_command(
                10, "定制词条", {"玩家id": char_id, "修改数据": modify_data}
            )
            self.add_log(f"已发送定制词条请求: {char_id}")

        except ValueError as e:
            self.show_error(str(e))

    def add_log(self, message: str):
        """添加日志"""
        print(f"[定制词条] {message}")

    def show_error(self, message: str):
        """显示错误信息框"""
        self.show_error_message(message)

    def set_client(self, client):
        """设置网络客户端"""
        super().set_client(client)
        # 移除on_receive设置，由MainWindow统一处理
