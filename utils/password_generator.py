#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全密码生成器
"""

import random
import string


def generate_secure_password(length: int = 12) -> str:
    """
    生成安全的随机密码
    
    Args:
        length: 密码长度（默认12位）
    
    Returns:
        随机密码字符串
        
    格式：
    - 至少1个大写字母
    - 至少1个小写字母
    - 至少1个数字
    - 至少1个特殊字符
    """
    if length < 8:
        length = 8  # 最小8位
    
    # 定义字符集
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*"
    
    # 确保至少包含每种类型的字符
    password = [
        random.choice(uppercase),
        random.choice(lowercase),
        random.choice(digits),
        random.choice(special)
    ]
    
    # 填充剩余长度
    all_chars = uppercase + lowercase + digits + special
    password.extend(random.choice(all_chars) for _ in range(length - 4))
    
    # 打乱顺序
    random.shuffle(password)
    
    return ''.join(password)


if __name__ == "__main__":
    # 测试生成器
    for i in range(5):
        print(f"密码 {i+1}: {generate_secure_password()}")
