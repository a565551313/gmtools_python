import json
import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理器 - 单例模式
    负责加载和保存 Config.json
    """
    _instance = None
    _config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Config.json")

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._config: Dict[str, Any] = {
            "Login": {
                "Account": "",
                "Password": "",
                "RememberPassword": False,
                "AutoLogin": False,
                "LastLogin": ""
            },
            "Server": {
                "Host": "127.0.0.1",
                "Port": 8080
            },
            "PlayerHistory": []
        }
        self._load_config()
        self._initialized = True

    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self._config_file):
            try:
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    # 深度合并配置，保留默认值
                    self._merge_config(self._config, saved_config)
                logger.info(f"已加载配置文件: {self._config_file}")
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
        else:
            logger.info("配置文件不存在，将使用默认配置")

    def _merge_config(self, default: Dict, saved: Dict):
        """递归合并配置"""
        for key, value in saved.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_config(default[key], value)
            else:
                default[key] = value

    def save_config(self):
        """保存配置文件"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            logger.info("配置文件已保存")
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        return self._config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置项"""
        self._config[key] = value
        self.save_config()

    # --- Login Section ---

    def get_login_config(self) -> Dict[str, Any]:
        return self._config.get("Login", {})

    def update_login_config(self, account: str = None, password: str = None, 
                          remember: bool = None, auto_login: bool = None, 
                          last_login: str = None):
        """更新登录配置"""
        login_cfg = self._config["Login"]
        if account is not None:
            login_cfg["Account"] = account
        if password is not None:
            login_cfg["Password"] = password
        if remember is not None:
            login_cfg["RememberPassword"] = remember
        if auto_login is not None:
            login_cfg["AutoLogin"] = auto_login
        if last_login is not None:
            login_cfg["LastLogin"] = last_login
        
        self.save_config()

    # --- Player History Section ---

    def get_player_history(self) -> List[str]:
        return self._config.get("PlayerHistory", [])

    def add_player_history(self, player_id: str):
        """添加玩家ID历史"""
        history = self._config["PlayerHistory"]
        if player_id in history:
            history.remove(player_id)
        history.insert(0, player_id)
        
        # 限制数量
        if len(history) > 10:
            self._config["PlayerHistory"] = history[:10]
            
        self.save_config()

    def remove_player_history(self, player_id: str):
        """移除玩家ID历史"""
        history = self._config["PlayerHistory"]
        if player_id in history:
            history.remove(player_id)
            self.save_config()

    def clear_player_history(self):
        """清空玩家ID历史"""
        self._config["PlayerHistory"] = []
        self.save_config()

    # --- Server Section ---

    def get_server_config(self) -> Dict[str, Any]:
        return self._config.get("Server", {"Host": "127.0.0.1", "Port": 8080})

    def update_server_config(self, host: str, port: int):
        """更新服务器配置"""
        self._config["Server"] = {
            "Host": host,
            "Port": port
        }
        self.save_config()
