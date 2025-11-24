from typing import Dict, Any, List, Optional
from .base_service import BaseService

class GameService(BaseService):
    """
    Service for handling game management operations (Command 6).
    """

    def send_broadcast(self, content: str) -> bool:
        """
        Send a system broadcast.
        """
        return self.send_command(6, "发送广播", {"数据": content})

    def send_announcement(self, content: str) -> bool:
        """
        Send a system announcement.
        """
        return self.send_command(6, "发送公告", {"数据": content})

    def set_exp_rate(self, rate: str) -> bool:
        """
        Set experience rate.
        """
        return self.send_command(6, "经验倍率", {"数据": rate})

    def set_difficulty(self, rate: str) -> bool:
        """
        Set game difficulty.
        """
        return self.send_command(6, "游戏难度", {"数据": rate})

    def set_level_cap(self, rate: str) -> bool:
        """
        Set level cap.
        """
        return self.send_command(6, "等级上限", {"数据": rate})

    def trigger_activity(self, activity_name: str) -> bool:
        """
        Trigger a game activity or toggle a system switch.
        """
        return self.send_command(6, activity_name, {})
