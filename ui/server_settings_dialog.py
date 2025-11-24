from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QColor, QPainter, QPainterPath, QPen
from config.config_manager import ConfigManager
from ui.login_window import StyleManager

class ServerSettingsDialog(QDialog):
    """服务器设置对话框 - Discord风格"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = ConfigManager()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(350, 300)
        
        self._drag_pos = None
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 容器
        self.container = QFrame()
        self.container.setStyleSheet(f"""
            QFrame {{
                background-color: {StyleManager.COLORS['background_primary']};
                border-radius: 8px;
            }}
        """)
        
        # 阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.container.setGraphicsEffect(shadow)
        
        main_layout.addWidget(self.container)
        
        # 容器布局
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("服务器设置")
        title_label.setFont(QFont("Microsoft YaHei UI", 14, QFont.Weight.Bold))
        title_label.setStyleSheet(f"color: {StyleManager.COLORS['text_normal']};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet(f"background-color: {StyleManager.COLORS['background_modifier_hover']};")
        layout.addWidget(line)
        
        # Host输入
        host_label = QLabel("服务器地址 (Host)")
        host_label.setStyleSheet(f"color: {StyleManager.COLORS['text_muted']}; font-weight: bold;")
        layout.addWidget(host_label)
        
        self.host_input = QLineEdit()
        self.host_input.setFixedHeight(38)
        self.host_input.setStyleSheet(f"""
            QLineEdit {{
                background-color: {StyleManager.COLORS['background_tertiary']};
                border: 1px solid {StyleManager.COLORS['background_tertiary']};
                border-radius: 4px;
                color: {StyleManager.COLORS['text_normal']};
                padding: 0 10px;
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border: 1px solid {StyleManager.COLORS['accent']};
            }}
        """)
        layout.addWidget(self.host_input)
        
        # Port输入
        port_label = QLabel("端口 (Port)")
        port_label.setStyleSheet(f"color: {StyleManager.COLORS['text_muted']}; font-weight: bold;")
        layout.addWidget(port_label)
        
        self.port_input = QLineEdit()
        self.port_input.setFixedHeight(38)
        self.port_input.setStyleSheet(self.host_input.styleSheet())
        layout.addWidget(self.port_input)
        
        layout.addStretch()
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedHeight(38)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {StyleManager.COLORS['text_normal']};
                border: none;
                font-weight: bold;
            }}
            QPushButton:hover {{
                text-decoration: underline;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("保存")
        save_btn.setFixedHeight(38)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {StyleManager.COLORS['accent']};
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                background-color: {StyleManager.COLORS['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {StyleManager.COLORS['accent_active']};
            }}
        """)
        save_btn.clicked.connect(self.save_settings)
        
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

    def load_settings(self):
        config = self.config_manager.get_server_config()
        self.host_input.setText(config.get("Host", "127.0.0.1"))
        self.port_input.setText(str(config.get("Port", 8080)))

    def save_settings(self):
        host = self.host_input.text().strip()
        port_str = self.port_input.text().strip()
        
        if not host:
            self.host_input.setFocus()
            return
            
        if not port_str.isdigit():
            self.port_input.setFocus()
            return
            
        self.config_manager.update_server_config(host, int(port_str))
        self.accept()

    def paintEvent(self, event):
        # 绘制边框
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 绘制圆角矩形边框
        rect = self.container.geometry()
        path = QPainterPath()
        path.addRoundedRect(rect.x(), rect.y(), rect.width(), rect.height(), 8, 8)
        
        # 边框颜色
        painter.setPen(QPen(QColor("#202225"), 1))
        painter.drawPath(path)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
