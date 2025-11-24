from typing import Dict, Any, List, Optional
from .base_service import BaseService

class CharacterService(BaseService):
    """
    Service for handling character-related operations.
    """

    def get_character_info(self, char_id: str) -> bool:
        """
        Get character information.
        """
        return self.send_command(7, "获取角色信息", {"玩家id": char_id})

    def recover_character_props(self, char_id: str) -> bool:
        """
        Recover character properties.
        """
        return self.send_command(7, "恢复角色道具", {"玩家id": char_id})

    def modify_character(self, char_id: str, modify_data_str: str) -> bool:
        """
        Modify character attributes.
        Note: modify_data_str is expected to be a pre-formatted Lua string.
        """
        return self.send_command(
            7, "确定修改", {"玩家id": char_id, "修改数据": modify_data_str}
        )
