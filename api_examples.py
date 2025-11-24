
# API Examples Definitions

ACCOUNT_EXAMPLES = {
    "recharge_currency": {
        "summary": "充值货币",
        "value": {
            "function": "recharge_currency",
            "args": {"account": "test_user", "currency_type": "yuanbao", "amount": 1000}
        }
    },
    "send_travel_fee": {
        "summary": "发送路费",
        "value": {
            "function": "send_travel_fee",
            "args": {"account": "test_user", "player_id": "123456"}
        }
    },
    "recharge_gm_level": {
        "summary": "充值GM等级",
        "value": {
            "function": "recharge_gm_level",
            "args": {"player_id": "123456", "amount": 100, "gm_level": "1"}
        }
    },
    "manage_account_ban": {
        "summary": "封禁账号",
        "value": {
            "function": "manage_account",
            "args": {"command": "ban_account", "target_id": "test_user", "id_type": "账号"}
        }
    },
    "change_password": {
        "summary": "修改密码",
        "value": {
            "function": "change_password",
            "args": {"account": "test_user", "new_password": "new_password123"}
        }
    },
    "give_title": {
        "summary": "给予称谓",
        "value": {
            "function": "give_title",
            "args": {"player_id": "123456", "title": "至尊VIP"}
        }
    },
    "recharge_skill": {
        "summary": "充值经验/技能",
        "value": {
            "function": "recharge_skill",
            "args": {"player_id": "123456", "amount": 10000, "skill_type": "充值经验"}
        }
    },
    "recharge_faction": {
        "summary": "充值帮派/积分",
        "value": {
            "function": "recharge_faction",
            "args": {"player_id": "123456", "amount": 500, "faction_type": "充值帮贡"}
        }
    },
    "recharge_gm_coin": {
        "summary": "充值GM币",
        "value": {
            "function": "recharge_gm_coin",
            "args": {"player_id": "123456", "amount": 100}
        }
    },
    "recharge_record": {
        "summary": "充值记录",
        "value": {
            "function": "recharge_record",
            "args": {"player_id": "123456"}
        }
    },
    "set_bagua": {
        "summary": "八卦设置",
        "value": {
            "function": "set_bagua",
            "args": {"bagua_name": "乾"}
        }
    }
}

PET_EXAMPLES = {
    "get_pet_info": {
        "summary": "获取宝宝信息",
        "value": {
            "function": "get_pet_info",
            "args": {"char_id": "123456"}
        }
    },
    "modify_pet": {
        "summary": "修改宝宝属性",
        "value": {
            "function": "modify_pet",
            "args": {
                "char_id": "123456",
                "pet_index": 1,
                "modify_data": {
                    "等级": 180,
                    "气血": 10000,
                    "攻击": 2000
                }
            }
        }
    },
    "activate_merit": {
        "summary": "激活功德录",
        "value": {
            "function": "activate_merit",
            "args": {"char_id": "123456"}
        }
    },
    "custom_pet_equip": {
        "summary": "定制宝宝装备",
        "value": {
            "function": "custom_pet_equip",
            "args": {
                "char_id": "123456",
                "equip_data": {
                    "type": "护腕",
                    "level": 150,
                    "attrs": {"伤害": 50, "命中": 50}
                }
            }
        }
    }
}

EQUIPMENT_EXAMPLES = {
    "get_equipment": {
        "summary": "获取角色装备",
        "value": {
            "function": "get_equipment",
            "args": {"char_id": "123456"}
        }
    },
    "send_equipment": {
        "summary": "发送装备",
        "value": {
            "function": "send_equipment",
            "args": {
                "char_id": "123456",
                "equip_data": {
                    "pos": 1,
                    "id": 1001,
                    "attrs": {"伤害": 100}
                }
            }
        }
    },
    "get_affix": {
        "summary": "获取词条信息",
        "value": {
            "function": "get_affix",
            "args": {"char_id": "123456"}
        }
    },
    "modify_affix": {
        "summary": "修改词条",
        "value": {
            "function": "modify_affix",
            "args": {
                "char_id": "123456",
                "affix_data": {
                    "pos": 1,
                    "affix_list": ["无级别限制", "永不磨损"]
                }
            }
        }
    }
}

GIFT_EXAMPLES = {
    "give_item": {
        "summary": "赠送道具",
        "value": {
            "function": "give_item",
            "args": {"player_id": "123456", "item_id": "item_001", "count": 10}
        }
    },
    "give_gem": {
        "summary": "赠送宝石",
        "value": {
            "function": "give_gem",
            "args": {"player_id": "123456", "gem_id": "gem_001", "count": 5}
        }
    },
    "generate_cdk": {
        "summary": "生成CDK",
        "value": {
            "function": "generate_cdk",
            "args": {"type": "gift_pack_1", "count": 10}
        }
    }
}

CHARACTER_EXAMPLES = {
    "get_character_info": {
        "summary": "获取角色信息",
        "value": {
            "function": "get_character_info",
            "args": {"char_id": "123456"}
        }
    },
    "recover_character_props": {
        "summary": "恢复角色道具",
        "value": {
            "function": "recover_character_props",
            "args": {"char_id": "123456"}
        }
    },
    "modify_character": {
        "summary": "修改角色属性",
        "value": {
            "function": "modify_character",
            "args": {
                "char_id": "123456",
                "modify_data_str": "{['等级']=175, ['门派']=1}"
            }
        }
    }
}

GAME_EXAMPLES = {
    "send_broadcast": {
        "summary": "发送系统广播",
        "value": {
            "function": "send_broadcast",
            "args": {"content": "系统广播测试消息"}
        }
    },
    "send_announcement": {
        "summary": "发送系统公告",
        "value": {
            "function": "send_announcement",
            "args": {"content": "系统公告测试消息"}
        }
    },
    "set_exp_rate": {
        "summary": "设置经验倍率",
        "value": {
            "function": "set_exp_rate",
            "args": {"rate": "2.0"}
        }
    },
    "trigger_activity": {
        "summary": "触发活动",
        "value": {
            "function": "trigger_activity",
            "args": {"activity_name": "双倍经验"}
        }
    }
}
