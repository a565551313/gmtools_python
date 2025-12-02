from typing import Dict, Any, List, Optional
from .base_service import BaseService
import logging

logger = logging.getLogger(__name__)

class GiftService(BaseService):
    """
    Service for handling gift and CDK related operations.
    """

    def give_item(self, player_id: str, item_name: str, count: int = 1, item_category: str = "default") -> bool:
        """
        Give item to character.
        :param player_id: 玩家ID
        :param item_name: 名称
        :param count: 数量
        :param item_category: 道具类别 (default/rare_items/currency)
        """
        # 安全验证
        from config.security_config import SecurityConfig
        
        # 验证数量
        is_valid, error_msg = SecurityConfig.validate_item_count(count, item_category)
        if not is_valid:
            logger.warning(f"道具数量验证失败: {error_msg}, 玩家ID: {player_id}, 道具: {item_name}, 数量: {count}")
            raise ValueError(f"参数验证失败: {error_msg}")
        
        # 记录敏感操作
        logger.info(f"[GIFT] 给予道具 - 玩家: {player_id}, 道具: {item_name}, 数量: {count}, 类别: {item_category}")
        
        give_data = {
            "名称": item_name,
            "数量": count
        }
        return self.send_command(
            9, "给予道具", {"玩家id": player_id, "给予数据": give_data}
        )

    def give_gem(self, player_id: str, gem_name: str, min_level: int = 1, max_level: int = 1) -> bool:
        """
        Give gem to character.
        :param player_id: 玩家ID
        :param gem_name: 名称
        :param min_level: 最小等级
        :param max_level: 最大等级
        """
        # 安全验证
        from config.security_config import SecurityConfig
        
        # 验证宝石等级
        is_valid, error_msg = SecurityConfig.validate_gem_level(min_level, max_level)
        if not is_valid:
            logger.warning(f"宝石等级验证失败: {error_msg}, 玩家ID: {player_id}, 宝石: {gem_name}")
            raise ValueError(f"参数验证失败: {error_msg}")
        
        # 记录敏感操作
        logger.info(f"[GIFT] 给予宝石 - 玩家: {player_id}, 宝石: {gem_name}, 等级: {min_level}-{max_level}")
        
        give_data = {
            "名称": gem_name,
            "最小等级": min_level,
            "最大等级": max_level
        }
        return self.send_command(
            9, "给予宝石", {"玩家id": player_id, "给予数据": give_data}
        )

    def get_recharge_types(self) -> bool:
        """
        Get available recharge types.
        """
        return self.send_command(9, "获取充值类型", {})

    def get_recharge_card(self, selected_type: str) -> bool:
        """
        Get recharge card numbers for a specific type.
        """
        return self.send_command(9, "获取充值卡号", {"生成文件": selected_type})

    def generate_cdk(self, selected_type: str, gen_data: Dict[str, Any]) -> bool:
        """
        Generate CDK cards.
        """
        return self.send_command(
            9,
            "生成CDK卡号",
            {"生成数据": gen_data, "生成文件": selected_type},
        )

    def generate_custom_cdk(self, selected_type: str, gen_data: Dict[str, Any]) -> bool:
        """
        Generate custom CDK card.
        """
        return self.send_command(
            9,
            "生成自定义CDK卡号",
            {"生成数据": gen_data, "生成文件": selected_type},
        )

    def new_recharge_type(self, type_name: str) -> bool:
        """
        Create a new recharge type.
        """
        return self.send_command(9, "新建充值类型", {"生成文件": type_name})

    def del_recharge_type(self, selected_type: str, type_name: str) -> bool:
        """
        Delete a recharge type (or card?).
        Note: The command name is "删除充值卡号" but it seems to delete types or specific cards.
        """
        return self.send_command(
            9, "删除充值卡号", {"生成文件": selected_type, "生成卡号": type_name}
        )
