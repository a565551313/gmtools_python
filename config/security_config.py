#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏操作安全配置
定义各种操作的限制和规则
"""

from typing import Dict, Any
from enum import Enum

class OperationType(Enum):
    """操作类型"""
    GIVE_ITEM = "give_item"
    GIVE_GEM = "give_gem"
    MODIFY_CHARACTER = "modify_character"
    RECHARGE = "recharge"
    BROADCAST = "broadcast"

class SecurityConfig:
    """安全配置"""
    
    # 道具数量限制
    ITEM_LIMITS = {
        "default": {
            "min": 1,
            "max": 999,  # 默认单次最多999个
            "daily_max": 9999  # 每日最多发放9999个
        },
        "rare_items": {  # 稀有道具
            "min": 1,
            "max": 10,
            "daily_max": 50
        },
        "currency": {  # 货币类
            "min": 1,
            "max": 100000000,
            "daily_max": 1000000000
        }
    }
    
    # 宝石等级限制
    GEM_LEVEL_LIMITS = {
        "min_level": 1,
        "max_level": 15
    }
    
    # 角色属性修改限制
    CHARACTER_ATTR_LIMITS = {
        "level": {"min": 1, "max": 200},
        "hp": {"min": 1, "max": 999999},
        "mp": {"min": 1, "max": 999999},
        "attack": {"min": 1, "max": 9999},
        "defense": {"min": 1, "max": 9999},
        "speed": {"min": 1, "max": 9999}
    }
    
    # 操作频率限制（每分钟）
    RATE_LIMITS = {
        OperationType.GIVE_ITEM: 30,  # 每分钟最多30次
        OperationType.GIVE_GEM: 20,
        OperationType.MODIFY_CHARACTER: 10,
        OperationType.RECHARGE: 5,
        OperationType.BROADCAST: 3
    }
    
    # 需要高级权限的操作（需要 level >= 8）
    HIGH_PRIVILEGE_OPERATIONS = [
        OperationType.RECHARGE,
        OperationType.BROADCAST
    ]
    
    # 敏感操作（需要记录详细日志）
    SENSITIVE_OPERATIONS = [
        OperationType.GIVE_ITEM,
        OperationType.GIVE_GEM,
        OperationType.RECHARGE
    ]

    @staticmethod
    def get_item_limit(item_category: str = "default") -> Dict[str, int]:
        """获取道具数量限制"""
        return SecurityConfig.ITEM_LIMITS.get(
            item_category, 
            SecurityConfig.ITEM_LIMITS["default"]
        )
    
    @staticmethod
    def validate_item_count(count: int, item_category: str = "default") -> tuple[bool, str]:
        """
        验证道具数量是否合法
        返回: (是否合法, 错误消息)
        """
        limits = SecurityConfig.get_item_limit(item_category)
        
        if count < limits["min"]:
            return False, f"数量不能小于 {limits['min']}"
        
        if count > limits["max"]:
            return False, f"单次数量不能超过 {limits['max']}"
        
        return True, ""
    
    @staticmethod
    def validate_gem_level(min_level: int, max_level: int) -> tuple[bool, str]:
        """验证宝石等级是否合法"""
        limits = SecurityConfig.GEM_LEVEL_LIMITS
        
        if min_level < limits["min_level"] or min_level > limits["max_level"]:
            return False, f"最小等级必须在 {limits['min_level']}-{limits['max_level']} 之间"
        
        if max_level < limits["min_level"] or max_level > limits["max_level"]:
            return False, f"最大等级必须在 {limits['min_level']}-{limits['max_level']} 之间"
        
        if min_level > max_level:
            return False, "最小等级不能大于最大等级"
        
        return True, ""
    
    @staticmethod
    def validate_character_attr(attr_name: str, value: int) -> tuple[bool, str]:
        """验证角色属性值是否合法"""
        if attr_name not in SecurityConfig.CHARACTER_ATTR_LIMITS:
            return False, f"未知的属性: {attr_name}"
        
        limits = SecurityConfig.CHARACTER_ATTR_LIMITS[attr_name]
        
        if value < limits["min"] or value > limits["max"]:
            return False, f"{attr_name} 必须在 {limits['min']}-{limits['max']} 之间"
        
        return True, ""
