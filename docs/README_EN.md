# GMTools Python - Mengjiangnan Super GM Tool

> **Version**: 2.0.0  
> **Language**: Python 3.8+  
> **License**: Proprietary

---

## 📋 Project Overview

**GMTools Python** is a Python port/enhanced version of the "Mengjiangnan Super GM Tool", a powerful game management backend system. The project provides two parallel management interfaces:

- **🖥️ Desktop GUI (PyQt6)**: For daily GM operations, featuring Discord-style modern UI
- **🌐 Web API (FastAPI)**: RESTful API with static management pages, supporting remote calls and permission control

Both interfaces share the same **TCP game server communication client**, communicating with game servers through **MessagePack + custom encryption** protocol.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        GMTools Python                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐              ┌──────────────────────┐       │
│   │  Desktop GUI │              │     Web API Service  │       │
│   │   (PyQt6)    │              │      (FastAPI)       │       │
│   │   main.py    │              │     api_main.py      │       │
│   └──────┬───────┘              └──────────┬───────────┘       │
│          │                                  │                   │
│          └──────────┬───────────────────────┘                   │
│                     ▼                                           │
│          ┌─────────────────────┐                                │
│          │  Business Modules/  │                                │
│          │  Services Layer     │                                │
│          └──────────┬──────────┘                                │
│                     ▼                                           │
│   ┌─────────────────────────────────────────────────────┐      │
│   │           Network Communication Layer (network/)     │      │
│   │    GMToolsClient + MessagePack + Custom Encryption   │      │
│   └──────────────────────────┬──────────────────────────┘      │
│                              ▼                                  │
│                     ┌────────────────┐                          │
│                     │  Game Server   │                          │
│                     │   TCP:8080     │                          │
│                     └────────────────┘                          │
│                                                                 │
│   ┌─────────────────────────────────────────────────────┐      │
│   │              Data Layer (database/)                  │      │
│   │         SQLite + Users/Permissions/Audit Logs        │      │
│   └─────────────────────────────────────────────────────┘      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Requirements

- Python 3.8 or higher
- Windows / Linux / macOS

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Main Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyQt6 | ≥6.5.0 | Desktop GUI framework |
| msgpack | ≥1.0.0 | Data serialization |
| FastAPI | ≥0.104.0 | Web API framework |
| uvicorn | ≥0.24.0 | ASGI server |
| pydantic | ≥2.0.0 | Data validation |
| PyJWT | ≥2.8.0 | JWT authentication |
| bcrypt | ≥4.1.0 | Password hashing |

### Start Desktop Client

```bash
python main.py
```

### Start API Service

```bash
python api_main.py --host 0.0.0.0 --port 8000
```

---

## 📁 Project Structure

```
gmtools_python/
├── main.py                 # Desktop entry point
├── api_main.py             # API service entry point
├── Config.json             # Runtime configuration
├── requirements.txt        # Python dependencies
├── gmtools.db              # SQLite database
│
├── network/                # Network communication layer
│   ├── client.py           # TCP client implementation
│   └── dynamic_header.py   # Dynamic packet header calculation
│
├── modules/                # GUI functional modules
│   ├── base_module.py      # Module base class
│   ├── account_recharge_module.py  # Account recharge
│   ├── character_module.py # Character management
│   ├── pet_module.py       # Pet management
│   ├── equipment_module.py # Equipment customization
│   ├── gift_module.py      # Item gifting
│   └── game_module.py      # Game management
│
├── services/               # API business service layer
│   ├── base_service.py     # Service base class
│   ├── account_service.py  # Account service
│   ├── character_service.py # Character service
│   ├── pet_service.py      # Pet service
│   ├── equipment_service.py # Equipment service
│   ├── gift_service.py     # Gift service
│   └── game_service.py     # Game service
│
├── routes/                 # API routing layer
│   ├── user_routes.py      # User management
│   ├── permission_routes.py # Permission management
│   ├── activity_routes.py  # Activity management
│   ├── message_routes.py   # Message management
│   └── item_gift_routes.py # Item gifting
│
├── auth/                   # Authentication & Authorization
│   ├── __init__.py         # JWT authentication utilities
│   ├── dependencies.py     # FastAPI dependencies
│   ├── permission_checker.py # Permission checking
│   └── level_permissions.py # Level-based permissions
│
├── database/               # Database layer
│   ├── connection.py       # Database connection
│   ├── models.py           # User/Audit models
│   ├── permissions.py      # Permission models
│   ├── activation_code.py  # Activation codes
│   └── level_config.py     # Level configuration
│
├── ui/                     # GUI interface layer
│   ├── login_window.py     # Login window
│   ├── main_window.py      # Main window
│   └── discord_main_window.py # Discord-style main window
│
├── utils/                  # Utilities
│   └── encryptor.py        # Custom encryptor
│
├── config/                 # Configuration management
│   ├── settings.py         # Static configuration
│   ├── config_manager.py   # Configuration manager
│   └── security_config.py  # Security configuration
│
├── static/                 # Static resources
├── frontend/               # Vue frontend project
├── scripts/                # Helper scripts
└── docs/                   # Documentation
```

