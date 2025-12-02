#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理系统测试脚本
演示所有主要功能
"""

import requests
import json
from typing import Optional

# API 基础 URL
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/users"


class GMToolsUserClient:
    """GMTools 用户管理客户端"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/users"
        self.token: Optional[str] = None
        self.user_info: Optional[dict] = None
    
    def _headers(self, auth: bool = True) -> dict:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, username: str, email: str, password: str, full_name: str = None) -> dict:
        """注册新用户"""
        data = {
            "username": username,
            "email": email,
            "password": password
        }
        if full_name:
            data["full_name"] = full_name
        
        response = requests.post(
            f"{self.api_url}/register",
            json=data,
            headers=self._headers(auth=False)
        )
        return response.json()
    
    def login(self, username: str, password: str) -> bool:
        """登录"""
        data = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{self.api_url}/login",
            json=data,
            headers=self._headers(auth=False)
        )
        
        if response.status_code == 200:
            result = response.json()
            self.token = result["access_token"]
            self.user_info = result["user"]
            return True
        return False
    
    def get_me(self) -> dict:
        """获取当前用户信息"""
        response = requests.get(
            f"{self.api_url}/me",
            headers=self._headers()
        )
        return response.json()
    
    def update_me(self, email: str = None, full_name: str = None) -> dict:
        """更新当前用户信息"""
        data = {}
        if email:
            data["email"] = email
        if full_name:
            data["full_name"] = full_name
        
        response = requests.put(
            f"{self.api_url}/me",
            json=data,
            headers=self._headers()
        )
        return response.json()
    
    def change_password(self, old_password: str, new_password: str) -> dict:
        """修改密码"""
        data = {
            "old_password": old_password,
            "new_password": new_password
        }
        
        response = requests.post(
            f"{self.api_url}/me/change-password",
            json=data,
            headers=self._headers()
        )
        return response.json()
    
    def get_my_logs(self, limit: int = 50) -> dict:
        """获取操作日志"""
        response = requests.get(
            f"{self.api_url}/me/logs?limit={limit}",
            headers=self._headers()
        )
        return response.json()
    
    def list_users(self, limit: int = 100, offset: int = 0) -> dict:
        """获取用户列表（管理员）"""
        response = requests.get(
            f"{self.api_url}/?limit={limit}&offset={offset}",
            headers=self._headers()
        )
        return response.json()
    
    def get_user(self, user_id: int) -> dict:
        """获取指定用户（管理员）"""
        response = requests.get(
            f"{self.api_url}/{user_id}",
            headers=self._headers()
        )
        return response.json()
    
    def update_user_role(self, user_id: int, role: str) -> dict:
        """更新用户角色（管理员）"""
        data = {"role": role}
        response = requests.put(
            f"{self.api_url}/{user_id}/role",
            json=data,
            headers=self._headers()
        )
        return response.json()
    
    def update_user_status(self, user_id: int, is_active: bool) -> dict:
        """更新用户状态（管理员）"""
        data = {"is_active": is_active}
        response = requests.put(
            f"{self.api_url}/{user_id}/status",
            json=data,
            headers=self._headers()
        )
        return response.json()
    
    def reset_user_password(self, user_id: int, new_password: str) -> dict:
        """重置用户密码（管理员）"""
        data = {"new_password": new_password}
        response = requests.post(
            f"{self.api_url}/{user_id}/reset-password",
            json=data,
            headers=self._headers()
        )
        return response.json()
    
    def delete_user(self, user_id: int) -> dict:
        """删除用户（管理员）"""
        response = requests.delete(
            f"{self.api_url}/{user_id}",
            headers=self._headers()
        )
        return response.json()
    
    def get_all_logs(self, limit: int = 100, offset: int = 0) -> dict:
        """获取所有操作日志（管理员）"""
        response = requests.get(
            f"{self.api_url}/logs/all?limit={limit}&offset={offset}",
            headers=self._headers()
        )
        return response.json()


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(result: dict):
    """打印结果"""
    print(json.dumps(result, indent=2, ensure_ascii=False))


