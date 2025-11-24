import sys
import winsound
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QWidget, QFrame, QGraphicsDropShadowEffect,
                           QSizePolicy, QApplication, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen, QIcon

class DiscordButton(QPushButton):
    """Discord风格按钮"""
    def __init__(self, text, btn_type="primary", parent=None):
        super().__init__(text, parent)
        self.btn_type = btn_type
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self.setFixedHeight(38)
        self.update_style()
        
    def update_style(self):
        if self.btn_type == "primary":
            # 蓝色按钮 (Discord Blurple)
            self.setStyleSheet("""
                QPushButton {
                    background-color: #5865F2;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #4752C4;
                }
                QPushButton:pressed {
                    background-color: #3C45A5;
                }
            """)
        elif self.btn_type == "secondary":
            # 灰色按钮
            self.setStyleSheet("""
                QPushButton {
                    background-color: #4F545C;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #5D6269;
                }
                QPushButton:pressed {
                    background-color: #40444B;
                }
            """)
        elif self.btn_type == "danger":
            # 红色按钮
            self.setStyleSheet("""
                QPushButton {
                    background-color: #ED4245;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #C03537;
                }
                QPushButton:pressed {
                    background-color: #A12D2F;
                }
            """)
        elif self.btn_type == "success":
            # 绿色按钮
            self.setStyleSheet("""
                QPushButton {
                    background-color: #3BA55C;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 0 20px;
                }
                QPushButton:hover {
                    background-color: #2D7D46;
                }
                QPushButton:pressed {
                    background-color: #246438;
                }
            """)


