#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMTools - Discord风格主窗口（精简版）
两栏布局：服务器栏（固定72px）| 内容区（固定968px）
- 移除频道列表
- 顶部右侧显示"管理员:xxx(在线) | 玩家ID 标签+输入框"
- 优化自定义标题栏
- 支持在顶部栏和服务器栏拖动移动窗口
- 玩家ID历史记录支持单项删除和全部清空
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStackedWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QScrollArea,
    QComboBox,
    QListView,
    QStyledItemDelegate,
    QListWidget,
    QListWidgetItem,
    QSizePolicy,
    QMenu,
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import (
    Qt,
    pyqtSignal,
    QEvent,
    QModelIndex,
    QRect,
    QAbstractListModel,
    QSize,
)
from PyQt6.QtGui import QFont, QColor, QPen, QPainter

from modules.account_recharge_module import AccountRechargeModule
from modules.game_module import GameModule
from modules.character_module import CharacterModule
from modules.pet_module import PetModule
from modules.gift_module import GiftModule
from modules.equipment_module import EquipmentModule
from modules.api_manager import APIManager
from ui.api_service_page import APIServicePage


class ServerButton(QPushButton):
    """Discord风格服务器按钮（圆形）"""

    def __init__(self, icon, tooltip="", parent=None):
        super().__init__(icon, parent)
        self.setFixedSize(48, 48)
        self.setToolTip(tooltip)
        self.setFont(QFont("Segoe UI Emoji", 20))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.is_active = False
        self.update_style()

    def update_style(self):
        if self.is_active:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #5865F2;
                    color: white;
                    border: none;
                    border-radius: 16px;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #36393F;
                    color: #DCDDDE;
                    border: none;
                    border-radius: 24px;
                }
                QPushButton:hover {
                    background-color: #5865F2;
                    color: white;
                    border-radius: 16px;
                }
            """
            )

    def set_active(self, active):
        self.is_active = active
        self.update_style()


class ServerBar(QFrame):
    """Discord风格服务器栏（最左侧）"""

    server_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = []
        self.current_index = 0
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("ServerBar")
        self.setFixedWidth(72)
        self.setStyleSheet(
            """
            #ServerBar {
                background-color: #202225;
                border: none;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Home按钮
        home_btn = ServerButton("🏠", "主页")
        home_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #5865F2;
                color: white;
                border: none;
                border-radius: 16px;
            }
        """
        )
        home_btn.clicked.connect(lambda: self.switch_server(-1))
        layout.addWidget(home_btn)

        # 分隔线
        separator = QFrame()
        separator.setFixedHeight(2)
        separator.setStyleSheet("background-color: #36393F;")
        layout.addWidget(separator)

        # 功能模块按钮
        servers = [
            ("💰", "账号充值"),
            ("🎮", "游戏管理"),
            ("👤", "角色管理"),
            ("🐾", "宝宝管理"),
            ("🎁", "赠送道具"),
            ("⚔️", "定制装备"),
        ]
        for i, (icon, tooltip) in enumerate(servers):
            btn = ServerButton(icon, tooltip)
            btn.clicked.connect(lambda checked, idx=i: self.switch_server(idx))
            layout.addWidget(btn)
            self.buttons.append(btn)

        layout.addStretch()

        # API 服务按钮
        api_btn = ServerButton("☁️", "API 服务")
        api_btn.clicked.connect(lambda: self.switch_server(999)) # 使用特殊 ID 999
        layout.addWidget(api_btn)
        self.buttons.append(api_btn)

        # 设置按钮
        settings_btn = ServerButton("⚙️", "设置")
        settings_btn.clicked.connect(self.open_settings)
        layout.addWidget(settings_btn)

    def switch_server(self, index):
        if index == -1:  # Home
            self.server_changed.emit(-1)
            for btn in self.buttons:
                btn.set_active(False)
        else:
            self.current_index = index
            for i, btn in enumerate(self.buttons):
                # 检查按钮是否对应当前索引
                # 注意：API按钮是最后一个，索引是 len(self.buttons)-1，但我们传的是 999
                # 这里需要特殊处理
                if index == 999:
                    btn.set_active(i == len(self.buttons) - 1)
                else:
                    # 普通模块按钮
                    if i < len(self.buttons) - 1: # 排除API按钮
                        btn.set_active(i == index)
                    else:
                        btn.set_active(False)
            self.server_changed.emit(index)

    def open_settings(self):
        """打开设置菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #2B2D31;
                color: #B9BBBE;
                border: 1px solid #1E1F22;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 8px 24px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #5865F2;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background-color: #3F4147;
                margin: 4px 0;
            }
            QMenu::item:disabled {
                color: #4F545C;
            }
        """
        )

        # 关于
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about_window)
        menu.addAction(about_action)

        # 退出
        exit_action = QAction("退出", self)
        from PyQt6.QtWidgets import QApplication
        exit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(exit_action)

        menu.addSeparator()

        # 版本号
        version_action = QAction("版本号: v1.0.0", self)
        version_action.setEnabled(False)
        menu.addAction(version_action)

        # 在按钮位置显示菜单
        sender = self.sender()
        if sender:
            pos = sender.mapToGlobal(sender.rect().topRight())
            menu.exec(pos)

    def show_about_window(self):
        """显示关于窗口"""
        from ui.about_window import AboutWindow
        
        window = AboutWindow(self)
        window.exec()

    def showPopup(self):
        """显示自定义弹出列表 - 重构后的简化版本"""

class WindowControls(QFrame):
    """自定义标题栏（优化版）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setFixedHeight(36)
        self.setStyleSheet(
            """
            QFrame { background-color: #2B2D31; }
            QPushButton {
                background-color: transparent;
                border: none;
                color: #B9BBBE;
                font-size: 14px;
                padding: 0 8px;
            }
            QPushButton:hover { color: white; }
        """
        )

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(6)

        # 应用标题（左侧）
        self.title_label = QLabel("GMTools")
        self.title_label.setStyleSheet("color: #DCDDDE;")
        self.title_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        layout.addWidget(self.title_label)
        layout.addStretch()

        # 最小化
        min_btn = QPushButton("—")
        min_btn.setFixedSize(24, 24)
        min_btn.clicked.connect(lambda: self.window().showMinimized())
        layout.addWidget(min_btn)

        # 最大化/还原
        self.max_btn = QPushButton("□")
        self.max_btn.setFixedSize(24, 24)
        self.max_btn.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.max_btn)

        # 关闭
        close_btn = QPushButton("×")
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet(
            """
            QPushButton { color: #B9BBBE; }
            QPushButton:hover { color: #ED4245; }
        """
        )
        close_btn.clicked.connect(lambda: self.window().close())
        layout.addWidget(close_btn)

        self.is_maximized = False

    def toggle_maximize(self):
        # 允许垂直方向最大化/还原（宽度不强制改变）
        if self.is_maximized:
            self.window().showNormal()
            self.max_btn.setText("□")
        else:
            self.window().showMaximized()
            self.max_btn.setText("❐")
        self.is_maximized = not self.is_maximized


