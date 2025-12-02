# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

GMTools Python is a game management tool (梦江南超级GM工具) with two interfaces:
- **PyQt6 Desktop GUI** (`main.py`) - Desktop application for game administrators
- **FastAPI REST API** (`api_main.py`) - Web API for remote management

The tool communicates with a game server using TCP sockets, MessagePack serialization, and custom encryption to send Lua commands.

## Commands

### Start Development

```powershell
# Install dependencies
pip install -r requirements.txt

# Run desktop GUI application
python main.py

# Run REST API server (default port 8000)
python api_main.py

# Run API on custom host/port
python api_main.py --host 0.0.0.0 --port 8000
```

### Database

```powershell
# Initialize database with admin user (interactive)
python init_db.py

# Quick database initialization
python init_db_quick.py
```

### Testing

```powershell
# Run user system tests (requires API server running)
python test_user_system.py

# Run syntax check on a file
python -m py_compile <file.py>
```

### Linting

```powershell
# Run flake8
flake8 <file_or_directory>

# Run black formatter
black <file_or_directory>

# Run pylint
pylint <file_or_directory>
```

## Architecture

### Dual Entry Points

1. **Desktop GUI** (`main.py`):
   - Uses `GMToolsClient` for network communication
   - UI components in `ui/` inherit from `modules/base_module.py`
   - Modules handle both UI rendering and command sending

2. **REST API** (`api_main.py`):
   - FastAPI application with JWT authentication
   - Services in `services/` inherit from `services/base_service.py`
   - Services are stateless wrappers around `GMToolsClient`
   - Routes in `routes/` define API endpoints

### Network Protocol

The `network/client.py` (`GMToolsClient`) manages:
- TCP socket connection to game server (default: `127.0.0.1:8080`)
- MessagePack serialization/deserialization
- Custom encryption via `utils/encryptor.py`
- Dynamic packet headers via `network/dynamic_header.py`

Commands are sent as Lua table strings:
```lua
do local ret={["文本"]="命令名",["玩家id"]="12345",["数额"]=100} return ret end
```

### Service Layer (API)

Services (`services/`) handle business logic:
- Inherit from `BaseService` which provides `send_command()` and Lua formatting
- Use `ResponseDispatcher` to collect async responses from the game server
- Each service method is `async` and returns response data

### Module Layer (GUI)

Modules (`modules/`) are PyQt6 widgets:
- Inherit from `BaseModule` which provides `send_command()` and UI helpers
- `init_ui()` is abstract and must be implemented
- Use `FormField` and `ButtonGroup` helper classes for UI construction

### Authentication & Authorization

- `auth/__init__.py` - JWT token creation/verification, bcrypt password hashing
- `auth/dependencies.py` - FastAPI dependencies for route protection
- `auth/permission_checker.py` - Level-based permission checking
- `database/permissions.py` - Permission and LevelPermission models
- Users have both `role` (admin/user) and `level` (1-10) for granular permissions

### Database

SQLite database (`gmtools.db`) managed by:
- `database/connection.py` - Singleton connection manager with context managers
- `database/models.py` - User, AuditLog models
- `database/permissions.py` - Permission, LevelPermission models
- `database/activation_code.py` - Activation code management

### Configuration

- `config/settings.py` - Server host/port, GM credentials, protocol constants
- `Config.json` - Runtime configuration (login credentials, API settings, player history)
- `config/config_manager.py` - JSON config file management

## Key Patterns

### API Endpoint Pattern
All game operations use a unified endpoint pattern with function dispatch:
```python
@app.post("/api/<module>")
async def endpoint(request_data: ModuleRequest, current_user: AuthUser = Depends(get_current_active_user)):
    check_function_permission(current_user, "<module>", request_data.function)
    return await handle_service_request(service, request_data)
```

Request format:
```json
{"function": "method_name", "args": {"param1": "value1"}}
```

### Lua Command Building
Both `BaseService` and `BaseModule` use `_build_lua_command()` to construct commands:
- Keys are quoted: `["key"]`
- String values are quoted: `"value"`
- Numeric values are unquoted: `123`
- Nested dicts become Lua tables: `{["nested"]=...}`

### Response Collection (API)
The `ResponseDispatcher` in `api_main.py`:
1. Registers a collector before sending command
2. Waits for responses with timeout
3. Collects all responses (handles multi-packet responses)
4. Returns collected data to the service