def test_user_management():
    """测试用户管理系统"""
    
    print("\n" + "🚀" * 30)
    print("GMTools 用户管理系统 - 功能测试")
    print("🚀" * 30)
    
    client = GMToolsUserClient()
    
    # 1. 管理员登录
    print_section("1. 管理员登录")
    if client.login("admin", "admin123"):
        print("✓ 管理员登录成功")
        print(f"Token: {client.token[:50]}...")
        print(f"用户信息: {client.user_info['username']} ({client.user_info['role']})")
    else:
        print("✗ 管理员登录失败")
        return
    
    # 2. 注册新用户
    print_section("2. 注册新用户")
    try:
        result = client.register(
            username="testuser",
            email="test@example.com",
            password="test123456",
            full_name="测试用户"
        )
        print_result(result)
    except Exception as e:
        print(f"注册可能已存在: {e}")
    
    # 3. 普通用户登录
    print_section("3. 普通用户登录")
    user_client = GMToolsUserClient()
    if user_client.login("testuser", "test123456"):
        print("✓ 普通用户登录成功")
    
    # 4. 获取当前用户信息
    print_section("4. 获取当前用户信息")
    result = user_client.get_me()
    print_result(result)
    
    # 5. 更新用户信息
    print_section("5. 更新用户信息")
    result = user_client.update_me(full_name="测试用户(已更新)")
    print_result(result)
    
    # 6. 修改密码
    print_section("6. 修改密码")
    result = user_client.change_password("test123456", "newpassword123")
    print_result(result)
    
    # 重新登录
    print("\n重新使用新密码登录...")
    if user_client.login("testuser", "newpassword123"):
        print("✓ 新密码登录成功")
    
    # 7. 获取操作日志
    print_section("7. 获取当前用户操作日志")
    result = user_client.get_my_logs(limit=10)
    print(f"日志数量: {result.get('total', 0)}")
    if result.get('logs'):
        print(f"最新操作: {result['logs'][0]['action']}")
    
    # 8. 管理员操作 - 获取用户列表
    print_section("8. 管理员 - 获取用户列表")
    result = client.list_users(limit=10)
    print(f"用户总数: {result.get('total', 0)}")
    if result.get('users'):
        for user in result['users']:
            print(f"  - {user['username']} ({user['email']}) - {user['role']}")
    
    # 9. 管理员操作 - 获取指定用户
    print_section("9. 管理员 - 获取指定用户")
    if result.get('users'):
        user_id = result['users'][0]['id']
        result = client.get_user(user_id)
        print_result(result)
    
    # 10. 管理员操作 - 更新用户角色
    print_section("10. 管理员 - 更新用户角色")
    # 找到 testuser 的 ID
    users_result = client.list_users()
    testuser = next((u for u in users_result.get('users', []) if u['username'] == 'testuser'), None)
    if testuser:
        result = client.update_user_role(testuser['id'], "admin")
        print_result(result)
    
    # 11. 管理员操作 - 获取所有日志
    print_section("11. 管理员 - 获取所有操作日志")
    result = client.get_all_logs(limit=20)
    print(f"日志总数: {result.get('total', 0)}")
    if result.get('logs'):
        print("\n最近的操作:")
        for log in result['logs'][:5]:
            print(f"  - [{log['created_at']}] {log.get('username', 'N/A')}: {log['action']}")
    
    # 12. 管理员操作 - 禁用用户
    print_section("12. 管理员 - 禁用用户")
    if testuser:
        result = client.update_user_status(testuser['id'], False)
        print_result(result)
        
        # 尝试用被禁用的账号登录
        print("\n尝试用被禁用的账号登录...")
        disabled_client = GMToolsUserClient()
        if not disabled_client.login("testuser", "newpassword123"):
            print("✓ 被禁用的账号无法登录")
        
        # 重新启用
        print("\n重新启用账号...")
        result = client.update_user_status(testuser['id'], True)
        print("✓ 账号已重新启用")
    
    # 13. 管理员操作 - 重置密码
    print_section("13. 管理员 - 重置用户密码")
    if testuser:
        result = client.reset_user_password(testuser['id'], "resetpassword123")
        print_result(result)
        
        # 验证新密码
        print("\n验证重置后的密码...")
        reset_client = GMToolsUserClient()
        if reset_client.login("testuser", "resetpassword123"):
            print("✓ 重置后的密码有效")
    
    print("\n" + "✅" * 30)
    print("所有测试完成!")
    print("✅" * 30 + "\n")


if __name__ == "__main__":
    try:
        # 检查 API 是否运行
        try:
            response = requests.get(BASE_URL)
            if response.status_code != 200:
                print("⚠️  API 服务未运行,请先启动: python api_main.py")
                exit(1)
        except requests.exceptions.ConnectionError:
            print("⚠️  无法连接到 API 服务")
            print("请确保已启动 API 服务: python api_main.py")
            exit(1)
        
        test_user_management()
        
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
