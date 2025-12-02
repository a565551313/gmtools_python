#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT 认证工具
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
import bcrypt
import logging

logger = logging.getLogger(__name__)

# JWT 配置
SECRET_KEY = "your-secret-key-change-this-in-production-gmtools-2024"  # 生产环境请修改
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时


class AuthUtils:
    """认证工具类"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"密码验证失败: {e}")
            return False
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """创建 JWT Token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """解码 JWT Token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token 已过期")
            return None
        except Exception as e:
            logger.error(f"Token 解码失败: {e}")
            return None
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """验证 Token 并返回 payload"""
        return AuthUtils.decode_token(token)
