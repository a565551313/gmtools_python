# GMTools Python - 梦江南超级GM工具

> **版本**: 2.0.0  
> **语言**: Python 3.8+  
> **许可证**: 私有项目

---

## 📋 项目概述

**GMTools Python** 是"梦江南超级GM工具"的 Python 移植版/增强版，是一个功能强大的游戏管理后台系统。项目提供两套可并行使用的管理入口：

- **🖥️ 桌面端 GUI（PyQt6）**：面向 GM 日常操作，Discord 风格现代界面
- **🌐 Web API（FastAPI）**：RESTful 接口与静态管理页面，支持远程调用与权限控制

两种入口底层共享同一套 **TCP 游戏服通信客户端**，通过 **MessagePack + 自定义加密** 协议与游戏服务器通信。

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        GMTools Python                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐              ┌──────────────────────┐       │
│   │  桌面端 GUI   │              │     Web API 服务      │       │
│   │  (PyQt6)     │              │     (FastAPI)        │       │
│   │  main.py     │              │     api_main.py      │       │
│   └──────┬───────┘              └──────────┬───────────┘       │
│          │                                  │                   │
│          └──────────┬───────────────────────┘                   │
│                     ▼                                           │
│          ┌─────────────────────┐                                │
│          │   业务模块/服务层    │                                │
│          │   modules/services  │                                │
│          └──────────┬──────────┘                                │
│                     ▼                                           │
│   ┌─────────────────────────────────────────────────────┐      │
│   │              网络通信层 (network/)                   │      │
│   │    GMToolsClient + MessagePack + 自定义加密          │      │
│   └──────────────────────────┬──────────────────────────┘      │
│                              ▼                                  │
│                     ┌────────────────┐                          │
│                     │   游戏服务器    │                          │
│                     │   TCP:8080     │                          │
│                     └────────────────┘                          │
│                                                                 │
│   ┌─────────────────────────────────────────────────────┐      │
│   │              数据层 (database/)                      │      │
│   │         SQLite + 用户/权限/审计日志                   │      │
│   └─────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows / Linux / macOS

### 安装依赖

```bash
pip install -r requirements.txt
```

### 主要依赖项

| 依赖包 | 版本 | 用途 |
|--------|------|------|
| PyQt6 | ≥6.5.0 | 桌面GUI框架 |
| msgpack | ≥1.0.0 | 数据序列化 |
| FastAPI | ≥0.104.0 | Web API框架 |
| uvicorn | ≥0.24.0 | ASGI服务器 |
| pydantic | ≥2.0.0 | 数据验证 |
| PyJWT | ≥2.8.0 | JWT认证 |
| bcrypt | ≥4.1.0 | 密码哈希 |

### 启动桌面端

```bash
python main.py
```

### 启动 API 服务

```bash
python api_main.py --host 0.0.0.0 --port 8000
```

---

## 📁 项目结构

```
gmtools_python/
├── main.py                 # 桌面端入口
├── api_main.py             # API服务入口
├── Config.json             # 运行时配置
├── requirements.txt        # Python依赖
├── gmtools.db              # SQLite数据库
│
├── network/                # 网络通信层
│   ├── client.py           # TCP客户端实现
│   └── dynamic_header.py   # 动态包头计算
│
├── modules/                # GUI功能模块
│   ├── base_module.py      # 模块基类
│   ├── account_recharge_module.py  # 账号充值
│   ├── character_module.py # 角色管理
│   ├── pet_module.py       # 宠物管理
│   ├── equipment_module.py # 装备定制
│   ├── gift_module.py      # 物品赠送
│   └── game_module.py      # 游戏管理
│
├── services/               # API业务服务层
│   ├── base_service.py     # 服务基类
│   ├── account_service.py  # 账号服务
│   ├── character_service.py # 角色服务
│   ├── pet_service.py      # 宠物服务
│   ├── equipment_service.py # 装备服务
│   ├── gift_service.py     # 礼物服务
│   └── game_service.py     # 游戏服务
│
├── routes/                 # API路由层
│   ├── user_routes.py      # 用户管理
│   ├── permission_routes.py # 权限管理
│   ├── activity_routes.py  # 活动管理
│   ├── message_routes.py   # 消息管理
│   └── item_gift_routes.py # 道具赠送
│
├── auth/                   # 认证与授权
│   ├── __init__.py         # JWT认证工具
│   ├── dependencies.py     # FastAPI依赖
│   ├── permission_checker.py # 权限检查
│   └── level_permissions.py # 等级权限
│
├── database/               # 数据库层
│   ├── connection.py       # 数据库连接
│   ├── models.py           # 用户/审计模型
│   ├── permissions.py      # 权限模型
│   ├── activation_code.py  # 激活码
│   └── level_config.py     # 等级配置
│
├── ui/                     # GUI界面层
│   ├── login_window.py     # 登录窗口
│   ├── main_window.py      # 主窗口
│   └── discord_main_window.py # Discord风格主窗口
│
├── utils/                  # 工具类
│   └── encryptor.py        # 自定义加密器
│
├── config/                 # 配置管理
│   ├── settings.py         # 静态配置
│   ├── config_manager.py   # 配置管理器
│   └── security_config.py  # 安全配置
│
├── static/                 # 静态资源
├── frontend/               # Vue前端项目
├── scripts/                # 辅助脚本
└── docs/                   # 文档目录
```

