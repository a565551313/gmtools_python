#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接管理
"""

import sqlite3
import os
from contextlib import contextmanager
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "gmtools.db")


class DatabaseConnection:
    """SQLite 数据库连接管理器"""
    
    _instance: Optional['DatabaseConnection'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self.db_path = DB_PATH
        self._initialized = True
        logger.info(f"数据库路径: {self.db_path}")
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
        return conn
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标的上下文管理器"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def init_database(self):
        """初始化数据库表结构"""
        with self.get_cursor() as cursor:
            # 创建用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    level INTEGER DEFAULT 1,
                    role VARCHAR(20) DEFAULT 'user',
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP
                )
            """)
            
            # 创建用户会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token VARCHAR(500) NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # 创建操作日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action VARCHAR(100) NOT NULL,
                    resource VARCHAR(100),
                    details TEXT,
                    ip_address VARCHAR(45),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            
            # 创建权限表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 创建 Level 权限关联表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS level_permissions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level INTEGER NOT NULL,
                    permission_id INTEGER NOT NULL,
                    UNIQUE(level, permission_id),
                    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
                )
            """)
            
            # 创建激活码表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activation_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(50) UNIQUE NOT NULL,
                    level INTEGER NOT NULL,
                    is_used BOOLEAN DEFAULT 0,
                    used_by INTEGER,
                    used_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (used_by) REFERENCES users(id) ON DELETE SET NULL
                )
            """)
            
            # 创建索引
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_username 
                ON users(username)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_email 
                ON users(email)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_token 
                ON user_sessions(token)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_sessions_user_id 
                ON user_sessions(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_user_id 
                ON audit_logs(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activation_codes_code 
                ON activation_codes(code)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activation_codes_level 
                ON activation_codes(level)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activation_codes_used_by 
                ON activation_codes(used_by)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_activation_codes_is_used 
                ON activation_codes(is_used)
            """)
            
            logger.info("数据库表结构初始化完成")


# 全局数据库实例
db = DatabaseConnection()
