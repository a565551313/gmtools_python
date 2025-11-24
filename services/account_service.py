#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号服务类
处理账号充值、管理等相关业务逻辑
"""

from .base_service import BaseService
import logging

logger = logging.getLogger(__name__)


class AccountService(BaseService):
    """账号服务类"""

    async def recharge_currency(self, player_id: str, currency_type: str, amount: int) -> bool:
        """
        充值货币

        Args:
            player_id: 玩家ID
            currency_type: 货币类型 (如: 仙玉, 点卡, 银子, 储备)
            amount: 数量

        Returns:
            bool: 发送是否成功
        """
        # BaseService 默认使用 self.current_account (即GM账号)
        
        data = {
            "玩家id": player_id,
            "数值": amount
        }
        
        # 构建命令名称，例如 "充值仙玉"
        command = f"充值{currency_type}"
        
        logger.info(f"发送充值请求: 玩家id={player_id}, 类型={currency_type}, 数量={amount}")
        return await self.send_command(2, command, data)

    async def send_travel_fee(self, account: str, player_id: str) -> bool:
        """
        发送路费

        Args:
            account: 账号
            player_id: 玩家ID

        Returns:
            bool: 发送是否成功
        """
        # 注意：发送路费时，命令后缀应该是GM账号，而不是目标账号
        # BaseService 默认使用 self.current_account (即GM账号)
        
        data = {
            "账号": account,
            "玩家id": player_id
        }
        
        logger.info(f"发送路费请求: 账号={account}, 玩家ID={player_id}")
        return await self.send_command(2, "发送路费", data)
    async def recharge_gm_level(self, player_id: str, amount: int, gm_level: str) -> bool:
        """
        充值GM等级

        Args:
            player_id: 玩家ID
            amount: 数额
            gm_level: GM等级 (如: GM1, GM2)

        Returns:
            bool: 发送是否成功
        """
        data = {
            "玩家id": player_id,
            "数额": amount,
            "GM等级": gm_level
        }
        logger.info(f"发送充值GM等级请求: 玩家ID={player_id}, 等级={gm_level}, 数额={amount}")
        return await self.send_command(2, "充值GM等级", data)

    async def manage_account(self, command: str, target_id: str, id_type: str = "账号") -> bool:
        """
        账号管理操作 (封禁/解封/踢人等)

        Args:
            command: 命令名称 (如: 封禁账号, 踢出战斗)
            target_id: 目标ID (账号或角色ID)
            id_type: ID类型 ("账号" 或 "角色ID")

        Returns:
            bool: 发送是否成功
        """
        key = "玩家id" if id_type == "角色ID" else "账号"
        data = {key: target_id}
        
        # BaseService 默认使用 self.current_account (即GM账号)
            
        logger.info(f"发送账号管理请求: 命令={command}, 目标={target_id}, 类型={id_type}")
        return await self.send_command(3, command, data)

    async def change_password(self, account: str, new_password: str) -> bool:
        """
        修改密码

        Args:
            account: 账号
            new_password: 新密码

        Returns:
            bool: 发送是否成功
        """
        # BaseService 默认使用 self.current_account (即GM账号)
        data = {
            "账号": account,
            "密码": new_password
        }
        logger.info(f"发送修改密码请求: 账号={account}")
        return await self.send_command(3, "修改密码", data)

    async def give_title(self, player_id: str, title: str) -> bool:
        """
        给予称谓
        
        Args:
            player_id: 玩家ID
            title: 称谓名称
            
        Returns:
            bool: 发送是否成功
        """
        data = {
            "玩家id": player_id,
            "坐骑名称": title  # 注意：原代码中使用"坐骑名称"作为key
        }
        logger.info(f"发送给予称谓请求: 玩家ID={player_id}, 称谓={title}")
        return await self.send_command(3, "给予称谓", data)

    async def recharge_skill(self, player_id: str, amount: int, skill_type: str) -> bool:
        """
        充值经验/技能/熟练度
        
        Args:
            player_id: 玩家ID
            amount: 数额
            skill_type: 类型 (充值经验, 充值累充, 打造熟练, 裁缝熟练, 炼金熟练, 淬灵熟练)
            
        Returns:
            bool: 发送是否成功
        """
        data = {
            "玩家id": player_id,
            "数额": amount
        }
        logger.info(f"发送{skill_type}请求: 玩家ID={player_id}, 数额={amount}")
        return await self.send_command(2, skill_type, data)

    async def recharge_faction(self, player_id: str, amount: int, faction_type: str) -> bool:
        """
        充值帮派/积分相关
        
        Args:
            player_id: 玩家ID
            amount: 数额
            faction_type: 类型 (充值帮贡, 充值门贡, 活跃积分, 比武积分)
            
        Returns:
            bool: 发送是否成功
        """
        data = {
            "玩家id": player_id,
            "数额": amount
        }
        logger.info(f"发送{faction_type}请求: 玩家ID={player_id}, 数额={amount}")
        return await self.send_command(2, faction_type, data)

    async def recharge_gm_coin(self, player_id: str, amount: int) -> bool:
        """
        充值GM币
        
        Args:
            player_id: 玩家ID
            amount: 数额
            
        Returns:
            bool: 发送是否成功
        """
        data = {
            "玩家id": player_id,
            "数额": amount
        }
        logger.info(f"发送充值GM币请求: 玩家ID={player_id}, 数额={amount}")
        return await self.send_command(2, "充值GM币", data)

    async def recharge_record(self, player_id: str) -> bool:
        """
        充值记录
        
        Args:
            player_id: 玩家ID
            
        Returns:
            bool: 发送是否成功
        """
        data = {
            "玩家id": player_id,
            "数额": ""
        }
        logger.info(f"发送充值记录请求: 玩家ID={player_id}")
        return await self.send_command(2, "充值记录", data)

    async def set_bagua(self, bagua_name: str) -> bool:
        """
        八卦设置
        
        Args:
            bagua_name: 八卦名称 (乾, 巽, 坎, 艮, 坤, 震, 离, 兑)
            
        Returns:
            bool: 发送是否成功
        """
        data = {
            "数额": bagua_name
        }
        logger.info(f"发送八卦设置请求: 名称={bagua_name}")
        return await self.send_command(2, "八卦设置", data)
