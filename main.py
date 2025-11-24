#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMTools Python移植版 - 主程序入口
梦江南超级GM工具登录功能

功能说明：
- 连接服务端 (127.0.0.1:8080)
- 使用自定义加密算法加密数据包
- 通过MessagePack格式发送登录请求
- 支持账号密码登录验证
"""

import sys
import os

# Add project root to path before importing local modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication  # noqa: E402
from PyQt6.QtGui import QPalette  # noqa: E402

# Import local modules
from network.client import GMToolsClient  # noqa: E402
from ui.login_window import LoginWindow  # noqa: E402


class GMToolsApp:
    """GMTools应用程序主类"""

    def __init__(self):
        """初始化应用程序"""
        # 创建QApplication
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("GMTools Python")
        self.app.setApplicationVersion("1.0")

        # 创建网络客户端
        self.client = GMToolsClient()

        # 创建登录窗口
        self.login_window = LoginWindow()
        self.login_window.set_client(self.client)

        # 设置窗口
        self.login_window.show()

    def run(self):
        """运行应用程序"""
        # 设置应用程序样式
        self.setup_style()

        # 进入事件循环
        return self.app.exec()

    def setup_style(self):
        """设置应用程序样式"""
        # 使用现代风格
        self.app.setStyle("Fusion")

        # 设置调色板（可选）
        palette = QPalette()
        self.app.setPalette(palette)


def main():
    """主函数"""
    print("=" * 60)
    print("  梦江南超级GM工具 - Python移植版")
    print("=" * 60)
    print()
    print("功能特性：")
    print("  - 登录功能")
    print("  - 自定义加密算法")
    print("  - MessagePack数据格式")
    print("  - 现代UI界面")
    print()
    print("=" * 60)
    print()

    try:
        # 创建并运行应用程序
        gm_app = GMToolsApp()
        exit_code = gm_app.run()

        print("程序退出")
        return exit_code

    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    # 强制退出所有线程和进程
    os._exit(exit_code)
