"""
GMTools登录界面 - Discord风格优化版
使用PyQt6实现，增强安全性和用户体验
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QApplication,
    QMessageBox,
    QFrame,
    QLabel,
    QGraphicsOpacityEffect,
)
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QObject,
    pyqtSignal,
    QPoint,
    QPropertyAnimation,
    QEasingCurve,
    QSettings,
    QParallelAnimationGroup,
    pyqtProperty,
)
from PyQt6.QtGui import QFont
import sys
import os
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")

# 导入配置
try:
    from config.settings import GM_ACCOUNT, GM_PASSWORD
except ImportError:
    GM_ACCOUNT = ""
    GM_PASSWORD = ""
    logger.warning("无法导入默认配置，使用空值")


class StyleManager:
    """样式管理器 - Discord风格"""

    # Discord 配色方案
    COLORS = {
        "background_primary": "#2f3136",
        "background_secondary": "#36393f",
        "background_tertiary": "#202225",
        "background_modifier_hover": "#40444b",
        "background_modifier_selected": "#4f545c",
        "accent": "#5865F2",
        "accent_hover": "#4752C4",
        "accent_active": "#3c45a5",
        "text_normal": "#dcddde",
        "text_muted": "#72767d",
        "text_link": "#00b0f4",
        "interactive_normal": "#b9bbbe",
        "interactive_hover": "#dcddde",
        "interactive_active": "#ffffff",
        "interactive_muted": "#4f545c",
        "error": "#ed4245",
        "success": "#3ba55c",
        "warning": "#faa61a",
        "info": "#5865F2",
    }

    @classmethod
    def get_input_style(cls) -> str:
        """获取输入框样式"""
        return f"""
            QFrame {{
                background-color: {cls.COLORS['background_tertiary']};
                border: 2px solid transparent;
                border-radius: 4px;
            }}
            QFrame:focus {{
                border: 2px solid {cls.COLORS['accent']};
            }}
        """

    @classmethod
    def get_button_style(cls, style_type: str = "primary") -> str:
        """获取按钮样式"""
        if style_type == "primary":
            return f"""
                QPushButton {{
                    background-color: {cls.COLORS['accent']};
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {cls.COLORS['accent_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {cls.COLORS['accent_active']};
                }}
                QPushButton:disabled {{
                    background-color: {cls.COLORS['interactive_muted']};
                    color: {cls.COLORS['text_muted']};
                }}
            """
        elif style_type == "secondary":
            return f"""
                QPushButton {{
                    background-color: {cls.COLORS['background_modifier_selected']};
                    color: {cls.COLORS['text_normal']};
                    border: none;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {cls.COLORS['background_modifier_hover']};
                    color: {cls.COLORS['interactive_hover']};
                }}
            """
        elif style_type == "danger":
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {cls.COLORS['interactive_normal']};
                    border: none;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {cls.COLORS['error']};
                    color: white;
                }}
            """

    @classmethod
    def get_checkbox_style(cls) -> str:
        """获取复选框样式"""
        return f"""
            QCheckBox {{
                color: {cls.COLORS['interactive_normal']};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            QCheckBox::indicator:unchecked {{
                border: 2px solid {cls.COLORS['interactive_muted']};
                border-radius: 4px;
                background-color: {cls.COLORS['background_tertiary']};
            }}
            QCheckBox::indicator:unchecked:hover {{
                border: 2px solid {cls.COLORS['interactive_normal']};
            }}
            QCheckBox::indicator:checked {{
                border: none;
                border-radius: 4px;
                background-color: {cls.COLORS['accent']};
                image: url(checkmark.png);
            }}
            QCheckBox::indicator:checked:hover {{
                background-color: {cls.COLORS['accent_hover']};
            }}
        """


from config.config_manager import ConfigManager

class SecurityManager:
    """安全管理器 - 处理密码加密和存储"""

    def __init__(self):
        self.config_manager = ConfigManager()

    def encrypt_password(self, password: str) -> str:
        """密码加密（简单示例，实际应使用更安全的方法）"""
        # 注意：为了兼容性，这里暂时保持简单的哈希
        # 实际生产环境应该使用更安全的加密方式
        salt = "GMTools_2024_Salt"
        return hashlib.sha256((password + salt).encode()).hexdigest()

    def save_credentials(
        self, account: str, password: str, remember: bool, auto_login: bool
    ):
        """保存登录凭证"""
        encrypted_pwd = self.encrypt_password(password) if remember else ""
        
        self.config_manager.update_login_config(
            account=account if remember else "",
            password=encrypted_pwd,
            remember=remember,
            auto_login=auto_login,
            last_login=datetime.now().isoformat()
        )

    def load_credentials(self) -> Dict[str, Any]:
        """加载登录凭证"""
        login_config = self.config_manager.get_login_config()
        return {
            "account": login_config.get("Account", ""),
            "password_hash": login_config.get("Password", ""),
            "remember_password": login_config.get("RememberPassword", False),
            "auto_login": login_config.get("AutoLogin", False),
            "last_login": login_config.get("LastLogin", ""),
        }

    def clear_credentials(self):
        """清除保存的凭证"""
        self.config_manager.update_login_config(
            account="", password="", remember=False, auto_login=False
        )


class AnimatedButton(QPushButton):
    """带动画效果的按钮"""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.animation = None
        self._progress = 0

    @pyqtProperty(float)
    def progress(self):
        return self._progress

    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()

    def start_loading_animation(self):
        """开始加载动画"""
        if self.animation:
            self.animation.stop()

        self.animation = QPropertyAnimation(self, b"progress")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(100)
        self.animation.setLoopCount(-1)  # 无限循环
        self.animation.start()

    def stop_loading_animation(self):
        """停止加载动画"""
        if self.animation:
            self.animation.stop()
            self.animation = None
            self._progress = 0
            self.update()


class DataHandler(QObject):
    """数据处理信号器"""

    show_message = pyqtSignal(str, str, int)  # title, message, message_type
    login_success = pyqtSignal()
    login_failed = pyqtSignal(str)  # error_message
    connection_status_changed = pyqtSignal(bool)  # connected

    def __init__(self, parent=None):
        super().__init__(parent)


class LoginWindow(QWidget):
    """GMTools登录窗口 - Discord风格优化版"""

    connect_success = pyqtSignal()
    connect_failed = pyqtSignal()
    disconnect_signal = pyqtSignal()
    error_signal = pyqtSignal(object)
    receive_signal = pyqtSignal(dict)

    def __init__(self):
        """初始化登录窗口"""
        super().__init__()

        # 基础属性
        self.client = None
        self.main_window = None
        self.auto_retry_count = 0
        self.max_auto_retry = 3
        self.dragging = False
        self.drag_position = QPoint()

        # 管理器
        self.style_manager = StyleManager()
        self.security_manager = SecurityManager()

        # 动画组
        self.animation_group = QParallelAnimationGroup()

        # 创建数据处理信号器
        self.data_handler = DataHandler()
        self.data_handler.show_message.connect(self._show_message_box)
        self.data_handler.login_success.connect(self.on_login_success)
        self.data_handler.login_failed.connect(self.on_login_failed)
        self.data_handler.connection_status_changed.connect(
            self.on_connection_status_changed
        )

        self.connect_success.connect(self.on_connect_success)
        self.connect_failed.connect(self.on_connect_failed)
        self.disconnect_signal.connect(self.on_disconnect)
        self.error_signal.connect(self.on_error)
        self.receive_signal.connect(self.on_receive_data)

        # 初始化UI
        self.init_ui()

        # 加载保存的凭证
        self.load_saved_credentials()

        # 设置窗口透明度动画
        self.setup_fade_animation()

    def setup_fade_animation(self):
        """设置淡入动画"""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_animation.start()

    def load_saved_credentials(self):
        """加载保存的登录凭证"""
        credentials = self.security_manager.load_credentials()

        if credentials["account"]:
            self.account_input.setText(credentials["account"])

        if credentials["remember_password"]:
            self.remember_pwd_cb.setChecked(True)
            # 注意：出于安全考虑，不直接恢复密码
            self.password_edit.setPlaceholderText("已保存密码")

        if credentials["auto_login"]:
            self.auto_login_cb.setChecked(True)

    def mousePressEvent(self, event):
        """鼠标按下事件 - 窗口拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 只在标题栏区域允许拖拽
            if event.position().y() < 40:
                self.dragging = True
                self.drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
                event.accept()

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 窗口拖拽"""
        if self.dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 窗口拖拽"""
        self.dragging = False
        event.accept()

    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口属性
        self.setWindowTitle("梦江南超级GM工具 - 登录")
        self.setFixedSize(430, 350)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)

        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 内容区域
        content_frame = QFrame()
        content_frame.setStyleSheet(
            f"background-color: {StyleManager.COLORS['background_primary']};"
        )
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 标题栏
        self.create_title_bar(content_layout)

        # 登录表单区域
        self.create_login_form(content_layout)

        main_layout.addWidget(content_frame)

    def create_title_bar(self, parent_layout):
        """创建自定义标题栏"""
        title_bar = QFrame()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {StyleManager.COLORS['background_tertiary']};
                border-bottom: 1px solid {StyleManager.COLORS['background_modifier_hover']};
            }}
        """
        )

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(10, 0, 5, 0)

        # Logo和标题
        title_label = QLabel("🎮 GMTools - 登录")
        title_label.setFont(QFont("Microsoft YaHei UI", 11, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {StyleManager.COLORS['text_normal']};")
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        # 控制按钮
        self.create_control_buttons(title_layout)

        parent_layout.addWidget(title_bar)

    def create_control_buttons(self, parent_layout):
        """创建窗口控制按钮"""
        # 最小化按钮
        minimize_btn = QPushButton("—")
        minimize_btn.setFixedSize(30, 30)
        minimize_btn.setFont(QFont("Segoe UI", 12))
        minimize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        minimize_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                color: #b9bbbe;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #40444b;
                color: #ffffff;
            }
        """
        )
        minimize_btn.clicked.connect(self.showMinimized)
        
        # 设置按钮
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(30, 30)
        settings_btn.setFont(QFont("Segoe UI Emoji", 12))
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.setStyleSheet(minimize_btn.styleSheet())
        settings_btn.clicked.connect(self.open_settings)
        
        parent_layout.addWidget(settings_btn)
        parent_layout.addWidget(minimize_btn)

        # 关闭按钮
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setFont(QFont("Segoe UI", 16))
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(StyleManager.get_button_style("danger"))
        close_btn.clicked.connect(self.close)
        parent_layout.addWidget(close_btn)

    def open_settings(self):
        """打开设置窗口"""
        from ui.server_settings_dialog import ServerSettingsDialog
        from PyQt6.QtWidgets import QDialog, QMessageBox
        
        dialog = ServerSettingsDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                from ui.discord_messagebox import DiscordMessageBox
                DiscordMessageBox.show_info(self, "设置已保存", "服务器设置已保存，请重启程序以生效。")
            except ImportError:
                QMessageBox.information(self, "设置已保存", "服务器设置已保存，请重启程序以生效。")

    def create_login_form(self, parent_layout):
        """创建登录表单"""
        # 表单容器
        form_frame = QFrame()
        form_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {StyleManager.COLORS['background_primary']};
            }}
        """
        )
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(32, 32, 32, 32)
        form_layout.setSpacing(18)

        # 账号输入
        self.create_account_input(form_layout)

        # 密码输入
        self.create_password_input(form_layout)

        # 选项
        self.create_options(form_layout)

        # 登录按钮
        self.create_login_button(form_layout)

        form_layout.addStretch()
        parent_layout.addWidget(form_frame)

    def create_account_input(self, parent_layout):
        """创建账号输入框"""
        account_container = QFrame()
        account_container.setFixedHeight(46)
        account_container.setFixedWidth(350)
        account_container.setStyleSheet(StyleManager.get_input_style())

        account_layout = QHBoxLayout(account_container)
        account_layout.setContentsMargins(12, 0, 12, 0)

        # 图标
        account_icon = QLabel("👤")
        account_icon.setFont(QFont("Segoe UI Emoji", 14))
        account_layout.addWidget(account_icon)

        # 输入框
        self.account_input = QLineEdit(GM_ACCOUNT)
        self.account_input.setPlaceholderText("请输入您的账号")
        self.account_input.setFont(QFont("Microsoft YaHei UI", 11))
        self.account_input.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                color: {StyleManager.COLORS['text_normal']};
            }}
            QLineEdit::placeholder {{
                color: {StyleManager.COLORS['text_muted']};
            }}
        """
        )
        account_layout.addWidget(self.account_input)
        parent_layout.addWidget(
            account_container, alignment=Qt.AlignmentFlag.AlignHCenter
        )

    def create_password_input(self, parent_layout):
        """创建密码输入框"""
        password_container = QFrame()
        password_container.setFixedHeight(46)
        password_container.setFixedWidth(350)
        password_container.setStyleSheet(StyleManager.get_input_style())

        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(12, 0, 12, 0)

        # 图标
        password_icon = QLabel("🔒")
        password_icon.setFont(QFont("Segoe UI Emoji", 14))
        password_layout.addWidget(password_icon)

        # 输入框
        self.password_edit = QLineEdit(GM_PASSWORD)
        self.password_edit.setPlaceholderText("请输入您的密码")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setFont(QFont("Microsoft YaHei UI", 11))
        self.password_edit.setStyleSheet(
            f"""
            QLineEdit {{
                background-color: transparent;
                border: none;
                color: {StyleManager.COLORS['text_normal']};
            }}
            QLineEdit::placeholder {{
                color: {StyleManager.COLORS['text_muted']};
            }}
        """
        )
        self.password_edit.returnPressed.connect(self.login)
        password_layout.addWidget(self.password_edit)

        # 显示/隐藏密码按钮
        self.toggle_password_btn = QPushButton("👁")
        self.toggle_password_btn.setFixedSize(24, 24)
        self.toggle_password_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.toggle_password_btn.setStyleSheet(
            """
            QPushButton {
                background-color: transparent;
                border: none;
                color: #72767d;
            }
            QPushButton:hover {
                color: #dcddde;
            }
        """
        )
        self.toggle_password_btn.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.toggle_password_btn)

        parent_layout.addWidget(
            password_container, alignment=Qt.AlignmentFlag.AlignHCenter
        )

    def create_options(self, parent_layout):
        """创建选项区域"""
        options_container = QFrame()
        options_container.setFixedWidth(350)
        options_container.setStyleSheet("background-color: transparent;")

        options_layout = QHBoxLayout(options_container)
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(12)

        self.remember_pwd_cb = QCheckBox("记住密码")
        self.remember_pwd_cb.setFont(QFont("Microsoft YaHei UI", 10))
        self.remember_pwd_cb.setStyleSheet(StyleManager.get_checkbox_style())
        options_layout.addWidget(self.remember_pwd_cb)

        self.auto_login_cb = QCheckBox("自动登录")
        self.auto_login_cb.setFont(QFont("Microsoft YaHei UI", 10))
        self.auto_login_cb.setStyleSheet(StyleManager.get_checkbox_style())
        options_layout.addWidget(self.auto_login_cb)

        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Microsoft YaHei UI", 8))
        self.status_label.setStyleSheet(f"color: {StyleManager.COLORS['text_muted']};")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setContentsMargins(0, 0, 0, 0)
        options_layout.addWidget(self.status_label)

        parent_layout.addWidget(
            options_container, alignment=Qt.AlignmentFlag.AlignHCenter
        )
        parent_layout.addSpacing(8)

    def create_login_button(self, parent_layout):
        """创建登录按钮"""
        self.login_btn = AnimatedButton("登录")
        self.login_btn.setFont(QFont("Microsoft YaHei UI", 12, QFont.Weight.Bold))
        self.login_btn.setFixedHeight(44)
        self.login_btn.setFixedWidth(350)
        self.login_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_btn.setStyleSheet(StyleManager.get_button_style("primary"))
        self.login_btn.clicked.connect(self.login)
        parent_layout.addWidget(self.login_btn, alignment=Qt.AlignmentFlag.AlignHCenter)
        parent_layout.addSpacing(12)

    def toggle_password_visibility(self):
        """切换密码可见性"""
        if self.password_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_btn.setText("🙈")
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_btn.setText("👁")

    def set_client(self, client):
        """设置网络客户端"""
        self.client = client
        if self.client:
            self.client.on_connect = lambda: self.connect_success.emit()
            self.client.on_disconnect = lambda: self.disconnect_signal.emit()
            self.client.on_receive = lambda data: self.receive_signal.emit(data)
            self.client.on_error = lambda err: self.error_signal.emit(err)

    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 自动连接
        QTimer.singleShot(1000, self.auto_connect)

        # 检查自动登录
        if self.auto_login_cb.isChecked() and self.account_input.text():
            QTimer.singleShot(2000, self.auto_login)

    def auto_login(self):
        """自动登录"""
        if self.client and self.client.connected:
            self.login()

    def auto_connect(self):
        """自动连接到服务器"""
        if self.client and not self.client.connected:
            self.connect_to_server()

    def connect_to_server(self):
        """连接到服务器"""
        if not self.client:
            logger.warning("客户端未初始化")
            self.update_status("客户端未初始化", "error")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("连接中...")
        self.login_btn.start_loading_animation()
        
        # 获取服务器配置
        server_config = self.security_manager.config_manager.get_server_config()
        host = server_config.get("Host", "127.0.0.1")
        port = server_config.get("Port", 8080)
        
        self.update_status(f"正在连接 {host}:{port}...", "info")

        import threading

        thread = threading.Thread(target=self._connect_thread, args=(host, port), daemon=True)
        thread.start()

    def _connect_thread(self, host, port):
        """连接线程"""
        try:
            # 确保client.connect支持参数，或者在这里设置client的属性
            if hasattr(self.client, 'connect_to'):
                success = self.client.connect_to(host, port)
            else:
                # 兼容旧接口，如果client支持直接设置属性
                self.client.host = host
                self.client.port = port
                success = self.client.connect()
                
            if success:
                self.connect_success.emit()
            else:
                self.connect_failed.emit()
        except Exception as e:
            logger.error(f"连接异常: {e}", exc_info=True)
            self.error_signal.emit(e)
            self.connect_failed.emit()

    def on_connect_success(self):
        """连接成功"""
        try:
            if self.login_btn:
                self.login_btn.stop_loading_animation()
                self.login_btn.setEnabled(True)
                self.login_btn.setText("登录")
                self.update_status("已连接到服务器", "success")
                logger.info("成功连接到服务器")
        except RuntimeError:
            pass

    def on_connect_failed(self):
        """连接失败"""
        try:
            self.auto_retry_count += 1

            if self.auto_retry_count < self.max_auto_retry:
                retry_delay = 2000 * self.auto_retry_count
                self.update_status(
                    f"连接失败，{retry_delay//1000}秒后重试...", "warning"
                )
                QTimer.singleShot(retry_delay, self.auto_connect)
            else:
                if self.login_btn:
                    self.login_btn.stop_loading_animation()
                    self.login_btn.setEnabled(True)
                    self.login_btn.setText("登录")

                self.update_status("无法连接到服务器", "error")

                try:
                    from ui.discord_messagebox import DiscordMessageBox

                    DiscordMessageBox.show_warning(
                        self,
                        "连接失败",
                        "无法连接到服务器！\n\n"
                        "已自动重试3次\n\n"
                        "请检查：\n"
                        "1. 服务器是否启动\n"
                        "2. 网络连接是否正常\n"
                        "3. 防火墙设置\n\n"
                        "然后点击'登录'按钮重试",
                    )
                except ImportError:
                    QMessageBox.warning(
                        self,
                        "连接失败",
                        "无法连接到服务器！\n\n"
                        "已自动重试3次\n\n"
                        "请检查：\n"
                        "1. 服务器是否启动\n"
                        "2. 网络连接是否正常\n"
                        "3. 防火墙设置\n\n"
                        "然后点击'登录'按钮重试",
                    )
                logger.error(f"连接服务器失败，已重试{self.max_auto_retry}次")
        except RuntimeError:
            pass

    def on_disconnect(self):
        """断开连接"""
        try:
            if self.login_btn:
                self.login_btn.setEnabled(False)
                self.login_btn.setText("未连接")
                self.update_status("已断开连接", "warning")
                logger.info("已断开服务器连接")
        except RuntimeError:
            pass

    def on_connection_status_changed(self, connected: bool):
        """连接状态改变"""
        if connected:
            self.update_status("已连接", "success")
        else:
            self.update_status("未连接", "error")

    def update_status(self, message: str, status_type: str = "info"):
        """更新状态信息"""
        color_map = {
            "info": StyleManager.COLORS["info"],
            "success": StyleManager.COLORS["success"],
            "warning": StyleManager.COLORS["warning"],
            "error": StyleManager.COLORS["error"],
        }

        color = color_map.get(status_type, StyleManager.COLORS["text_muted"])
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")

        # 添加淡出动画
        if status_type != "error":
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))

    def on_error(self, error: Exception):
        """错误处理"""
        error_msg = str(error)
        logger.error(f"发生错误: {error_msg}", exc_info=True)
        self.update_status(f"错误: {error_msg}", "error")

    def _show_message_box(self, title: str, message: str, message_type: int):
        """显示消息框"""

        def show_discord_message():
            try:
                from ui.discord_messagebox import DiscordMessageBox

                if message_type == 0:
                    DiscordMessageBox.show_info(self, title, message)
                elif message_type == 1:
                    DiscordMessageBox.show_warning(self, title, message)
            except ImportError:
                # 回退到原来的QMessageBox
                if message_type == 0:
                    QMessageBox.information(self, title, message)
                elif message_type == 1:
                    QMessageBox.warning(self, title, message)

        QTimer.singleShot(0, show_discord_message)

    def on_login_success(self):
        """登录成功处理"""
        logger.info("登录成功")

        # 保存凭证
        if self.remember_pwd_cb.isChecked():
            self.security_manager.save_credentials(
                self.account_input.text(),
                self.password_edit.text(),
                self.remember_pwd_cb.isChecked(),
                self.auto_login_cb.isChecked(),
            )

        # 更新状态
        self.update_status("登录成功，正在打开主窗口...", "success")

        # 断开数据接收监听，避免后续数据被误认为登录响应
        try:
            self.client.on_receive = None
            self.receive_signal.disconnect(self.on_receive_data)
        except (RuntimeError, TypeError) as e:
            # Ignore signal disconnect errors (e.g., signal already disconnected)
            logger.debug(f"Signal disconnect error: {e}")

        # 延迟打开主窗口
        QTimer.singleShot(500, self._create_and_show_main_window)

    def on_login_failed(self, error_msg: str):
        """登录失败处理"""
        logger.warning(f"登录失败: {error_msg}")
        self.reset_login_button()
        self.update_status(f"登录失败: {error_msg}", "error")

    def _create_and_show_main_window(self):
        """创建并显示主窗口"""
        try:
            from .discord_main_window import DiscordMainWindow

            # 创建主窗口
            self.main_window = DiscordMainWindow(self.client)
            self.main_window.set_client(self.client)
            self.main_window.set_account(self.account_input.text())

            # 更新回调
            self.client.on_connect = lambda: self.main_window.update_connection_status(
                True
            )
            self.client.on_disconnect = (
                lambda: self.main_window.update_connection_status(False)
            )
            self.client.on_receive = lambda data: self.main_window.on_receive_data(data)

            # 更新连接状态
            self.main_window.update_connection_status(self.client.connected)

            # 淡出动画
            self.fade_out_animation = QPropertyAnimation(
                self.opacity_effect, b"opacity"
            )
            self.fade_out_animation.setDuration(300)
            self.fade_out_animation.setStartValue(1)
            self.fade_out_animation.setEndValue(0)
            self.fade_out_animation.finished.connect(self.hide)
            self.fade_out_animation.finished.connect(self.main_window.show)
            self.fade_out_animation.start()

            # 连接登出信号
            self.main_window.logout_signal.connect(self.on_logout)

            logger.info("主窗口已打开")

        except Exception as e:
            logger.error(f"创建主窗口失败: {e}", exc_info=True)
            try:
                from ui.discord_messagebox import DiscordMessageBox

                DiscordMessageBox.show_error(self, "错误", f"无法打开主窗口：{str(e)}")
            except ImportError:
                QMessageBox.critical(self, "错误", f"无法打开主窗口：{str(e)}")

    def on_logout(self):
        """处理登出"""
        # 清理密码
        if not self.remember_pwd_cb.isChecked():
            self.password_edit.clear()

        # 淡入动画
        self.show()
        fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        fade_in.setDuration(300)
        fade_in.setStartValue(0)
        fade_in.setEndValue(1)
        fade_in.start()

        self.update_status("已登出", "info")
        logger.info("用户已登出")

    def on_receive_data(self, data: dict):
        """接收数据"""
        seq_no = data.get("seq_no")
        content = data.get("content", "")

        logger.debug(f"收到响应 - 序号: {seq_no}, 内容: {content[:100]}")

        if seq_no == 7:  # 登录成功
            clean_content = content.replace("#Y/", "").replace("#Y", "")
            self.data_handler.show_message.emit(
                "登录成功", f"登录成功！\n\n{clean_content}", 0
            )
            self.data_handler.login_success.emit()

        elif seq_no == 999:  # 登录失败
            self.data_handler.login_failed.emit(content)
            self.data_handler.show_message.emit("登录失败", content, 1)

    def login(self):
        """执行登录"""
        if not self.client:
            self.update_status("客户端未初始化", "error")
            return

        if not self.client.connected:
            self.update_status("请先连接服务器", "warning")
            self.connect_to_server()
            return

        account = self.account_input.text().strip()
        password = self.password_edit.text().strip()

        if not account:
            self.account_input.setFocus()
            self.update_status("请输入账号", "warning")
            return

        if not password:
            self.password_edit.setFocus()
            self.update_status("请输入密码", "warning")
            return

        self.login_btn.setEnabled(False)
        self.login_btn.setText("登录中...")
        self.login_btn.start_loading_animation()
        self.update_status("正在登录...", "info")

        try:
            if self.client.send_login(account, password):
                logger.info(f"发送登录请求 - 账号: {account}")
                QTimer.singleShot(3000, self.reset_login_button)
            else:
                self.reset_login_button()
                self.update_status("发送登录请求失败", "error")

        except Exception as e:
            logger.error(f"登录异常: {e}", exc_info=True)
            self.reset_login_button()
            self.update_status(f"登录失败: {str(e)}", "error")

    def reset_login_button(self):
        """重置登录按钮"""
        try:
            if self.login_btn:
                self.login_btn.stop_loading_animation()
                self.login_btn.setEnabled(True)
                self.login_btn.setText("登录")
        except RuntimeError:
            pass

    def closeEvent(self, event):
        """窗口关闭事件"""
        if self.client:
            try:
                self.client._is_closing = True
                self.client.disconnect()
            except (RuntimeError, OSError, AttributeError) as e:
                # Ignore exceptions during window close
                logger.debug(f"Client disconnect error during close: {e}")

        logger.info("登录窗口已关闭")
        event.accept()


def main():
    """主函数 - 测试用"""
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # 设置应用图标
    app.setWindowIcon(
        QApplication.style().standardIcon(
            QApplication.style().StandardPixmap.SP_ComputerIcon
        )
    )

    window = LoginWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