class DiscordMessageBox(QDialog):
    """Discord风格消息框"""
    
    # 定义按钮类型常量
    BUTTON_OK = 1
    BUTTON_YES_NO = 2
    BUTTON_OK_CANCEL = 3
    
    # 定义消息类型常量
    MSG_INFO = "info"
    MSG_WARNING = "warning"
    MSG_ERROR = "error"
    MSG_SUCCESS = "success"
    
    # 长度限制常量
    MAX_MESSAGE_LENGTH = 100
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置固定宽度，高度自适应
        self.setFixedWidth(400)
        self.setMaximumHeight(400)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # 设置无边框窗口
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        self.button_result = QDialog.DialogCode.Rejected
        
        # 用于拖拽的变量
        self._drag_pos = None
        self.message_type = self.MSG_INFO
        
        self.init_ui()
        
    def init_ui(self):
        """初始化界面"""
        # 主布局 - 添加边距用于绘制边框和阴影
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)  # 为边框和阴影留空间
        
        # 创建主容器
        self.container = QWidget()
        self.container.setObjectName("mainContainer")
        self.container.setStyleSheet("""
            #mainContainer {
                background-color: #36393F;
                border-radius: 8px;
            }
        """)
        
        # 添加阴影效果
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.container.setGraphicsEffect(shadow)
        
        main_layout.addWidget(self.container)
        
        # 容器内布局
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)
        
        # 标题区域
        self.title_widget = self.create_title_widget()
        container_layout.addWidget(self.title_widget)
        
        # 分割线
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        self.separator.setFixedHeight(1)
        self.separator.setStyleSheet("""
            QFrame {
                background-color: #40444B;
                border: none;
                margin: 0px;
            }
        """)
        container_layout.addWidget(self.separator)
        
        # 消息内容区域
        self.content_widget = self.create_content_widget()
        container_layout.addWidget(self.content_widget, 1)
        
        # 按钮区域
        self.button_widget = self.create_button_widget()
        container_layout.addWidget(self.button_widget)
        
    def create_title_widget(self) -> QWidget:
        """创建标题区域"""
        widget = QWidget()
        widget.setFixedHeight(45)
        widget.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(0)
        
        # 标题标签
        self.title_label = QLabel("标题")
        self.title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.title_label.setStyleSheet("color: white; background-color: transparent;")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # 关闭按钮
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setFont(QFont("Segoe UI", 16))
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #B9BBBE;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #ED4245;
                color: white;
            }
        """)
        self.close_button.clicked.connect(self.reject)
        layout.addWidget(self.close_button)
        
        return widget
        
    def create_content_widget(self) -> QWidget:
        """创建内容区域"""
        widget = QWidget()
        widget.setStyleSheet("background-color: transparent;")
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # 消息图标和文本容器
        content_container = QWidget()
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(12)
        
        # 图标标签
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        content_layout.addWidget(self.icon_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: #2B2D31;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #1A1B1E;
                border-radius: 4px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #40444B;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # 消息标签
        self.message_label = QLabel()
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Segoe UI", 11))
        self.message_label.setStyleSheet("color: #DCDDDE;")
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.message_label)
        content_layout.addWidget(scroll_area, 1)
        
        layout.addWidget(content_container)
        
        return widget
        
    def create_button_widget(self) -> QWidget:
        """创建按钮区域"""
        widget = QWidget()
        widget.setFixedHeight(65)
        widget.setStyleSheet("""
            QWidget {
                background-color: #2F3136;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        
        self.button_layout = QHBoxLayout(widget)
        self.button_layout.setContentsMargins(20, 10, 20, 10)
        self.button_layout.setSpacing(10)
        
        return widget
    
    def paintEvent(self, event):
        """绘制事件 - 用于绘制边框"""
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制边框
        pen = QPen(QColor("#7289DA"))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # 绘制圆角矩形边框
        rect = self.container.geometry()
        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 8, 8)
        painter.drawPath(path)
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
            
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()
            
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            event.accept()
    
    def set_message_type(self, msg_type: str):
        """设置消息类型并更新图标"""
        self.message_type = msg_type
        
        # 设置图标
        icons = {
            self.MSG_INFO: "ℹ️",
            self.MSG_WARNING: "⚠️",
            self.MSG_ERROR: "❌",
            self.MSG_SUCCESS: "✅"
        }
        
        icon_text = icons.get(msg_type, "ℹ️")
        self.icon_label.setText(icon_text)
        self.icon_label.setFont(QFont("Segoe UI", 16))
        
        # 播放对应音效
        self.play_sound()
    
    def play_sound(self):
        """播放音效"""
        if sys.platform != "win32":
            return
            
        try:
            sound_map = {
                self.MSG_INFO: winsound.MB_ICONASTERISK,
                self.MSG_SUCCESS: winsound.MB_OK,
                self.MSG_WARNING: winsound.MB_ICONEXCLAMATION,
                self.MSG_ERROR: winsound.MB_ICONHAND
            }
            sound = sound_map.get(self.message_type, winsound.MB_ICONASTERISK)
            winsound.MessageBeep(sound)
        except Exception as e:
            print(f"播放音效失败: {e}")
    
    def setup_buttons(self, button_type: int):
        """设置按钮"""
        # 清除现有按钮
        while self.button_layout.count():
            item = self.button_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self.button_layout.addStretch()
        
        if button_type == self.BUTTON_OK:
            ok_btn = DiscordButton("确定", "primary")
            ok_btn.clicked.connect(self.accept)
            self.button_layout.addWidget(ok_btn)
            
        elif button_type == self.BUTTON_YES_NO:
            no_btn = DiscordButton("否", "secondary")
            no_btn.clicked.connect(self.reject)
            yes_btn = DiscordButton("是", "primary")
            yes_btn.clicked.connect(self.accept)
            self.button_layout.addWidget(no_btn)
            self.button_layout.addWidget(yes_btn)
            
        elif button_type == self.BUTTON_OK_CANCEL:
            cancel_btn = DiscordButton("取消", "secondary")
            cancel_btn.clicked.connect(self.reject)
            ok_btn = DiscordButton("确定", "primary")
            ok_btn.clicked.connect(self.accept)
            self.button_layout.addWidget(cancel_btn)
            self.button_layout.addWidget(ok_btn)
    
    @staticmethod
    def show_info(parent, title: str, message: str, button_type: int = 1) -> int:
        """显示信息消息框"""
        dialog = DiscordMessageBox(parent)
        dialog.title_label.setText(title)
        dialog.message_label.setText(message)
        dialog.set_message_type(DiscordMessageBox.MSG_INFO)
        dialog.setup_buttons(button_type)
        return dialog.exec()
    
    @staticmethod
    def show_warning(parent, title: str, message: str, button_type: int = 3) -> int:
        """显示警告消息框"""
        dialog = DiscordMessageBox(parent)
        dialog.title_label.setText(title)
        dialog.message_label.setText(message)
        dialog.set_message_type(DiscordMessageBox.MSG_WARNING)
        dialog.setup_buttons(button_type)
        return dialog.exec()
    
    @staticmethod
    def show_error(parent, title: str, message: str, button_type: int = 1) -> int:
        """显示错误消息框"""
        dialog = DiscordMessageBox(parent)
        dialog.title_label.setText(title)
        dialog.message_label.setText(message)
        dialog.set_message_type(DiscordMessageBox.MSG_ERROR)
        dialog.setup_buttons(button_type)
        return dialog.exec()
    
    @staticmethod
    def show_success(parent, title: str, message: str, button_type: int = 1) -> int:
        """显示成功消息框"""
        dialog = DiscordMessageBox(parent)
        dialog.title_label.setText(title)
        dialog.message_label.setText(message)
        dialog.set_message_type(DiscordMessageBox.MSG_SUCCESS)
        dialog.setup_buttons(button_type)
        return dialog.exec()


# 测试
if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 测试各种消息类型
    DiscordMessageBox.show_info(None, "信息提示", "这是一条信息消息，可以很长很长的内容。", DiscordMessageBox.BUTTON_OK)
    
    result = DiscordMessageBox.show_warning(None, "确认操作", "确定要删除这个文件吗？", DiscordMessageBox.BUTTON_YES_NO)
    print(f"警告对话框结果: {result}")
    
    DiscordMessageBox.show_error(None, "错误", "操作失败，请重试！")
    
    DiscordMessageBox.show_success(None, "成功", "操作已成功完成！")
    
    sys.exit(0)