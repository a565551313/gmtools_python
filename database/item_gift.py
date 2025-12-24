#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道具赠送系统数据模型

包含：
1. ItemConfig - 道具配置模型
2. ItemLevelLimit - 道具等级限制模型
3. ItemGiftLog - 道具发送记录模型
"""

from typing import Optional, List, Dict
from datetime import datetime, timedelta
from database.connection import db
import logging

logger = logging.getLogger(__name__)


class ItemConfig:
    """道具配置模型"""
    
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.item_name = data.get('item_name')
        self.display_name = data.get('display_name')
        self.description = data.get('description', '')
        self.icon_url = data.get('icon_url')
        self.is_active = bool(data.get('is_active', 1))
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'item_name': self.item_name,
            'display_name': self.display_name,
            'description': self.description,
            'icon_url': self.icon_url,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def create(item_name: str, display_name: str = None, 
               description: str = '', icon_url: str = None) -> Optional['ItemConfig']:
        """创建道具配置"""
        try:
            # 如果未提供显示名称，默认使用道具名称
            if not display_name:
                display_name = item_name
                
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO item_configs (item_name, display_name, description, icon_url, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (item_name, display_name, description, icon_url))
                
                logger.info(f"创建道具配置: {display_name} ({item_name})")
                return ItemConfig.get_by_name(item_name)
        except Exception as e:
            logger.error(f"创建道具配置失败: {e}")
            return None
    
    @staticmethod
    def get_by_name(item_name: str) -> Optional['ItemConfig']:
        """根据道具名称获取配置"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM item_configs WHERE item_name = ?
                """, (item_name,))
                row = cursor.fetchone()
                return ItemConfig(dict(row)) if row else None
        except Exception as e:
            logger.error(f"获取道具配置失败: {e}")
            return None
    
    @staticmethod
    def get_all_active() -> List['ItemConfig']:
        """获取所有启用的道具配置"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM item_configs WHERE is_active = 1
                    ORDER BY item_name
                """)
                rows = cursor.fetchall()
                return [ItemConfig(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"获取道具配置列表失败: {e}")
            return []
    
    @staticmethod
    def get_all() -> List['ItemConfig']:
        """获取所有道具配置（包括禁用的）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("SELECT * FROM item_configs ORDER BY item_name")
                rows = cursor.fetchall()
                return [ItemConfig(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"获取道具配置列表失败: {e}")
            return []
    
    def update(self, display_name: str = None, description: str = None,
               icon_url: str = None, is_active: bool = None) -> bool:
        """更新道具配置"""
        try:
            updates = []
            params = []
            
            if display_name is not None:
                updates.append("display_name = ?")
                params.append(display_name)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if icon_url is not None:
                updates.append("icon_url = ?")
                params.append(icon_url)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(int(is_active))
            
            if not updates:
                return True
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(self.item_name)
            
            with db.get_cursor() as cursor:
                sql = f"UPDATE item_configs SET {', '.join(updates)} WHERE item_name = ?"
                cursor.execute(sql, tuple(params))
                
            logger.info(f"更新道具配置: {self.item_name}")
            return True
        except Exception as e:
            logger.error(f"更新道具配置失败: {e}")
            return False

    def rename(self, new_item_name: str) -> bool:
        """重命名道具（级联更新所有关联表）"""
        if self.item_name == new_item_name:
            return True
            
        try:
            with db.get_cursor() as cursor:
                # 开启事务
                cursor.execute("BEGIN TRANSACTION")
                
                try:
                    # 1. 更新 item_configs
                    cursor.execute("""
                        UPDATE item_configs SET item_name = ?, updated_at = CURRENT_TIMESTAMP 
                        WHERE item_name = ?
                    """, (new_item_name, self.item_name))
                    
                    # 2. 更新 item_level_limits
                    cursor.execute("""
                        UPDATE item_level_limits SET item_name = ? 
                        WHERE item_name = ?
                    """, (new_item_name, self.item_name))
                    
                    # 3. 更新 item_gift_logs
                    cursor.execute("""
                        UPDATE item_gift_logs SET item_name = ? 
                        WHERE item_name = ?
                    """, (new_item_name, self.item_name))
                    
                    cursor.execute("COMMIT")
                    self.item_name = new_item_name
                    logger.info(f"道具重命名成功: {self.item_name} -> {new_item_name}")
                    return True
                    
                except Exception as e:
                    cursor.execute("ROLLBACK")
                    raise e
                    
        except Exception as e:
            logger.error(f"道具重命名失败: {e}")
            return False
    
    @staticmethod
    def delete(item_name: str) -> bool:
        """删除道具配置（软删除）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE item_configs 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE item_name = ?
                """, (item_name,))
                
            logger.info(f"删除道具配置: {item_name}")
            return True
        except Exception as e:
            logger.error(f"删除道具配置失败: {e}")
            return False


