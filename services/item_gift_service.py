#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
道具赠送服务

提供道具赠送的业务逻辑：
1. 权限检查
2. 周期配额验证
3. 发送执行
"""

from typing import Tuple, Dict, List
from database.item_gift import ItemConfig, ItemLevelLimit, ItemGiftLog
from database.models import User
import logging

logger = logging.getLogger(__name__)


class ItemGiftService:
    """道具赠送服务"""
    
    @staticmethod
    def check_gift_permission(
        sender_username: str,
        sender_level: int,
        item_name: str,
        quantity: int,
        is_admin: bool = False
    ) -> Tuple[bool, str]:
        """
        检查道具赠送权限
        
        Args:
            sender_username: 发送者用户名
            sender_level: 发送者等级
            item_name: 道具名称
            quantity: 数量
            is_admin: 是否为管理员
        
        Returns:
            (是否允许, 错误信息或成功提示)
        """
        try:
            # 1. 管理员豁免所有限制
            if is_admin:
                logger.info(f"管理员 {sender_username} 发送 {item_name} x{quantity} - 豁免检查")
                return True, "管理员无限制"
            
            # 2. 检查道具是否在白名单
            item_config = ItemConfig.get_by_name(item_name)
            if not item_config:
                logger.warning(f"道具不存在: {item_name}")
                return False, f"道具 '{item_name}' 不存在"
            
            if not item_config.is_active:
                logger.warning(f"道具已禁用: {item_name}")
                return False, f"道具 '{item_name}' 已被禁用，无法发送"
            
            # 3. 获取等级限制配置
            limit = ItemLevelLimit.get_limit(item_name, sender_level)
            if not limit:
                logger.warning(f"等级 {sender_level} 无权发送道具: {item_name}")
                return False, f"您的等级 (Level {sender_level}) 无权发送道具 '{item_config.display_name}'"
            
            # 4. 检查数量范围
            if quantity < limit.min_quantity:
                return False, f"发送数量不能少于 {limit.min_quantity} 个"
            
            if quantity > limit.max_quantity:
                return False, f"发送数量不能超过 {limit.max_quantity} 个"
            
            # 5. 检查周期配额
            period_used = ItemGiftLog.get_period_usage(
                sender_username, 
                item_name, 
                limit.reset_period_hours
            )
            
            remaining = limit.period_total_limit - period_used
            if quantity > remaining:
                return False, (
                    f"超出周期配额限制。"
                    f"周期：{limit.reset_period_hours}小时，"
                    f"总量限制：{limit.period_total_limit}，"
                    f"已使用：{period_used}，"
                    f"剩余：{remaining}"
                )
            
            # 6. 所有检查通过
            logger.info(
                f"权限检查通过: {sender_username} (L{sender_level}) "
                f"可发送 {item_name} x{quantity}, "
                f"剩余配额: {remaining - quantity}/{limit.period_total_limit}"
            )
            
            return True, "检查通过"
            
        except Exception as e:
            logger.error(f"权限检查异常: {e}", exc_info=True)
            return False, f"系统错误: {str(e)}"
    
    @staticmethod
    def send_item_gift(
        sender_username: str,
        sender_level: int,
        recipient_username: str,
        item_name: str,
        quantity: int,
        is_admin: bool = False
    ) -> Tuple[bool, str]:
        """
        执行道具赠送
        
        Args:
            sender_username: 发送者用户名
            sender_level: 发送者等级
            recipient_username: 接收者用户名
            item_name: 道具名称
            quantity: 数量
            is_admin: 是否为管理员
        
        Returns:
            (是否成功, 消息)
        """
        try:
            # 1. 权限检查
            can_send, message = ItemGiftService.check_gift_permission(
                sender_username, 
                sender_level, 
                item_name, 
                quantity, 
                is_admin
            )
            
            if not can_send:
                return False, message
            
            # 2. 获取限制配置（用于记录周期）
            limit = ItemLevelLimit.get_limit(item_name, sender_level)
            reset_period_hours = limit.reset_period_hours if limit else 24
            
            # 3. 记录发送日志
            log = ItemGiftLog.create(
                sender_username=sender_username,
                sender_level=sender_level,
                recipient_username=recipient_username,
                item_name=item_name,
                quantity=quantity,
                reset_period_hours=reset_period_hours,
                is_admin_send=is_admin
            )
            
            if not log:
                logger.error(f"创建发送记录失败: {sender_username} -> {recipient_username}")
                return False, "系统错误：记录发送失败"
            
            # 4. 这里应该调用实际的游戏服务器API发送道具
            # TODO: 集成游戏服务器API
            # success = game_server.send_item(recipient_username, item_name, quantity)
            
            # 暂时返回成功（实际应该等待游戏服务器响应）
            logger.info(
                f"道具发送成功: {sender_username} -> {recipient_username}, "
                f"{item_name} x{quantity}"
            )
            
            item_config = ItemConfig.get_by_name(item_name)
            display_name = item_config.display_name if item_config else item_name
            
            return True, f"成功发送 {display_name} x{quantity} 给 {recipient_username}"
            
        except Exception as e:
            logger.error(f"发送道具异常: {e}", exc_info=True)
            return False, f"系统错误: {str(e)}"
    
    @staticmethod
    def get_user_limits(user_level: int) -> List[Dict]:
        """
        获取用户的所有道具限制
        
        Args:
            user_level: 用户等级
        
        Returns:
            限制列表
        """
        try:
            limits = ItemLevelLimit.get_all_by_level(user_level)
            result = []
            
            for limit in limits:
                item_config = ItemConfig.get_by_name(limit.item_name)
                if item_config and item_config.is_active:
                    result.append({
                        'item_name': limit.item_name,
                        'display_name': item_config.display_name,
                        'description': item_config.description,
                        'icon_url': item_config.icon_url,
                        'min_quantity': limit.min_quantity,
                        'max_quantity': limit.max_quantity,
                        'reset_period_hours': limit.reset_period_hours,
                        'period_total_limit': limit.period_total_limit
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户限制失败: {e}")
            return []
    
    @staticmethod
    def get_user_usage(username: str, user_level: int) -> List[Dict]:
        """
        获取用户的配额使用情况
        
        Args:
            username: 用户名
            user_level: 用户等级
        
        Returns:
            使用情况列表
        """
        try:
            limits = ItemLevelLimit.get_all_by_level(user_level)
            result = []
            
            for limit in limits:
                item_config = ItemConfig.get_by_name(limit.item_name)
                if not item_config or not item_config.is_active:
                    continue
                
                # 获取周期内已使用量
                used = ItemGiftLog.get_period_usage(
                    username, 
                    limit.item_name, 
                    limit.reset_period_hours
                )
                
                remaining = limit.period_total_limit - used
                
                result.append({
                    'item_name': limit.item_name,
                    'display_name': item_config.display_name,
                    'total_limit': limit.period_total_limit,
                    'used': used,
                    'remaining': remaining,
                    'reset_period_hours': limit.reset_period_hours,
                    'usage_percent': round(used / limit.period_total_limit * 100, 1) if limit.period_total_limit > 0 else 0
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取用户使用情况失败: {e}")
            return []
    
    @staticmethod
    def get_available_items(user_level: int) -> List[Dict]:
        """
        获取用户可发送的道具列表
        
        Args:
            user_level: 用户等级
        
        Returns:
            可发送道具列表
        """
        try:
            limits = ItemLevelLimit.get_all_by_level(user_level)
            result = []
            
            for limit in limits:
                item_config = ItemConfig.get_by_name(limit.item_name)
                if item_config and item_config.is_active:
                    result.append({
                        'item_name': limit.item_name,
                        'display_name': item_config.display_name,
                        'description': item_config.description,
                        'icon_url': item_config.icon_url
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"获取可发送道具列表失败: {e}")
            return []
