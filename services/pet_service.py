from typing import Dict, Any, List, Optional
from .base_service import BaseService

class PetService(BaseService):
    """
    Service for handling pet-related operations.
    """

    async def get_pet_info(self, char_id: str) -> bool:
        """
        Get pet information for a character.
        """
        return await self.send_command(8, "获取宝宝信息", {"玩家id": char_id})

    async def modify_pet(self, char_id: str, pet_index: int, modify_data: Dict[str, Any]) -> bool:
        """
        Modify a pet's attributes, skills, etc.
        """
        return await self.send_command(
            8,
            "确定修改",
            {"玩家id": char_id, "修改数据": modify_data, "召唤兽编号": pet_index},
        )

    async def activate_merit(self, char_id: str) -> bool:
        """
        Activate merit record for a character.
        """
        return await self.send_command(8, "激活功德录", {"玩家id": char_id})

    async def modify_merit(self, char_id: str, modify_data: Dict[str, Any]) -> bool:
        """
        Modify merit record.
        """
        return await self.send_command(
            8, "修改功德录", {"玩家id": char_id, "修改数据": modify_data}
        )

    async def custom_pet_equip(self, char_id: str, equip_data: Dict[str, Any]) -> bool:
        """
        Customize pet equipment.
        """
        return await self.send_command(
            8, "定制宝宝装备", {"玩家id": char_id, "装备数据": equip_data}
        )

    async def get_mount(self, char_id: str) -> bool:
        """
        Get mount information.
        """
        return await self.send_command(8, "获取坐骑", {"玩家id": char_id})

    async def modify_mount(self, char_id: str, modify_data: Dict[str, Any]) -> bool:
        """
        Modify mount attributes and skills.
        """
        return await self.send_command(
            8, "坐骑修改", {"玩家id": char_id, "修改数据": modify_data}
        )