class HistoryItemWidget(QWidget):
    """历史记录项Widget - 包含文本和删除按钮"""

    delete_clicked = pyqtSignal(str)
    item_clicked = pyqtSignal(str)

    def __init__(self, text, parent=None):
        super().__init__(parent)
        self.text = text
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 4, 4)
        layout.setSpacing(4)

        # ID文本
        self.label = QLabel(self.text)
        self.label.setStyleSheet("color: white; padding: 2px;")
        self.label.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.label, 1)

        # 删除按钮
        self.delete_btn = QPushButton("×")
        self.delete_btn.setFixedSize(20, 20)
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #72767D;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #ED4245;
                background-color: rgba(237, 66, 69, 0.1);
                border-radius: 4px;
            }
        """
        )
        self.delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.text))
        layout.addWidget(self.delete_btn)

    def mousePressEvent(self, event):
        # 点击文本区域选择该项
        if event.button() == Qt.MouseButton.LeftButton:
            self.item_clicked.emit(self.text)
        super().mousePressEvent(event)


class ClearAllWidget(QWidget):
    """清空全部Widget"""

    clear_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)

        self.label = QLabel("🗑️ 清空历史记录")
        self.label.setStyleSheet(
            """
            QLabel {
                color: #ED4245;
                padding: 4px;
                font-weight: bold;
            }
        """
        )
        self.label.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(self.label, 1, Qt.AlignmentFlag.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clear_clicked.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self.setStyleSheet("background-color: rgba(237, 66, 69, 0.1);")
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setStyleSheet("")
        super().leaveEvent(event)


class PlayerIDComboBox(QComboBox):
    """自定义玩家ID下拉框 - 带删除功能和清空全部"""

    item_deleted = pyqtSignal(str)
    history_cleared = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEditable(True)
        self.setMaxVisibleItems(11)  # 最多显示10个历史+1个清空按钮

        # 创建自定义列表
        self.list_widget = QListWidget()
        self.list_widget.setWindowFlags(
            Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint
        )
        self.list_widget.setAttribute(Qt.WidgetAttribute.WA_WindowPropagation)
        self.list_widget.setStyleSheet(
            """
            QListWidget {
                background-color: #202225;
                border: 1px solid #5865F2;
                border-radius: 4px;
                padding: 4px;
                outline: none;
            }
            QListWidget::item {
                background-color: transparent;
                padding: 0;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #40444b;
            }
            QListWidget::item:selected {
                background-color: #5865F2;
            }
        """
        )

    def _get_parent_history(self):
        """获取父级ContentArea的历史记录

        Returns:
            历史记录列表，如果未找到返回None
        """
        parent = self.parent()
        while parent and not hasattr(parent, "_player_id_history"):
            parent = parent.parent()

        if not parent or not hasattr(parent, "_player_id_history"):
            return None

        return parent._player_id_history

    def _add_history_items(self, history: list):
        """添加历史记录项到列表

        Args:
            history: 历史记录列表
        """
        for player_id in history[:10]:  # 最多显示10个
            item = QListWidgetItem(self.list_widget)
            widget = HistoryItemWidget(player_id)
            widget.delete_clicked.connect(self._on_delete_item)
            widget.item_clicked.connect(self._on_select_item)
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)

    def _add_separator_and_clear_button(self):
        """添加分隔线和清空按钮"""
        # 分隔线
        separator_item = QListWidgetItem(self.list_widget)
        separator_widget = QWidget()
        separator_widget.setFixedHeight(1)
        separator_widget.setStyleSheet("background-color: #40444b;")
        separator_item.setSizeHint(QSize(0, 1))
        self.list_widget.addItem(separator_item)
        self.list_widget.setItemWidget(separator_item, separator_widget)

        # 清空全部按钮
        clear_item = QListWidgetItem(self.list_widget)
        clear_widget = ClearAllWidget()
        clear_widget.clear_clicked.connect(self._on_clear_all)
        clear_item.setSizeHint(clear_widget.sizeHint())
        self.list_widget.addItem(clear_item)
        self.list_widget.setItemWidget(clear_item, clear_widget)

    def _position_and_show_popup(self):
        """计算位置并显示弹出列表"""
        self.list_widget.resize(
            self.width(),
            min(
                300, self.list_widget.sizeHintForRow(0) * (self.list_widget.count() + 1)
            ),
        )
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self.list_widget.move(pos)
        self.list_widget.show()
        self.list_widget.installEventFilter(self)

    def showPopup(self):
        """显示自定义弹出列表 - 重构后的简化版本"""
        history = self._get_parent_history()
        if not history:
            return

        self.list_widget.clear()
        self._add_history_items(history)

        if history:
            self._add_separator_and_clear_button()

        self._position_and_show_popup()

    def _on_select_item(self, text):
        """选择历史记录项"""
        self.setCurrentText(text)
        self.list_widget.hide()

    def _on_delete_item(self, text):
        """删除历史记录项"""
        # 通过父级ContentArea删除
        parent = self.parent()
        while parent and not hasattr(parent, "_remove_player_id_from_history"):
            parent = parent.parent()

        if parent and hasattr(parent, "_remove_player_id_from_history"):
            parent._remove_player_id_from_history(text)
            self.item_deleted.emit(text)
            # 刷新列表
            self.list_widget.hide()
            from PyQt6.QtCore import QTimer

            QTimer.singleShot(100, self.showPopup)

    def _on_clear_all(self):
        """清空所有历史记录"""
        # 通过父级ContentArea清空
        parent = self.parent()
        while parent and not hasattr(parent, "_clear_player_id_history"):
            parent = parent.parent()

        if parent and hasattr(parent, "_clear_player_id_history"):
            parent._clear_player_id_history()
            self.history_cleared.emit()
            self.list_widget.hide()

    def eventFilter(self, obj, event):
        """事件过滤器 - 处理点击外部关闭下拉列表"""
        if obj == self.list_widget:
            if event.type() == QEvent.Type.MouseButtonPress:
                if not self.list_widget.rect().contains(event.pos()):
                    self.list_widget.hide()
                    return True
        return super().eventFilter(obj, event)

    def hidePopup(self):
        """隐藏弹出列表"""
        if hasattr(self, "list_widget"):
            self.list_widget.hide()

    def focusOutEvent(self, event):
        """失去焦点时保存到历史记录"""
        # 获取当前文本
        current_text = self.currentText().strip()

        # 调用父类的事件处理
        super().focusOutEvent(event)

        # 如果是有效ID，保存到历史（延迟执行以避免干扰焦点事件）
        if current_text and current_text.isdigit():
            # 通过父级ContentArea保存历史记录
            parent = self.parent()
            while parent and not hasattr(parent, "_add_player_id_to_history"):
                parent = parent.parent()

            if parent and hasattr(parent, "_add_player_id_to_history"):
                # 延迟执行以确保焦点事件已完成
                from PyQt6.QtCore import QTimer

                def save_history():
                    parent._add_player_id_to_history(current_text)
                    # 确保文本不会被清空
                    self.setCurrentText(current_text)

                QTimer.singleShot(50, save_history)

    def _save_history_delayed(self, text: str):
        """延迟保存历史记录

        Args:
            text: 要保存的文本
        """
        parent = self.parent()
        while parent and not hasattr(parent, "_add_player_id_to_history"):
            parent = parent.parent()

        if parent and hasattr(parent, "_add_player_id_to_history"):
            from PyQt6.QtCore import QTimer

            def save_and_keep_text():
                parent._add_player_id_to_history(text)
                self.setCurrentText(text)

            QTimer.singleShot(50, save_and_keep_text)

    def keyPressEvent(self, event):
        """处理键盘按键事件 - 重构后的简化版本"""
        from PyQt6.QtCore import Qt

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            current_text = self.currentText().strip()

            if current_text and current_text.isdigit():
                self._save_history_delayed(current_text)

            super().keyPressEvent(event)
            self.setCurrentText(current_text)
        else:
            super().keyPressEvent(event)


class ContentArea(QFrame):
    """内容展示区域（固定宽度 968px）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._player_id_history = []  # 玩家ID历史记录
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("ContentArea")
        self.setFixedWidth(968)
        self.setStyleSheet(
            """
            #ContentArea {
                background-color: #36393F;
                border: none;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部栏（用于面包屑 + 右侧信息）
        self.topbar = QFrame()
        self.topbar.setFixedHeight(48)
        self.topbar.setStyleSheet(
            """
            QFrame {
                background-color: #36393F;
                border-bottom: 1px solid #202225;
            }
        """
        )
        topbar_layout = QHBoxLayout(self.topbar)
        topbar_layout.setContentsMargins(20, 0, 20, 0)
        topbar_layout.setSpacing(12)

        # 左侧：当前位置
        self.breadcrumb = QLabel("# 欢迎")
        self.breadcrumb.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        self.breadcrumb.setStyleSheet("color: white;")
        topbar_layout.addWidget(self.breadcrumb)
        topbar_layout.addStretch()

        # 右侧：管理员与状态 + 分隔 + 玩家ID
        self.account_label = QLabel("管理员: — (离线)")
        self.account_label.setStyleSheet("color: #DCDDDE;")
        self.account_label.setFont(QFont("Segoe UI", 10))
        topbar_layout.addWidget(self.account_label)

        sep = QLabel("|")
        sep.setStyleSheet("color: #72767D;")
        topbar_layout.addWidget(sep)

        pid_lbl = QLabel("玩家ID")
        pid_lbl.setStyleSheet("color: #B9BBBE;")
        pid_lbl.setFont(QFont("Segoe UI", 10))
        topbar_layout.addWidget(pid_lbl)

        self.api_manager = None
        
        # 使用自定义ComboBox支持历史记录下拉选择
        self.player_id = PlayerIDComboBox(self)
        self.player_id.setPlaceholderText("输入或选择玩家ID")
        self.player_id.setFixedWidth(150)
        self.player_id.setFixedHeight(28)
        self.player_id.setStyleSheet(
            """
            PlayerIDComboBox {
                background-color: #202225;
                color: white;
                border: 1px solid #202225;
                border-radius: 4px;
                padding: 2px 6px;
            }
            PlayerIDComboBox:focus {
                border: 1px solid #5865F2;
            }
            PlayerIDComboBox QLineEdit {
                background-color: transparent;
                color: white;
                border: none;
                padding: 0;
            }
            PlayerIDComboBox::down-arrow {
                width: 12px;
                height: 12px;
                image: none;
                border-left: 4px solid #72767D;
                border-bottom: 4px solid #72767D;
                margin-right: 4px;
            }
            PlayerIDComboBox::drop-down {
                border: none;
                width: 20px;
                background-color: transparent;
            }
        """
        )

        # 连接信号
        self.player_id.item_deleted.connect(
            lambda text: print(f"[INFO] 删除历史记录: {text}")
        )
        self.player_id.history_cleared.connect(lambda: print("[INFO] 清空所有历史记录"))

        # 加载历史记录
        self._load_player_id_history()
        topbar_layout.addWidget(self.player_id)

        layout.addWidget(self.topbar)

        # 内容堆栈
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background-color: #36393F;")

        # 欢迎页
        welcome = self.create_welcome_page()
        self.stack.addWidget(welcome)

        layout.addWidget(self.stack)

    def create_welcome_page(self):
        """创建欢迎页"""
        page = QWidget()
        page.setStyleSheet("background-color: #36393F;")
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(30)

        # 大Logo
        logo = QLabel("🎮")
        logo.setFont(QFont("Segoe UI Emoji", 72))
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet("color: #5865F2;")
        layout.addWidget(logo)

        # 欢迎标题
        title = QLabel("欢迎使用 GMTools")
        title.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: white;")
        layout.addWidget(title)

        # 描述
        desc = QLabel("Discord风格的游戏管理工具")
        desc.setFont(QFont("Segoe UI", 14))
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("color: #B9BBBE;")
        layout.addWidget(desc)

        # API 文档按钮
        self.api_docs_btn = QPushButton("打开 API 文档")
        self.api_docs_btn.setFixedSize(200, 44)
        self.api_docs_btn.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.api_docs_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.api_docs_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #5865F2;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background-color: #4752C4; }
            QPushButton:pressed { background-color: #3C45A5; }
        """
        )
        self.api_docs_btn.clicked.connect(self.open_api_docs)
        layout.addWidget(self.api_docs_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        return page

    def set_api_manager(self, api_manager):
        self.api_manager = api_manager

    def open_api_docs(self):
        if self.api_manager:
            from PyQt6.QtGui import QDesktopServices
            from PyQt6.QtCore import QUrl
            url = f"http://{self.api_manager.host}:{self.api_manager.port}/docs"
            QDesktopServices.openUrl(QUrl(url))
        else:
            print("[WARN] API Manager not initialized")

    def add_module(self, widget):
        self.stack.addWidget(widget)

    def switch_to(self, index):
        self.stack.setCurrentIndex(index)

    def set_breadcrumb(self, text):
        self.breadcrumb.setText(f"# {text}")

    def set_account_display(self, account: str, connected: bool):
        status = "在线" if connected else "离线"
        color = "#3BA55D" if connected else "#ED4245"
        account_disp = account or "—"
        self.account_label.setText(
            f"管理员: {account_disp} (<span style='color:{color};'>{status}</span>)"
        )
        self.account_label.setTextFormat(Qt.TextFormat.RichText)

    def get_player_id(self):
        return self.player_id.currentText().strip()

    def _add_player_id_to_history(self, player_id):
        """添加玩家ID到历史记录"""
        from config.config_manager import ConfigManager
        ConfigManager().add_player_history(player_id)
        self._player_id_history = ConfigManager().get_player_history()
        print(
            f"[INFO] 添加历史记录: {player_id}, 当前数量: {len(self._player_id_history)}"
        )

    def _remove_player_id_from_history(self, player_id):
        """从历史记录中删除指定ID"""
        from config.config_manager import ConfigManager
        ConfigManager().remove_player_history(player_id)
        self._player_id_history = ConfigManager().get_player_history()
        print(
            f"[INFO] 删除历史记录: {player_id}, 剩余数量: {len(self._player_id_history)}"
        )

    def _clear_player_id_history(self):
        """清空所有历史记录"""
        from config.config_manager import ConfigManager
        ConfigManager().clear_player_history()
        self._player_id_history = []
        print("[INFO] 清空所有历史记录")

    def _load_player_id_history(self):
        """加载玩家ID历史记录"""
        from config.config_manager import ConfigManager
        self._player_id_history = ConfigManager().get_player_history()
        print(f"[INFO] 加载历史记录完成，数量: {len(self._player_id_history)}")

    def _save_player_id_history(self):
        """保存玩家ID历史记录 - 已废弃，由ConfigManager接管"""
        pass


# 后续的DiscordMainWindow类保持不变...
class DiscordMainWindow(QMainWindow):
    """GMTools - Discord两栏式主窗口"""

    logout_signal = pyqtSignal()
    show_result_signal = pyqtSignal(int, str)  # seq_no, message
    fill_data_signal = pyqtSignal(dict)  # parsed data
    fill_pet_data_signal = pyqtSignal(dict)  # pet data
    fill_recharge_types_signal = pyqtSignal(list)  # recharge types data
    fill_card_numbers_signal = pyqtSignal(list)  # card numbers data
    fill_mount_data_signal = pyqtSignal(dict)  # mount data

    def __init__(self, client=None, parent=None):
        super().__init__(parent)
        self.client = client
        self.account_name = ""
        self._connected = False
        self._drag_pos = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("GMTools")
        self.setMinimumHeight(720)
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        # 连接信号
        self.show_result_signal.connect(self._show_result_message)
        self.fill_data_signal.connect(self._fill_character_data)
        self.fill_pet_data_signal.connect(self._fill_pet_data)
        self.fill_recharge_types_signal.connect(self._fill_recharge_types)
        self.fill_card_numbers_signal.connect(self._fill_card_numbers)
        self.fill_mount_data_signal.connect(self._fill_mount_data)

        # 主容器
        central = QWidget()
        central.setObjectName("CentralWidget")
        self.setCentralWidget(central)

        # 主布局
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部自定义标题栏
        self.window_controls = WindowControls()
        main_layout.addWidget(self.window_controls)

        # 两栏布局容器：服务器栏（固定72） + 内容区（固定968）
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 服务器栏（最左侧 72px）
        self.server_bar = ServerBar()
        self.server_bar.server_changed.connect(self.on_server_changed)
        content_layout.addWidget(self.server_bar)

        # 内容区域（固定 968px）
        self.content_area = ContentArea()
        content_layout.addWidget(self.content_area)

        # 右侧留白（随着窗口宽度变化）
        spacer = QWidget()
        spacer.setStyleSheet("background-color: #313338;")
        content_layout.addWidget(spacer, 1)

        main_layout.addWidget(content, 1)

        # 初始化模块
        self.init_modules()

        # 设置初始状态
        self.on_server_changed(-1)  # 显示主页

        # 安装拖动事件过滤（标题栏 + 顶部工具栏 + 服务器栏可拖动）
        self.window_controls.installEventFilter(self)
        self.content_area.topbar.installEventFilter(self)
        self.server_bar.installEventFilter(self)

    def _handle_drag_event(self, event) -> bool:
        """处理拖动事件

        Args:
            event: 事件对象

        Returns:
            bool: 是否处理了事件
        """
        if (
            event.type() == QEvent.Type.MouseButtonPress
            and event.button() == Qt.MouseButton.LeftButton
        ):
            self._drag_pos = event.globalPosition().toPoint() - self.pos()
            return True
        elif (
            event.type() == QEvent.Type.MouseMove
            and event.buttons() & Qt.MouseButton.LeftButton
            and self._drag_pos
        ):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            return True
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self._drag_pos = None
            return True
        return False

    def eventFilter(self, obj, event):
        """事件过滤器 - 重构后的简化版本"""
        # 在标题栏、内容顶部栏、服务器栏上按下左键可拖动窗口
        if obj in (self.window_controls, self.content_area.topbar, self.server_bar):
            if self._handle_drag_event(event):
                return True
        return super().eventFilter(obj, event)

    def init_modules(self):
        """初始化模块（兼容 init_ui/setup_ui）"""
        self.modules = []
        module_classes = [
            AccountRechargeModule,
            GameModule,
            CharacterModule,
            PetModule,
            GiftModule,
            EquipmentModule,
        ]
        # 欢迎页占 index 0，后续模块从 1 开始
        for ModuleClass in module_classes:
            module = ModuleClass(self.client)
            if hasattr(module, "init_ui") and callable(getattr(module, "init_ui")):
                module.init_ui()
            elif hasattr(module, "setup_ui") and callable(getattr(module, "setup_ui")):
                module.setup_ui()
            if hasattr(module, "set_main_window"):
                module.set_main_window(self)
            module.set_client(self.client)
            self.content_area.add_module(module)
            self.modules.append(module)

        # 初始化 API 管理器和页面
        self.api_manager = APIManager(self.client)
        self.content_area.set_api_manager(self.api_manager)
        self.api_service_page = APIServicePage(self.api_manager)
        self.content_area.add_module(self.api_service_page)
        if self.api_manager.auto_start:
            self.api_manager.start_service()

    def on_server_changed(self, index):
        """服务器（模块）切换"""
        if index == -1:  # 主页
            self.content_area.switch_to(0)
            self.content_area.set_breadcrumb("欢迎")
        else:
            module_names = [
                "账号充值",
                "游戏管理",
                "角色管理",
                "宝宝管理",
                "赠送道具",
                "定制装备",
            ]
            if 0 <= index < len(module_names):
                name = module_names[index]
                self.content_area.switch_to(index + 1)  # +1 因为第0个是欢迎页
                self.content_area.set_breadcrumb(name)
            elif index == 999: # API 服务
                # API 页面是最后一个添加的，索引是 len(module_names) + 1
                self.content_area.switch_to(len(module_names) + 1)
                self.content_area.set_breadcrumb("API 服务")

    def set_client(self, client):
        self.client = client
        for module in self.modules:
            module.set_client(client)

    def set_account(self, account):
        """设置当前账号并展示于右上角"""
        self.account_name = account
        self.content_area.set_account_display(account, self._connected)
        # 同时设置各个模块的账号，以便发送命令时使用
        for module in self.modules:
            module._current_account = account

    def update_connection_status(self, connected):
        """更新在线状态显示"""
        self._connected = connected
        self.content_area.set_account_display(self.account_name, connected)

    def get_player_id(self):
        """提供给各模块使用"""
        # 从ContentArea的ComboBox获取当前文本
        return self.content_area.get_player_id()

    def validate_player_id(self):
        pid = self.get_player_id()
        return bool(pid and pid.isdigit())

    def on_receive_data(self, data: dict):
        """接收服务器数据并显示结果"""
        from PyQt6.QtCore import QTimer

        seq_no = data.get("seq_no")
        content = data.get("content", "")

        print(f"[DEBUG] 主窗口收到数据 - 序号: {seq_no}, 内容长度: {len(content)}")

        # 序号10是获取玩家信息的响应，包含复杂数据
        if seq_no == 10:
            if content.startswith("{"):
                # 解析Lua字典格式的数据
                try:
                    parsed_data = self._parse_lua_dict(content)
                    if parsed_data:
                        # 使用信号跨线程调用数据填充
                        self.fill_data_signal.emit(parsed_data)
                except Exception as e:
                    print(f"[ERROR] 解析角色数据失败: {e}")

        # 序号11是获取宝宝信息的响应，返回数组格式的宝宝数据
        if seq_no == 11:
            if content.startswith("{"):
                # 解析Lua数组格式的数据
                try:
                    parsed_data = self._parse_lua_dict(content)
                    if parsed_data:
                        # 使用信号跨线程调用宠物数据填充
                        self.fill_pet_data_signal.emit(parsed_data)
                        print(
                            f"[DEBUG] 解析宝宝数据成功，包含 {len(parsed_data) if isinstance(parsed_data, list) else 0} 只宝宝"
                        )
                except Exception as e:
                    print(f"[ERROR] 解析宝宝数据失败: {e}")

        # 序号12是获取充值类型或获取卡号的响应，返回数组格式的数据
        if seq_no == 12:
            if content.startswith("{"):
                # 解析Lua数组格式的数据
                try:
                    parsed_data = self._parse_lua_dict(content)
                    if parsed_data:
                        # 判断是充值类型还是卡号数据（卡号数据中包含"卡号"键）
                        if "卡号" in parsed_data or "卡号" in str(parsed_data.keys()):
                            # 这是获取卡号的响应
                            card_numbers = []
                            for key, value in parsed_data.items():
                                if key != "卡号" and isinstance(value, str):
                                    # 去掉字符串两端的引号
                                    cleaned_value = value.strip('"').strip("'")
                                    card_numbers.append(cleaned_value)

                            # 无论是否有卡号数据，都发送信号更新显示
                            self.fill_card_numbers_signal.emit(card_numbers)
                            print(
                                f"[DEBUG] 解析卡号完成，包含 {len(card_numbers)} 个卡号"
                            )
                        else:
                            # 这是获取充值类型的响应
                            recharge_types = []
                            for _, value in parsed_data.items():
                                if isinstance(value, str):
                                    # 去掉字符串两端的引号
                                    cleaned_value = value.strip('"').strip("'")
                                    recharge_types.append(cleaned_value)

                            # 只有在充值类型列表不为空时才发送信号
                            if recharge_types:
                                # 使用信号跨线程调用充值类型数据填充
                                self.fill_recharge_types_signal.emit(recharge_types)
                                print(
                                    f"[DEBUG] 解析充值类型成功，包含 {len(recharge_types)} 个类型"
                                )
                            else:
                                print("[DEBUG] 解析到的充值类型列表为空，跳过填充")
                except Exception as e:
                    print(f"[ERROR] 解析seq_no=12数据失败: {e}")

        # 序号14是获取坐骑信息的响应
        if seq_no == 14:
            if content.startswith("{"):
                try:
                    parsed_data = self._parse_lua_dict(content)
                    if parsed_data:
                        self.fill_mount_data_signal.emit(parsed_data)
                except Exception as e:
                    print(f"[ERROR] 解析坐骑数据失败: {e}")

        # 清理内容（去掉颜色代码）
        clean_content = (
            content.replace("#Y/", "")
            .replace("#Y", "")
            .replace("#R/", "")
            .replace("#R", "")
        )

        # 使用信号跨线程调用显示消息框
        self.show_result_signal.emit(seq_no, clean_content)

    def _show_result_message(self, seq_no, clean_content):
        """显示结果消息框"""
        # 智能静默模式：如果有活跃的API请求收集器，说明这是API请求的响应，不弹窗
        import api_main
        if api_main.dispatcher.has_active_collectors():
            print(f"[INFO] (API静默) 收到响应 (序号: {seq_no}): {clean_content}")
            return

        try:
            # 确保窗口在前台并激活
            self.raise_()
            self.activateWindow()

            # 使用DiscordMessageBox显示结果
            try:
                from ui.discord_messagebox import DiscordMessageBox

                result = DiscordMessageBox.show_info(
                    self, f"操作结果 (序号: {seq_no})", clean_content
                )
                
                # 特殊处理：修改宝宝数据成功后自动刷新
                if seq_no == 7 and "修改玩家召唤兽数据完成" in clean_content:
                    print("[DEBUG] 检测到宝宝修改成功，自动刷新宝宝数据")
                    pet_module = self._find_pet_module()
                    if pet_module:
                        # 延迟一点执行，确保消息框完全关闭
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(200, pet_module.get_pet_info)
                        
                # 特殊处理：修改坐骑数据成功后自动刷新
                if seq_no == 7 and "玩家坐骑修改完成" in clean_content:
                    print("[DEBUG] 检测到坐骑修改成功，自动刷新坐骑数据")
                    pet_module = self._find_pet_module()
                    if pet_module:
                        # 延迟一点执行，确保消息框完全关闭
                        from PyQt6.QtCore import QTimer
                        QTimer.singleShot(200, pet_module.get_mount)
                        
            except ImportError:
                # 如果DiscordMessageBox不可用，回退到原来的QMessageBox
                from PyQt6.QtWidgets import QMessageBox

                QMessageBox.information(
                    self, f"操作结果 (序号: {seq_no})", clean_content
                )

        except Exception as e:
            print(f"[ERROR] 显示消息框失败: {e}")

    def _parse_lua_dict(self, lua_str: str) -> dict:
        """解析Lua字典格式字符串为Python字典"""
        import re

        try:
            # 去掉外层大括号
            if lua_str.startswith("{") and lua_str.endswith("}"):
                content = lua_str[1:-1]
            else:
                content = lua_str

            result = {}
            self._parse_dict_content(content, result)
            return result
        except Exception as e:
            print(f"[ERROR] 解析Lua字典失败: {e}")
            return {}

    def _parse_dict_content(self, content: str, result: dict):
        """递归解析字典内容"""
        import re

        # 使用栈来追踪大括号深度
        items = []
        current_key = None
        brace_depth = 0
        in_value = False

        # 按字符遍历，处理嵌套字典
        i = 0
        while i < len(content):
            char = content[i]

            # 跳过空格和逗号
            if char in " \t,":
                i += 1
                continue

            # 遇到等号，开始解析值
            if char == "=":
                # 提取键名
                if current_key is None:
                    # 获取键名（从最近的分隔符或开头到当前位置）
                    start = max(
                        [
                            idx
                            for idx in [0]
                            + [m.end() for m in re.finditer(r"[,]+", content[:i])]
                        ]
                        or [0]
                    )
                    current_key = content[start:i].strip()

                # 跳过等号和空格
                i += 1
                while i < len(content) and content[i] in " \t":
                    i += 1
                continue

            # 遇到大括号，增加深度并提取整个字典值
            if char == "{":
                if brace_depth == 0:
                    # 这是值的开始
                    start = i
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
                if brace_depth == 0:
                    # 这是值的结束
                    value = content[start : i + 1]
                    if current_key:
                        # 递归解析嵌套字典
                        nested_dict = {}
                        self._parse_dict_content(value[1:-1], nested_dict)
                        result[current_key] = nested_dict
                        current_key = None
            else:
                # 普通字符，检查是否为数字或字符串
                if brace_depth == 0 and current_key:
                    # 提取值（到下一个分隔符或结束）
                    match = re.match(r"([^,}]*)", content[i:])
                    if match:
                        value = match.group(1).strip()
                        # 尝试转换为数字
                        try:
                            if value.isdigit():
                                result[current_key] = int(value)
                            else:
                                result[current_key] = (
                                    int(value)
                                    if value.replace("-", "").isdigit()
                                    else value
                                )
                        except:
                            result[current_key] = value
                        current_key = None
                        i += match.end() - 1

            i += 1

    def _fill_character_data(self, data: dict):
        """填充角色数据到UI"""
        try:
            print(f"[DEBUG] 开始填充角色数据，收到数据键: {list(data.keys())}")

            # 查找角色管理模块
            character_module = None
            for module in self.modules:
                if "Character" in module.__class__.__name__:
                    character_module = module
                    break

            if not character_module:
                print("[DEBUG] 未找到角色模块")
                return

            print(f"[DEBUG] 找到角色模块: {character_module.__class__.__name__}")

            # 查找所有QLineEdit
            all_inputs = character_module.findChildren(QLineEdit)

            # 处理InputRow包装的输入框
            try:
                from modules.account_recharge_module import InputRow

                input_rows = character_module.findChildren(InputRow)

                # 合并所有输入框（包括InputRow内部的）
                all_editable_inputs = []
                for inp in all_inputs:
                    all_editable_inputs.append(inp)
                for row in input_rows:
                    all_editable_inputs.append(row.input)
            except:
                all_editable_inputs = all_inputs

            # 填充角色修炼数据（包括玩家等级）
            if "修炼" in data:
                cultivation_data = data["修炼"]
                print(f"[DEBUG] 处理角色修炼数据: {cultivation_data}")

                # 检查CharacterModule是否有预定义的角色修炼输入框字典
                if hasattr(character_module, "cultivation_inputs"):
                    filled_count = 0
                    for skill_name, value in cultivation_data.items():
                        if skill_name == "当前":
                            continue  # 跳过"当前"字段
                        if skill_name in character_module.cultivation_inputs:
                            # 处理字典格式的数据（Lua数组格式）
                            if isinstance(value, dict) and "[1]" in value:
                                actual_value = value["[1]"]  # 取[1]的值
                            elif isinstance(value, list) and len(value) >= 1:
                                actual_value = value[0]  # 取数组第一个值
                            else:
                                actual_value = value
                            input_widget = character_module.cultivation_inputs[
                                skill_name
                            ]
                            input_widget.setText(str(actual_value))
                            filled_count += 1
                            print(f"[DEBUG] 填充角色修炼 {skill_name}: {actual_value}")
                    print(f"[DEBUG] 角色修炼填充完成，成功填充 {filled_count} 项")
                else:
                    print("[DEBUG] CharacterModule没有cultivation_inputs属性")

            # 填充召唤兽修炼数据
            if "bb修炼" in data:
                pet_cultivation_data = data["bb修炼"]
                print(f"[DEBUG] 处理召唤兽修炼数据: {pet_cultivation_data}")

                # 先处理玩家等级（在bb修炼中）
                if "玩家等级" in pet_cultivation_data:
                    player_level = pet_cultivation_data["玩家等级"]
                    if isinstance(player_level, dict) and "[1]" in player_level:
                        level_value = player_level["[1]"]
                    elif isinstance(player_level, list) and len(player_level) >= 1:
                        level_value = player_level[0]
                    else:
                        level_value = player_level

                    # 将玩家等级填充到召唤兽修炼的"玩家等级"输入框
                    if (
                        hasattr(character_module, "pet_cultivation_inputs")
                        and "玩家等级" in character_module.pet_cultivation_inputs
                    ):
                        level_widget = character_module.pet_cultivation_inputs[
                            "玩家等级"
                        ]
                        level_widget.setText(str(level_value))
                        print(f"[DEBUG] 填充玩家等级: {level_value}")

                # 检查CharacterModule是否有预定义的召唤兽修炼输入框字典
                if hasattr(character_module, "pet_cultivation_inputs"):
                    filled_count = 0
                    for skill_name, value in pet_cultivation_data.items():
                        if skill_name == "当前":
                            continue  # 跳过"当前"字段
                        if skill_name == "玩家等级":
                            continue  # 玩家等级已经处理过了
                        if skill_name in character_module.pet_cultivation_inputs:
                            # 处理字典格式的数据（Lua数组格式）
                            if isinstance(value, dict) and "[1]" in value:
                                actual_value = value["[1]"]  # 取[1]的值
                            elif isinstance(value, list) and len(value) >= 1:
                                actual_value = value[0]  # 取数组第一个值
                            else:
                                actual_value = value
                            input_widget = character_module.pet_cultivation_inputs[
                                skill_name
                            ]
                            input_widget.setText(str(actual_value))
                            filled_count += 1
                            print(
                                f"[DEBUG] 填充召唤兽修炼 {skill_name}: {actual_value}"
                            )
                    print(f"[DEBUG] 召唤兽修炼填充完成，成功填充 {filled_count} 项")
                else:
                    print("[DEBUG] CharacterModule没有pet_cultivation_inputs属性")

            # 填充强化技能数据
            if "强化技能" in data:
                enhanced_skills = data["强化技能"]
                print(f"[DEBUG] 处理强化技能数据: {enhanced_skills}")

                # 检查CharacterModule是否有预定义的输入框字典
                if hasattr(character_module, "enhancement_inputs"):
                    filled_count = 0
                    for skill_name, value in enhanced_skills.items():
                        if skill_name in character_module.enhancement_inputs:
                            input_widget = character_module.enhancement_inputs[
                                skill_name
                            ]
                            input_widget.setText(str(value))
                            filled_count += 1
                            print(f"[DEBUG] 填充强化技能 {skill_name}: {value}")
                    print(f"[DEBUG] 强化技能填充完成，成功填充 {filled_count} 项")
                else:
                    print("[DEBUG] CharacterModule没有enhancement_inputs属性")

            # 填充生活技能数据
            if "生活技能" in data:
                life_skills = data["生活技能"]
                print(f"[DEBUG] 处理生活技能数据: {life_skills}")

                # 检查CharacterModule是否有预定义的生活技能输入框字典
                if hasattr(character_module, "life_inputs"):
                    filled_count = 0
                    for skill_name, value in life_skills.items():
                        if skill_name in character_module.life_inputs:
                            input_widget = character_module.life_inputs[skill_name]
                            input_widget.setText(str(value))
                            filled_count += 1
                            print(f"[DEBUG] 填充生活技能 {skill_name}: {value}")
                    print(f"[DEBUG] 生活技能填充完成，成功填充 {filled_count} 项")
                else:
                    print("[DEBUG] CharacterModule没有life_inputs属性")

            print("[DEBUG] 角色数据填充完成")

        except Exception as e:
            print(f"[ERROR] 填充角色数据失败: {e}")

    def _find_pet_module(self):
        """查找宠物管理模块"""
        for module in self.modules:
            if "Pet" in module.__class__.__name__:
                return module
        return None

    def _process_bracket_key(self, key: str, value: any, pet_list: list):
        """处理以[数字]格式的键

        Args:
            key: 键名
            value: 键值
            pet_list: 宝宝列表（用于添加数据）
        """
        print(f"[DEBUG] 找到宝宝数据: {key} -> {value}")
        if isinstance(value, dict) and "名称" in value:
            pet_list.append(value)
        else:
            print(f"[DEBUG] 数据格式异常: {value}")

    def _process_digit_key(self, key: str, value: any, pet_list: list):
        """处理数字键

        Args:
            key: 键名
            value: 键值
            pet_list: 宝宝列表（用于添加数据）
        """
        print(f"[DEBUG] 找到数字键数据: {key} -> {value}")
        if isinstance(value, dict):
            pet_list.append(value)

    def _parse_pet_dict(self, data: dict) -> list:
        """解析宝宝字典数据为列表 - 重构后的简化版本

        处理类似 {[2]={...}, [1]={...}} 或 {1={...}, 2={...}} 的格式
        """
        pet_list = []
        
        # 辅助函数：从键中提取数字用于排序
        def get_key_number(k):
            if k.startswith("[") and k.endswith("]"):
                try:
                    return int(k[1:-1])
                except ValueError:
                    return float('inf')
            elif k.isdigit():
                return int(k)
            return float('inf')

        # 按数字键排序
        try:
            sorted_keys = sorted(data.keys(), key=get_key_number)
        except Exception as e:
            print(f"[WARN] 排序宝宝数据失败: {e}，使用默认顺序")
            sorted_keys = data.keys()

        for key in sorted_keys:
            value = data[key]
            if key.startswith("[") and key.endswith("]"):
                self._process_bracket_key(key, value, pet_list)
            elif key.isdigit():
                self._process_digit_key(key, value, pet_list)

        print(f"[DEBUG] 解析到 {len(pet_list)} 个宝宝数据 (已排序)")
        return pet_list

    def _normalize_pet_data(self, data) -> list:
        """
        标准化宝宝数据为列表格式

        Args:
            data: 字典或列表格式的宝宝数据

        Returns:
            统一的列表格式
        """
        if isinstance(data, dict):
            pet_list = self._parse_pet_dict(data)
            if pet_list:
                return pet_list
            else:
                print(f"[DEBUG] 未找到有效的宝宝数据，使用原始数据")
                return [data]
        elif isinstance(data, list):
            return data
        else:
            return [data]

    def _fill_pet_data(self, data: dict):
        """填充宝宝数据到UI - 重构后的简化版本"""
        try:
            print(f"[DEBUG] 开始填充宝宝数据，数据类型: {type(data)}")
            print(
                f"[DEBUG] 原始数据键: {list(data.keys()) if isinstance(data, dict) else '不是字典'}"
            )

            # 查找宠物管理模块
            pet_module = self._find_pet_module()
            if not pet_module:
                print("[DEBUG] 未找到宠物模块")
                return

            print(f"[DEBUG] 找到宠物模块: {pet_module.__class__.__name__}")

            # 标准化数据为列表格式
            pet_list = self._normalize_pet_data(data)
            print(f"[DEBUG] 处理宝宝列表，共 {len(pet_list)} 只宝宝")

            # 将宝宝数据传递给宠物模块
            pet_module.set_pet_data(pet_list)

        except Exception as e:
            print(f"[ERROR] 填充宝宝数据失败: {e}")
            import traceback

            traceback.print_exc()

    def _fill_recharge_types(self, recharge_types: list):
        """填充充值类型数据到赠送道具模块的下拉框"""
        try:
            print(f"[DEBUG] 开始填充充值类型数据，共 {len(recharge_types)} 个类型")

            # 查找赠送道具模块
            gift_module = None
            for module in self.modules:
                if "Gift" in module.__class__.__name__:
                    gift_module = module
                    break

            if not gift_module:
                print("[DEBUG] 未找到赠送道具模块")
                return

            print(f"[DEBUG] 找到赠送道具模块: {gift_module.__class__.__name__}")

            # 调用模块的方法填充充值类型
            if hasattr(gift_module, "set_recharge_types"):
                gift_module.set_recharge_types(recharge_types)
                print(f"[DEBUG] 成功填充 {len(recharge_types)} 个充值类型")
            else:
                print("[DEBUG] 赠送道具模块没有 set_recharge_types 方法")

        except Exception as e:
            print(f"[ERROR] 填充充值类型数据失败: {e}")
            import traceback

            traceback.print_exc()

    def _fill_card_numbers(self, card_numbers: list):
        """填充卡号数据到赠送道具模块的卡号显示区域"""
        try:
            print(f"[DEBUG] 开始填充卡号数据，共 {len(card_numbers)} 个卡号")

            # 查找赠送道具模块
            gift_module = None
            for module in self.modules:
                if "Gift" in module.__class__.__name__:
                    gift_module = module
                    break

            if not gift_module:
                print("[DEBUG] 未找到赠送道具模块")
                return

            print(f"[DEBUG] 找到赠送道具模块: {gift_module.__class__.__name__}")

            # 调用模块的方法填充卡号
            if hasattr(gift_module, "set_card_numbers"):
                gift_module.set_card_numbers(card_numbers)
                print(f"[DEBUG] 成功填充 {len(card_numbers)} 个卡号")
            else:
                print("[DEBUG] 赠送道具模块没有 set_card_numbers 方法")

        except Exception as e:
            print(f"[ERROR] 填充卡号数据失败: {e}")
            import traceback

            traceback.print_exc()

    def _fill_mount_data(self, data: dict):
        """填充坐骑数据"""
        try:
            pet_module = self._find_pet_module()
            if pet_module and hasattr(pet_module, 'set_mount_data'):
                pet_module.set_mount_data(data)
        except Exception as e:
            print(f"[ERROR] 填充坐骑数据失败: {e}")

    def closeEvent(self, event):
        if self.client:
            self.client._is_closing = True
            self.client.disconnect()
        event.accept()
        
        # 强制完全退出程序
        import os
        os._exit(0)
