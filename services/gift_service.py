from typing import Dict, Any, List, Optional
from .base_service import BaseService

class GiftService(BaseService):
    """
    Service for handling gift and CDK related operations.
    """

    def give_item(self, player_id: str, item_name: str, count: int = 1) -> bool:
        """
        Give item to character.
        :param player_id: 玩家ID
        :param item_name: 名称
        :param count: 数量
        """
        give_data = {
            "名称": item_name,
            "数量": count
        }
        return self.send_command(
            9, "给予道具", {"玩家id": player_id, "给予数据": give_data}
        )

    def give_gem(self, player_id: str, gem_name: str, mix_level: int = 1,max_level: int = 1) -> bool:
        """
        Give gem to character.
        :param player_id: 玩家ID
        :param gem_name: 名称
        :param mix_level: 最小等级
        :param max_level: 最大等级
        """
        give_data = {
            "名称": gem_name,
            "最小等级": mix_level,
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
