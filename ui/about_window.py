#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
关于窗口 - Discord风格
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class AboutWindow(QDialog):
    """关于窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于 GMTools")
        self.setFixedSize(400, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setup_ui()

    def setup_ui(self):
        # 主背景
        self.setStyleSheet(
            """
            QDialog {
                background-color: transparent;
            }
            QFrame#MainFrame {
                background-color: #313338;
                border-radius: 8px;
                border: 1px solid #1E1F22;
            }
            QLabel {
                color: #DBDEE1;
            }
        """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 主框架
        main_frame = QFrame()
        main_frame.setObjectName("MainFrame")
        layout.addWidget(main_frame)

        frame_layout = QVBoxLayout(main_frame)
        frame_layout.setContentsMargins(24, 24, 24, 24)
        frame_layout.setSpacing(16)

        # 标题部分
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        app_name = QLabel("GMTools")
        app_name.setStyleSheet(
            """
            font-size: 28px;
            font-weight: bold;
            color: #F2F3F5;
        """
        )
        title_layout.addWidget(app_name)

        version = QLabel("v1.0.0")
        version.setStyleSheet(
            """
            font-size: 14px;
            color: #949BA4;
            background-color: #2B2D31;
            padding: 4px 8px;
            border-radius: 4px;
        """
        )
        title_layout.addWidget(version)

        frame_layout.addLayout(title_layout)

        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #3F4147; border: none; max-height: 1px;")
        frame_layout.addWidget(line)

        # 内容部分
        content_layout = QVBoxLayout()
        content_layout.setSpacing(8)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc = QLabel("一个基于Python的GM管理工具\n专为Discord风格设计")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 14px; line-height: 1.5;")
        content_layout.addWidget(desc)

        copyright_label = QLabel("© 2025 GMTools Team")
        copyright_label.setStyleSheet("color: #949BA4; font-size: 12px;")
        content_layout.addWidget(copyright_label)

        frame_layout.addLayout(content_layout)

        frame_layout.addStretch()

        # 按钮部分
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setFixedSize(100, 38)
        close_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #5865F2;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:pressed {
                background-color: #3C45A5;
            }
        """
        )
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        button_layout.addStretch()

        frame_layout.addLayout(button_layout)

    def mousePressEvent(self, event):
        # 允许拖动窗口
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()
