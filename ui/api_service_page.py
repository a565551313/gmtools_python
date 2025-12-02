#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 服务控制页面
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QComboBox, QSpinBox, QCheckBox, QGroupBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QFont

class APIServicePage(QWidget):
    def __init__(self, api_manager):
        super().__init__()
        self.api_manager = api_manager
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("API 服务控制台")
        title_label.setStyleSheet("color: white; font-size: 24px; font-weight: bold;")
        layout.addWidget(title_label)
        
        # 设置区域
        settings_group = QGroupBox("服务配置")
        settings_group.setStyleSheet("""
            QGroupBox {
                color: white;
                border: 1px solid #40444b;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        settings_layout = QHBoxLayout(settings_group)
        
        # IP 地址
        settings_layout.addWidget(QLabel("监听地址:", styleSheet="color: #b9bbbe;"))
        self.host_combo = QComboBox()
        self.host_combo.setEditable(True)
        self.host_combo.addItems(self.api_manager.known_hosts)
        self.host_combo.setCurrentText(self.api_manager.host)
        self.host_combo.setFixedSize(150, 30)
        self.host_combo.setStyleSheet("""
            QComboBox {
                color: white;
                background-color: #202225;
                border: 1px solid #202225;
                border-radius: 4px;
                padding: 2px 6px;
            }
            QComboBox:focus {
                border: 1px solid #5865F2;
            }
            QComboBox QLineEdit {
                color: white;
                background-color: transparent;
            }
            QComboBox::drop-down {
                border: none;
                background-color: transparent;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid #72767D;
                border-bottom: 4px solid #72767D;
                margin-right: 4px;
            }
        """)
        settings_layout.addWidget(self.host_combo)
        
        # 端口
        settings_layout.addWidget(QLabel("端口:", styleSheet="color: #b9bbbe;"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(self.api_manager.port)
        self.port_spin.setFixedSize(80, 30)
        self.port_spin.setStyleSheet("""
            QSpinBox {
                color: white;
                background-color: #202225;
                border: 1px solid #202225;
                border-radius: 4px;
                padding: 2px 6px;
            }
            QSpinBox:focus {
                border: 1px solid #5865F2;
            }
        """)
        settings_layout.addWidget(self.port_spin)
        
        # 自动启动
        self.auto_start_check = QCheckBox("自动启动")
        self.auto_start_check.setChecked(self.api_manager.auto_start)
        self.auto_start_check.setStyleSheet("color: #b9bbbe;")
        settings_layout.addWidget(self.auto_start_check)
        
        # 保存按钮
        self.save_btn = QPushButton("保存配置")
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                color: white;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
        """)
        self.save_btn.clicked.connect(self.save_config)
        settings_layout.addWidget(self.save_btn)
        
        settings_layout.addStretch()
        layout.addWidget(settings_group)
        
        # 控制区域
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("启动服务")
        self.start_btn.setFixedSize(120, 40)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #3ba55c;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2d7d46;
            }
            QPushButton:disabled {
                background-color: #3ba55c80;
            }
        """)
        self.start_btn.clicked.connect(self.api_manager.start_service)
        control_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("停止服务")
        self.stop_btn.setFixedSize(120, 40)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #ed4245;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c03537;
            }
            QPushButton:disabled {
                background-color: #ed424580;
            }
        """)
        self.stop_btn.clicked.connect(self.api_manager.stop_service)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        self.restart_btn = QPushButton("重启服务")
        self.restart_btn.setFixedSize(120, 40)
        self.restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
            QPushButton:disabled {
                background-color: #5865F280;
            }
        """)
        self.restart_btn.clicked.connect(self.api_manager.restart_service)
        self.restart_btn.setEnabled(False)
        control_layout.addWidget(self.restart_btn)
        
        # 快捷链接
        control_layout.addStretch()
        
        self.user_mgmt_btn = QPushButton("用户管理")
        self.user_mgmt_btn.setStyleSheet("""
            QPushButton {
                background-color: #5865F2;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4752C4;
            }
        """)
        self.user_mgmt_btn.clicked.connect(self.open_user_management)
        control_layout.addWidget(self.user_mgmt_btn)
        
        self.docs_btn = QPushButton("打开 API 文档")
        self.docs_btn.setStyleSheet("""
            QPushButton {
                background-color: #4f545c;
                color: white;
                border-radius: 4px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #686d73;
            }
        """)
        self.docs_btn.clicked.connect(self.open_docs)
        control_layout.addWidget(self.docs_btn)
        
        self.tester_btn = QPushButton("打开测试页面")
        self.tester_btn.setStyleSheet(self.docs_btn.styleSheet())
        self.tester_btn.clicked.connect(self.open_tester)
        control_layout.addWidget(self.tester_btn)
        
        layout.addLayout(control_layout)
        
        # 日志区域
        log_header = QHBoxLayout()
        log_label = QLabel("运行日志")
        log_label.setStyleSheet("color: #b9bbbe; font-weight: bold;")
        log_header.addWidget(log_label)
        
        log_header.addStretch()
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("""
            QTextEdit {
                background-color: #000000;
                color: #00ff00;
                font-family: "Microsoft YaHei", "SimHei", Consolas, monospace;
                border: 1px solid #40444b;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        
        self.clear_log_btn = QPushButton("清空日志")
        self.clear_log_btn.setFixedSize(80, 24)
        self.clear_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #4f545c;
                color: white;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #686d73;
            }
        """)
        self.clear_log_btn.clicked.connect(self.log_output.clear)
        log_header.addWidget(self.clear_log_btn)
        
        layout.addLayout(log_header)
        layout.addWidget(self.log_output)
        
    def connect_signals(self):
        self.api_manager.service_started.connect(self.on_service_started)
        self.api_manager.service_stopped.connect(self.on_service_stopped)
        self.api_manager.log_received.connect(self.append_log)
        
    def save_config(self):
        host = self.host_combo.currentText()
        port = self.port_spin.value()
        auto_start = self.auto_start_check.isChecked()
        self.api_manager.save_config(host, port, auto_start)
        QMessageBox.information(self, "提示", "配置已保存")
        
    def on_service_started(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.restart_btn.setEnabled(True)
        self.host_combo.setEnabled(False)
        self.port_spin.setEnabled(False)
        
    def on_service_stopped(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.restart_btn.setEnabled(False)
        self.host_combo.setEnabled(True)
        self.port_spin.setEnabled(True)
        
    def append_log(self, text):
        self.log_output.append(text.strip())
        # 滚动到底部
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def open_docs(self):
        url = f"http://{self.api_manager.host}:{self.api_manager.port}/docs"
        QDesktopServices.openUrl(QUrl(url))
        
    def open_tester(self):
        url = f"http://{self.api_manager.host}:{self.api_manager.port}/docs-custom"
        QDesktopServices.openUrl(QUrl(url))
    
    def open_user_management(self):
        """打开用户管理页面"""
        if not self.api_manager.is_running():
            QMessageBox.warning(self, "提示", "请先启动 API 服务")
            return
        self.api_manager.open_user_management()