---

## 🎯 核心功能模块

### 1. 账号管理 (Account)
- 账号充值（货币、GM等级、技能等）
- 账号封禁/解封
- IP封禁管理
- 密码修改
- 称号发放

### 2. 角色管理 (Character)
- 角色信息查询
- 属性修改
- 道具恢复

### 3. 宠物管理 (Pet)
- 宠物信息查询
- 属性/技能修改
- 天生技能管理
- 坐骑管理
- 宠物装备

### 4. 装备定制 (Equipment)
- 装备定制（武器/防具）
- 灵饰定制
- 宝宝装备定制
- 词条定制

### 5. 物品赠送 (Gift)
- 道具发放
- 宝石发放
- CDK卡号生成
- 充值类型管理

### 6. 游戏管理 (Game)
- 全服广播
- 公告发布
- 经验倍率设置
- 难度设置
- 等级上限
- 活动触发

---

## 🔐 认证与权限系统

### 用户角色

| 角色 | 说明 | 权限 |
|------|------|------|
| user | 普通用户 | 基于等级的权限 |
| admin | 管理员 | 用户管理权限 |
| super_admin | 超级管理员 | 所有权限 |

### 等级体系（Level）

用户等级范围为 1-10，不同等级对应不同的功能权限：

- **Level 1-3**: 基础只读权限
- **Level 4-6**: 部分操作权限
- **Level 7-9**: 高级操作权限
- **Level 10**: 完全权限

### 权限检查逻辑

1. `super_admin` 角色：全部允许
2. `level >= 10`：全部允许
3. 其他：按 `LevelPermission` 配置判断

### 权限通配符支持

- `"*"`：全权限
- `"category.*"`：某类下全权限

---

## 🔌 API 接口概览

### 系统接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API运行状态 |
| `/docs` | GET | Swagger文档 |
| `/user-management` | GET | 用户管理页面 |
| `/level-permissions` | GET | 权限配置页面 |

### 游戏服操作接口

所有游戏服操作使用统一格式：

```json
POST /api/{module}
{
    "function": "method_name",
    "args": {"key": "value"}
}
```

| 模块 | 端点 |
|------|------|
| 账号 | `/api/account` |
| 宠物 | `/api/pet` |
| 装备 | `/api/equipment` |
| 礼物 | `/api/gift` |
| 角色 | `/api/character` |
| 游戏 | `/api/game` |

### 用户管理接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/users/register` | POST | 用户注册 |
| `/api/users/login` | POST | 用户登录 |
| `/api/users/me` | GET | 当前用户信息 |
| `/api/users/me` | PUT | 更新用户信息 |
| `/api/users/me/change-password` | POST | 修改密码 |

---

## 🔒 通信协议

### 数据包结构

```
┌─────────────┬──────────────────────────────────┐
│   包头(4B)   │         MessagePack数据          │
└─────────────┴──────────────────────────────────┘
```

### 加密流程

1. **发送**: 原文 → GBK编码 → Base64编码 → 字符替换加密 → MessagePack打包
2. **接收**: MessagePack解包 → 字符替换解密 → Base64解码 → GBK解码 → 原文

### 命令格式

业务命令封装为 Lua table 字符串：

```lua
do local ret={
    ["文本"]="命令名",
    ["玩家id"]="12345",
    ["数额"]=100
} return ret end
```

---

## ⚙️ 配置说明

### Config.json

```json
{
    "Login": {
        "Account": "账号名",
        "Password": "密码哈希",
        "RememberPassword": true,
        "AutoLogin": false
    },
    "Server": {
        "Host": "127.0.0.1",
        "Port": 8080
    },
    "api_host": "127.0.0.1",
    "api_port": 8000,
    "api_auto_start": true
}
```

### config/settings.py

包含默认游戏服地址、GM账号、协议分隔符等静态配置。

---

## 📊 数据库表结构

### 主要表

| 表名 | 说明 |
|------|------|
| users | 用户信息 |
| audit_logs | 审计日志 |
| permissions | 权限字典 |
| level_permissions | 等级权限关系 |
| activation_codes | 激活码 |
| messages | 站内消息 |

---

## 🛠️ 开发指南

### 新增游戏服命令（API）

1. 在 `services/<xxx>_service.py` 添加方法
2. 在 `api_main.py::FUNCTION_PERMISSIONS` 添加权限映射
3. 前端调用 `/api/<module>` 接口

### 新增GUI功能模块

1. 在 `modules/` 创建模块类，继承 `BaseModule`
2. 实现 `init_ui()` 方法
3. 在 `ui/main_window.py` 添加 Tab

---

## ⚠️ 安全注意事项

1. **生产环境必须**修改 `auth/__init__.py` 中的 `SECRET_KEY`
2. **建议禁用** `password_plain` 明文密码存储
3. **收敛CORS**：将 `allow_origins=["*"]` 改为可信域名
4. **关闭调试日志**：生产环境统一使用 `logging` 模块

---

## 📞 技术支持

如有问题，请联系项目维护者。

---

**© 2024 GMTools Python Project. All Rights Reserved.**