class ItemLevelLimit:
    """道具等级限制模型"""
    
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.item_name = data.get('item_name')
        self.user_level = data.get('user_level')
        self.min_quantity = data.get('min_quantity', 1)
        self.max_quantity = data.get('max_quantity', 99)
        self.reset_period_hours = data.get('reset_period_hours', 24)
        self.period_total_limit = data.get('period_total_limit', 999)
        self.is_active = bool(data.get('is_active', 1))
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'item_name': self.item_name,
            'user_level': self.user_level,
            'min_quantity': self.min_quantity,
            'max_quantity': self.max_quantity,
            'reset_period_hours': self.reset_period_hours,
            'period_total_limit': self.period_total_limit,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def create(item_name: str, user_level: int, 
               min_quantity: int = 1, max_quantity: int = 99,
               reset_period_hours: int = 24, period_total_limit: int = 999) -> Optional['ItemLevelLimit']:
        """创建等级限制"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO item_level_limits 
                    (item_name, user_level, min_quantity, max_quantity, reset_period_hours, period_total_limit, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (item_name, user_level, min_quantity, max_quantity, reset_period_hours, period_total_limit))
                
                logger.info(f"创建等级限制: {item_name} - Level {user_level}")
                return ItemLevelLimit.get_limit(item_name, user_level)
        except Exception as e:
            logger.error(f"创建等级限制失败: {e}")
            return None

    @staticmethod
    def batch_create(limits_data: List[dict]) -> bool:
        """批量创建等级限制"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("BEGIN TRANSACTION")
                try:
                    for data in limits_data:
                        cursor.execute("""
                            INSERT INTO item_level_limits 
                            (item_name, user_level, min_quantity, max_quantity, reset_period_hours, period_total_limit, is_active)
                            VALUES (?, ?, ?, ?, ?, ?, 1)
                        """, (
                            data['item_name'], 
                            data['user_level'], 
                            data.get('min_quantity', 1), 
                            data.get('max_quantity', 99),
                            data.get('reset_period_hours', 24),
                            data.get('period_total_limit', 999)
                        ))
                    cursor.execute("COMMIT")
                    return True
                except Exception as e:
                    cursor.execute("ROLLBACK")
                    raise e
        except Exception as e:
            logger.error(f"批量创建等级限制失败: {e}")
            return False
    
    @staticmethod
    def get_limit(item_name: str, user_level: int) -> Optional['ItemLevelLimit']:
        """获取指定道具和等级的限制（包括禁用的，用于管理）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM item_level_limits 
                    WHERE item_name = ? AND user_level = ?
                """, (item_name, user_level))
                row = cursor.fetchone()
                return ItemLevelLimit(dict(row)) if row else None
        except Exception as e:
            logger.error(f"获取等级限制失败: {e}")
            return None
    
    @staticmethod
    def get_active_limit(item_name: str, user_level: int) -> Optional['ItemLevelLimit']:
        """获取有效的限制（用于检查）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM item_level_limits 
                    WHERE item_name = ? AND user_level = ? AND is_active = 1
                """, (item_name, user_level))
                row = cursor.fetchone()
                return ItemLevelLimit(dict(row)) if row else None
        except Exception as e:
            logger.error(f"获取有效等级限制失败: {e}")
            return None

    @staticmethod
    def get_all_by_level(user_level: int) -> List['ItemLevelLimit']:
        """获取某等级的所有限制（包括禁用的）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM item_level_limits 
                    WHERE user_level = ?
                    ORDER BY item_name
                """, (user_level,))
                rows = cursor.fetchall()
                return [ItemLevelLimit(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"获取等级限制列表失败: {e}")
            return []
    
    @staticmethod
    def get_all_by_item(item_name: str) -> List['ItemLevelLimit']:
        """获取某道具的所有等级限制（包括禁用的）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM item_level_limits 
                    WHERE item_name = ?
                    ORDER BY user_level
                """, (item_name,))
                rows = cursor.fetchall()
                return [ItemLevelLimit(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"获取等级限制列表失败: {e}")
            return []
    
    @staticmethod
    def get_all() -> List['ItemLevelLimit']:
        """获取所有限制（包括禁用的）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM item_level_limits
                    ORDER BY item_name, user_level
                """)
                rows = cursor.fetchall()
                return [ItemLevelLimit(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"获取限制列表失败: {e}")
            return []
    
    def update(self, min_quantity: int = None, max_quantity: int = None,
               reset_period_hours: int = None, period_total_limit: int = None,
               is_active: bool = None, item_name: str = None, user_level: int = None) -> bool:
        """更新限制"""
        try:
            updates = []
            params = []
            
            if min_quantity is not None:
                updates.append("min_quantity = ?")
                params.append(min_quantity)
            if max_quantity is not None:
                updates.append("max_quantity = ?")
                params.append(max_quantity)
            if reset_period_hours is not None:
                updates.append("reset_period_hours = ?")
                params.append(reset_period_hours)
            if period_total_limit is not None:
                updates.append("period_total_limit = ?")
                params.append(period_total_limit)
            if is_active is not None:
                updates.append("is_active = ?")
                params.append(int(is_active))
            if item_name is not None:
                updates.append("item_name = ?")
                params.append(item_name)
            if user_level is not None:
                updates.append("user_level = ?")
                params.append(user_level)
            
            if not updates:
                return True
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(self.id)
            
            with db.get_cursor() as cursor:
                sql = f"UPDATE item_level_limits SET {', '.join(updates)} WHERE id = ?"
                cursor.execute(sql, tuple(params))
                
            logger.info(f"更新等级限制: ID {self.id}")
            return True
        except Exception as e:
            logger.error(f"更新等级限制失败: {e}")
            return False
    
    @staticmethod
    def delete(item_name: str, user_level: int) -> bool:
        """删除限制（软删除）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE item_level_limits 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE item_name = ? AND user_level = ?
                """, (item_name, user_level))
                
            logger.info(f"删除等级限制: {item_name} - Level {user_level}")
            return True
        except Exception as e:
            logger.error(f"删除等级限制失败: {e}")
            return False
    
    @staticmethod
    def delete_by_id(limit_id: int) -> bool:
        """根据ID删除限制（软删除）"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE item_level_limits 
                    SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (limit_id,))
                
            logger.info(f"删除等级限制 ID: {limit_id}")
            return True
        except Exception as e:
            logger.error(f"删除等级限制失败: {e}")
            return False


class ItemGiftLog:
    """道具发送记录模型"""
    
    def __init__(self, data: dict):
        self.id = data.get('id')
        self.sender_username = data.get('sender_username')
        self.sender_level = data.get('sender_level')
        self.recipient_username = data.get('recipient_username')
        self.item_name = data.get('item_name')
        self.quantity = data.get('quantity')
        self.reset_period_hours = data.get('reset_period_hours')
        self.is_admin_send = bool(data.get('is_admin_send', 0))
        self.sent_at = data.get('sent_at')
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'id': self.id,
            'sender_username': self.sender_username,
            'sender_level': self.sender_level,
            'recipient_username': self.recipient_username,
            'item_name': self.item_name,
            'quantity': self.quantity,
            'reset_period_hours': self.reset_period_hours,
            'is_admin_send': self.is_admin_send,
            'sent_at': self.sent_at
        }
    
    @staticmethod
    def create(sender_username: str, sender_level: int, recipient_username: str,
               item_name: str, quantity: int, reset_period_hours: int = 24,
               is_admin_send: bool = False) -> Optional['ItemGiftLog']:
        """创建发送记录"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO item_gift_logs 
                    (sender_username, sender_level, recipient_username, item_name, quantity, reset_period_hours, is_admin_send)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (sender_username, sender_level, recipient_username, item_name, quantity, reset_period_hours, int(is_admin_send)))
                
                log_id = cursor.lastrowid
                logger.info(f"记录道具发送: {sender_username} -> {recipient_username}, {item_name} x{quantity}")
                
                cursor.execute("SELECT * FROM item_gift_logs WHERE id = ?", (log_id,))
                row = cursor.fetchone()
                return ItemGiftLog(dict(row)) if row else None
        except Exception as e:
            logger.error(f"创建发送记录失败: {e}")
            return None
    
    @staticmethod
    def get_period_usage(sender_username: str, item_name: str, period_hours: int) -> int:
        """获取周期内已发送的数量（不含管理员发送）"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=period_hours)
            
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT SUM(quantity) as total 
                    FROM item_gift_logs 
                    WHERE sender_username = ? AND item_name = ? AND sent_at > ? AND is_admin_send = 0
                """, (sender_username, item_name, cutoff_time.strftime('%Y-%m-%d %H:%M:%S')))
                
                row = cursor.fetchone()
                total = row['total'] if row and row['total'] else 0
                return int(total)
        except Exception as e:
            logger.error(f"获取周期使用量失败: {e}")
            return 0
    
    @staticmethod
    def get_recent_logs(sender_username: str, limit: int = 50) -> List['ItemGiftLog']:
        """获取最近的发送记录"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM item_gift_logs 
                    WHERE sender_username = ? 
                    ORDER BY sent_at DESC 
                    LIMIT ?
                """, (sender_username, limit))
                
                rows = cursor.fetchall()
                return [ItemGiftLog(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"获取发送记录失败: {e}")
            return []
    
    @staticmethod
    def get_logs_by_item(item_name: str, limit: int = 100) -> List['ItemGiftLog']:
        """获取某道具的发送记录"""
        try:
            with db.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM item_gift_logs 
                    WHERE item_name = ? 
                    ORDER BY sent_at DESC 
                    LIMIT ?
                """, (item_name, limit))
                
                rows = cursor.fetchall()
                return [ItemGiftLog(dict(row)) for row in rows]
        except Exception as e:
            logger.error(f"获取发送记录失败: {e}")
            return []
