from typing import Dict, Any, List, Optional
from .base_service import BaseService

class EquipmentService(BaseService):
    """
    Service for handling equipment-related operations.
    """

    def get_equipment(self, char_id: str) -> bool:
        """
        Get character equipment.
        """
        return self.send_command(4, "获取角色装备", {"玩家id": char_id})

    def send_equipment(self, char_id: str, equipment_data: Dict[str, Any]) -> bool:
        """
        Send customized equipment to character.
        """
        return self.send_command(
            4,
            "发送装备",
            {"玩家id": char_id, "装备数据": equipment_data},
        )

    def get_ornament(self, char_id: str) -> bool:
        """
        Get character ornaments.
        """
        return self.send_command(5, "获取角色灵饰", {"玩家id": char_id})

    def send_ornament(self, char_id: str, ornament_data: Dict[str, Any]) -> bool:
        """
        Send customized ornament to character.
        """
        return self.send_command(
            5,
            "发送灵饰",
            {"玩家id": char_id, "灵饰数据": ornament_data},
        )

    def get_pet_equipment(self, char_id: str) -> bool:
        """
        Get pet equipment.
        """
        return self.send_command(8, "获取宝宝装备", {"玩家id": char_id})

    def send_pet_equipment(self, char_id: str, pet_equip_data: Dict[str, Any]) -> bool:
        """
        Send customized pet equipment.
        """
        return self.send_command(
            8,
            "定制宝宝装备",
            {"玩家id": char_id, "装备数据": pet_equip_data},
        )

    def get_affix(self, char_id: str) -> bool:
        """
        Get equipment affixes.
        """
        return self.send_command(10, "获取装备词条", {"玩家id": char_id})

    def send_affix(self, char_id: str, affix_data: Dict[str, Any]) -> bool:
        """
        Modify equipment affixes.
        """
        return self.send_command(
            10, "装备词条", {"玩家id": char_id, "修改数据": affix_data}
        )