---

## 🎯 Core Feature Modules

### 1. Account Management
- Account recharge (currency, GM level, skills, etc.)
- Account ban/unban
- IP ban management
- Password modification
- Title assignment

### 2. Character Management
- Character information query
- Attribute modification
- Item recovery

### 3. Pet Management
- Pet information query
- Attribute/skill modification
- Innate skill management
- Mount management
- Pet equipment

### 4. Equipment Customization
- Equipment customization (weapons/armor)
- Ornament customization
- Pet equipment customization
- Affix customization

### 5. Item Gifting
- Item distribution
- Gem distribution
- CDK code generation
- Recharge type management

### 6. Game Management
- Server-wide broadcast
- Announcement publishing
- Experience rate settings
- Difficulty settings
- Level cap adjustment
- Activity triggers

---

## 🔐 Authentication & Permission System

### User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| user | Regular user | Level-based permissions |
| admin | Administrator | User management permissions |
| super_admin | Super administrator | All permissions |

### Level System

User levels range from 1-10, with different levels granting different feature permissions:

- **Level 1-3**: Basic read-only permissions
- **Level 4-6**: Partial operational permissions
- **Level 7-9**: Advanced operational permissions
- **Level 10**: Full permissions

### Permission Check Logic

1. `super_admin` role: Always allowed
2. `level >= 10`: Always allowed
3. Others: Check against `LevelPermission` configuration

### Wildcard Permission Support

- `"*"`: Full permissions
- `"category.*"`: All permissions under a category

---

## 🔌 API Endpoints Overview

### System Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API status |
| `/docs` | GET | Swagger documentation |
| `/user-management` | GET | User management page |
| `/level-permissions` | GET | Permission configuration page |

### Game Server Operation Endpoints

All game server operations use a unified format:

```json
POST /api/{module}
{
    "function": "method_name",
    "args": {"key": "value"}
}
```

| Module | Endpoint |
|--------|----------|
| Account | `/api/account` |
| Pet | `/api/pet` |
| Equipment | `/api/equipment` |
| Gift | `/api/gift` |
| Character | `/api/character` |
| Game | `/api/game` |

### User Management Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/register` | POST | User registration |
| `/api/users/login` | POST | User login |
| `/api/users/me` | GET | Current user info |
| `/api/users/me` | PUT | Update user info |
| `/api/users/me/change-password` | POST | Change password |

---

## 🔒 Communication Protocol

### Packet Structure

```
┌─────────────┬──────────────────────────────────┐
│  Header(4B) │         MessagePack Data          │
└─────────────┴──────────────────────────────────┘
```

### Encryption Flow

1. **Send**: Plain text → GBK encoding → Base64 encoding → Character substitution encryption → MessagePack packing
2. **Receive**: MessagePack unpacking → Character substitution decryption → Base64 decoding → GBK decoding → Plain text

### Command Format

Business commands are encapsulated as Lua table strings:

```lua
do local ret={
    ["text"]="command_name",
    ["player_id"]="12345",
    ["amount"]=100
} return ret end
```

---

## ⚙️ Configuration

### Config.json

```json
{
    "Login": {
        "Account": "username",
        "Password": "password_hash",
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

Contains default game server address, GM account, protocol separator, and other static configurations.

---

## 📊 Database Schema

### Main Tables

| Table | Description |
|-------|-------------|
| users | User information |
| audit_logs | Audit logs |
| permissions | Permission dictionary |
| level_permissions | Level-permission relationships |
| activation_codes | Activation codes |
| messages | In-app messages |

---

## 🛠️ Development Guide

### Adding Game Server Commands (API)

1. Add method in `services/<xxx>_service.py`
2. Add permission mapping in `api_main.py::FUNCTION_PERMISSIONS`
3. Call `/api/<module>` endpoint from frontend

### Adding GUI Feature Module

1. Create module class in `modules/`, extending `BaseModule`
2. Implement `init_ui()` method
3. Add Tab in `ui/main_window.py`

---

## ⚠️ Security Considerations

1. **MUST change** `SECRET_KEY` in `auth/__init__.py` for production
2. **Recommend disabling** `password_plain` plaintext password storage
3. **Restrict CORS**: Change `allow_origins=["*"]` to trusted domains
4. **Disable debug logging**: Use `logging` module uniformly in production

---

## 📞 Technical Support

For issues, please contact the project maintainer.

---

**© 2024 GMTools Python Project. All Rights Reserved.**
