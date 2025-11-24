#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号充值组合模块 - Discord风格
整合账号操作和充值操作功能
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGridLayout,
    QFrame,
    QTabWidget,
    QComboBox,
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


class CategoryCard(QFrame):
    """分类卡片 - 带标题和图标"""

    def __init__(self, title="", icon="", color="#5865F2", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: #2B2D31;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        # 标题行
        if title:
            header = QHBoxLayout()
            header.setSpacing(8)

            title_label = QLabel(f"{icon} {title}" if icon else title)
            title_label.setStyleSheet(
                f"""
                QLabel {{
                    color: {color};
                    font-size: 14px;
                    font-weight: 700;
                }}
            """
            )
            header.addWidget(title_label)
            header.addStretch()

            layout.addLayout(header)

        self.content_layout = QGridLayout()
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)


class CompactButton(QPushButton):
    """紧凑型操作按钮"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFont(QFont("Microsoft YaHei", 9))
        self.setMinimumHeight(32)
        self.setMinimumWidth(90)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            """
            QPushButton {
                background-color: #383A40;
                color: #DCDDDE;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #5865F2;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4752C4;
            }
        """
        )


class InputRow(QWidget):
    """输入行组件"""

    def __init__(self, label="", placeholder="", width=None, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        if label:
            lbl = QLabel(label)
            lbl.setMinimumWidth(70)
            lbl.setStyleSheet(
                """
                QLabel {
                    color: #B5BAC1;
                    font-size: 13px;
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


class AccountRechargeModule(BaseModule):
    """账号充值组合模块 - 全新Discord风格设计"""

    def __init__(self, client=None):
        super().__init__(client)
        self.main_window = None

    def set_main_window(self, main_window):
        self.main_window = main_window

    def get_character_id(self) -> str:
        if self.main_window and hasattr(self.main_window, "get_player_id"):
            return self.main_window.get_player_id()
        return ""

    def validate_character_id(self) -> bool:
        if self.main_window and hasattr(self.main_window, "validate_player_id"):
            return self.main_window.validate_player_id()
        return False

    def init_ui(self):
        """初始化界面 - 全新设计"""
        self.setStyleSheet("background-color: #202225; border-radius: 4px;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        # ========== 顶部标题栏 ==========
        title_bar = QWidget()
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(16)

        title = QLabel("💳 账号充值管理")
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

        subtitle = QLabel("管理玩家账号与充值服务")
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

        # ========== 主内容区域 ==========
        content = QHBoxLayout()
        content.setSpacing(20)

        # 左侧：控制面板
        left_panel = QVBoxLayout()
        left_panel.setSpacing(16)

        # 充值控制面板
        recharge_control = self._create_recharge_control()
        left_panel.addWidget(recharge_control)

        # 账号控制面板
        account_control = self._create_account_control()
        left_panel.addWidget(account_control)

        left_panel.addStretch()

        # 右侧：操作区域
        right_panel = QVBoxLayout()
        right_panel.setSpacing(16)

        # 选项卡
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget::pane {
                background-color: transparent;
                border: none;
            }
            QTabBar::tab {
                background-color: #2B2D31;
                color: #8E9297;
                padding: 10px 20px;
                margin-right: 6px;
                border-radius: 6px 6px 0 0;
                font-weight: 600;
                min-width: 100px;
            }
            QTabBar::tab:selected {
                background-color: #5865F2;
                color: #FFFFFF;
            }
            QTabBar::tab:hover:!selected {
                background-color: #383A40;
                color: #DCDDDE;
            }
        """
        )

        self._create_recharge_operations()
        self._create_account_operations()

        right_panel.addWidget(self.tab_widget)

        content.addLayout(left_panel, 1)
        content.addLayout(right_panel, 2)

        main_layout.addLayout(content)

    def _create_recharge_control(self):
        """创建充值控制面板"""
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #2B2D31;
                border-radius: 10px;
            }
        """
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # 标题
        title = QLabel("💰 充值控制")
        title.setStyleSheet(
            """
            QLabel {
                color: #F2F3F5;
                font-size: 16px;
                font-weight: 700;
            }
        """
        )
        layout.addWidget(title)

        # 充值金额
        self.amount_row = InputRow("充值金额", "输入金额", 200)
        layout.addWidget(self.amount_row)

        # GM等级
        gm_layout = QHBoxLayout()
        gm_layout.setSpacing(12)

        gm_label = QLabel("GM等级")
        gm_label.setMinimumWidth(70)
        gm_label.setStyleSheet("color: #B5BAC1; font-size: 13px; font-weight: 600;")
        gm_layout.addWidget(gm_label)

        self.gm_level_combo = DiscordComboBox()
        for i in range(8):
            self.gm_level_combo.addItem(f"GM{i}")
        self.gm_level_combo.setMaximumWidth(120)
        gm_layout.addWidget(self.gm_level_combo)
        gm_layout.addStretch()

        layout.addLayout(gm_layout)

        # 八卦设置
        bagua_title = QLabel("☯️ 八卦设置")
        bagua_title.setStyleSheet("color: #DCDDDE; font-size: 13px; font-weight: 600;")
        layout.addWidget(bagua_title)

        bagua_grid = QGridLayout()
        bagua_grid.setSpacing(6)

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

        for i, (text, callback) in enumerate(self.bagua_buttons):
            r, c = divmod(i, 4)
            btn = CompactButton(text)
            btn.setFixedWidth(50)
            btn.clicked.connect(callback)
            bagua_grid.addWidget(btn, r, c)

        layout.addLayout(bagua_grid)

        return frame

    def _create_account_control(self):
        """创建账号控制面板"""
        frame = QFrame()
        frame.setStyleSheet(
            """
            QFrame {
                background-color: #2B2D31;
                border-radius: 10px;
            }
        """
        )

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        # 标题
        title = QLabel("👤 账号控制")
        title.setStyleSheet(
            """
            QLabel {
                color: #F2F3F5;
                font-size: 16px;
                font-weight: 700;
            }
        """
        )
        layout.addWidget(title)

        # 账号输入
        self.account_row = InputRow("账号名称", "输入账号", 200)
        layout.addWidget(self.account_row)

        # 新密码
        self.password_row = InputRow("新密码", "输入新密码", 200)
        self.password_row.input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password_row)

        # 称谓
        self.title_row = InputRow("角色称谓", "输入称谓名称", 200)
        layout.addWidget(self.title_row)

        # 快捷操作
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)

        pwd_btn = DiscordButton("修改密码", "warning")
        pwd_btn.setFixedHeight(32)
        pwd_btn.clicked.connect(self.on_change_password)
        quick_layout.addWidget(pwd_btn)

        title_btn = DiscordButton("给予称谓", "primary")
        title_btn.setFixedHeight(32)
        title_btn.clicked.connect(self.on_give_title)
        quick_layout.addWidget(title_btn)

        layout.addLayout(quick_layout)

        return frame

    def _create_recharge_operations(self):
        """创建充值操作选项卡"""
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")

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
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #1A1B1E;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover { background: #232428; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """
        )

        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setSpacing(12)

        # 货币充值
        currency_card = CategoryCard("货币充值", "💰", "#FEE75C")
        self._add_buttons_to_card(
            currency_card,
            [
                ("充值仙玉", self.on_recharge_xy),
                ("充值点卡", self.on_recharge_dk),
                ("充值银子", self.on_recharge_yz),
                ("充值储备", self.on_recharge_cc),
            ],
            4,
        )
        layout.addWidget(currency_card)

        # 经验与技能
        skill_card = CategoryCard("经验 & 技能", "⚡", "#57F287")
        self._add_buttons_to_card(
            skill_card,
            [
                ("充值经验", self.on_recharge_jy),
                ("充值累充", self.on_recharge_lc),
                ("打造熟练", self.on_recharge_dz),
                ("裁缝熟练", self.on_recharge_cf),
                ("炼金熟练", self.on_recharge_lj),
                ("淬灵熟练", self.on_recharge_cl),
            ],
            3,
        )
        layout.addWidget(skill_card)

        # 帮派与积分
        faction_card = CategoryCard("帮派 & 积分", "🏆", "#EB459E")
        self._add_buttons_to_card(
            faction_card,
            [
                ("充值帮贡", self.on_recharge_bg),
                ("充值门贡", self.on_recharge_mg),
                ("活跃积分", self.on_recharge_hy),
                ("比武积分", self.on_recharge_bi),
            ],
            4,
        )
        layout.addWidget(faction_card)

        # GM功能
        gm_card = CategoryCard("GM功能", "👑", "#5865F2")
        self._add_buttons_to_card(
            gm_card,
            [
                ("充值GM等级", self.on_recharge_gm_level),
                ("充值GM币", self.on_recharge_gm_coin),
                ("充值记录", self.on_recharge_record),
            ],
            3,
        )
        layout.addWidget(gm_card)

        layout.addStretch()

        scroll.setWidget(content)

        tab_layout = QVBoxLayout(tab)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.addWidget(scroll)

        self.tab_widget.addTab(tab, "💰 充值服务")

    def _create_account_operations(self):
        """创建账号操作选项卡"""
        tab = QWidget()
        tab.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)

        # 信息查询
        info_card = CategoryCard("信息查询", "🔍", "#5865F2")
        self._add_buttons_to_card(
            info_card,
            [
                ("玩家信息", self.on_player_info),
                ("发送路费", self.on_send_travel_fee),
            ],
            2,
        )
        layout.addWidget(info_card)

        # 战斗控制
        battle_card = CategoryCard("战斗控制", "⚔️", "#FEE75C")
        self._add_buttons_to_card(
            battle_card,
            [
                ("踢出战斗", self.on_kick_battle),
                ("强制下线", self.on_force_offline),
            ],
            2,
        )
        layout.addWidget(battle_card)

        # 账号管理
        manage_card = CategoryCard("账号管理", "🔐", "#ED4245")
        self._add_buttons_to_card(
            manage_card,
            [
                ("封禁账号", self.on_ban_account),
                ("解封账号", self.on_unban_account),
                ("封禁IP", self.on_ban_ip),
                ("解封IP", self.on_unban_ip),
            ],
            2,
        )
        layout.addWidget(manage_card)

        # 权限管理
        permission_card = CategoryCard("权限管理", "⚙️", "#57F287")
        self._add_buttons_to_card(
            permission_card,
            [
                ("开通管理", self.on_open_admin),
                ("关闭管理", self.on_close_admin),
            ],
            2,
        )
        layout.addWidget(permission_card)

        layout.addStretch()

        self.tab_widget.addTab(tab, "👤 账号管理")

    def _add_buttons_to_card(self, card, buttons, cols):
        """向卡片添加按钮"""
        for i, (text, callback) in enumerate(buttons):
            r, c = divmod(i, cols)
            btn = CompactButton(text)
            btn.clicked.connect(callback)
            card.content_layout.addWidget(btn, r, c)

    # ========== 充值操作 ==========
    def on_recharge_xy(self):
        self._send_recharge("充值仙玉")

    def on_recharge_dk(self):
        self._send_recharge("充值点卡")

    def on_recharge_yz(self):
        self._send_recharge("充值银子")

    def on_recharge_cc(self):
        self._send_recharge("充值储备")

    def on_recharge_jy(self):
        self._send_recharge("充值经验")

    def on_recharge_lc(self):
        self._send_recharge("充值累充")

    def on_recharge_bg(self):
        self._send_recharge("充值帮贡")

    def on_recharge_mg(self):
        self._send_recharge("充值门贡")

    def on_recharge_dz(self):
        self._send_recharge("打造熟练")

    def on_recharge_cf(self):
        self._send_recharge("裁缝熟练")

    def on_recharge_lj(self):
        self._send_recharge("炼金熟练")

    def on_recharge_cl(self):
        self._send_recharge("淬灵熟练")

    def on_recharge_hy(self):
        self._send_recharge("活跃积分")

    def on_recharge_bi(self):
        self._send_recharge("比武积分")

    def on_recharge_gm_level(self):
        account_id = self.get_character_id()
        amount = self.amount_row.text().strip()
        gm_level = self.gm_level_combo.currentText()

        if not account_id or not amount:
            self.show_error_message("请输入角色ID和充值金额")
            return

        if not gm_level.startswith("GM"):
            self.show_error_message("GM等级格式错误")
            return

        try:
            if int(gm_level[2:]) > 7:
                self.show_error_message("GM等级不能超过7")
                return
        except:
            self.show_error_message("GM等级格式错误")
            return

        self.send_command(
            2, "充值GM等级", {"玩家id": account_id, "数额": amount, "GM等级": gm_level}
        )

    def on_recharge_gm_coin(self):
        self._send_recharge("充值GM币")

    def on_recharge_record(self):
        account_id = self.get_character_id()
        if not account_id:
            self.show_error_message("请输入角色ID")
            return

        self.send_command(2, "充值记录", {"玩家id": account_id, "数额": ""})

    def _send_recharge(self, command: str):
        account_id = self.get_character_id()
        amount = self.amount_row.text().strip()

        if not account_id or not amount:
            self.show_error_message("请输入角色ID和充值金额")
            return

        self.send_command(2, command, {"玩家id": account_id, "数额": amount})

    # ========== 八卦操作 ==========
    def on_bagua_qian(self):
        self._send_bagua("乾")

    def on_bagua_xun(self):
        self._send_bagua("巽")

    def on_bagua_kan(self):
        self._send_bagua("坎")

    def on_bagua_gen(self):
        self._send_bagua("艮")

    def on_bagua_kun(self):
        self._send_bagua("坤")

    def on_bagua_zhen(self):
        self._send_bagua("震")

    def on_bagua_li(self):
        self._send_bagua("离")

    def on_bagua_dui(self):
        self._send_bagua("兑")

    def _send_bagua(self, bagua_name: str):
        self.send_command(2, "八卦设置", {"数额": bagua_name})

    # ========== 账号操作 ==========
    def on_player_info(self):
        self._send_account_cmd("玩家信息", "角色ID")

    def on_send_travel_fee(self):
        account = self.account_row.text().strip()
        player_id = self.get_character_id()

        if not account or not player_id:
            self.show_error_message("请输入账号和角色ID")
            return

        self.send_command(3, "发送路费", {"账号": account, "玩家id": player_id})

    def on_kick_battle(self):
        self._send_account_cmd("踢出战斗", "角色ID")

    def on_force_offline(self):
        self._send_account_cmd("强制下线", "角色ID")

    def on_ban_account(self):
        self._send_account_cmd("封禁账号", "账号")

    def on_unban_account(self):
        self._send_account_cmd("解封账号", "账号")

    def on_ban_ip(self):
        self._send_account_cmd("封禁IP", "账号")

    def on_unban_ip(self):
        self._send_account_cmd("解封IP", "账号")

    def on_open_admin(self):
        self._send_account_cmd("开通管理", "账号")

    def on_close_admin(self):
        self._send_account_cmd("关闭管理", "账号")

    def on_change_password(self):
        account = self.account_row.text().strip()
        password = self.password_row.text().strip()

        if not account or not password:
            self.show_error_message("请输入账号和新密码")
            return

        self.send_command(3, "修改密码", {"账号": account, "密码": password})

    def on_give_title(self):
        account_id = self.get_character_id()
        title = self.title_row.text().strip()

        if not account_id or not title:
            self.show_error_message("请输入角色ID和称谓名称")
            return

        self.send_command(3, "给予称谓", {"玩家id": account_id, "坐骑名称": title})

    def _send_account_cmd(self, command: str, id_type: str):
        if id_type == "角色ID":
            value = self.get_character_id()
        else:
            value = self.account_row.text().strip()

        if not value:
            self.show_error_message(f"请输入{id_type}")
            return

        data_key = "玩家id" if id_type == "角色ID" else "账号"
        self.send_command(3, command, {data_key: value})

    def set_client(self, client):
        super().set_client(client)
