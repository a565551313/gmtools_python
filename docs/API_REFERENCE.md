# GMTools API Reference

This document provides a comprehensive reference for all API endpoints available in GMTools Python.

---

## Authentication

All API endpoints (except login and register) require JWT authentication.

### Headers

```
Authorization: Bearer <jwt_token>
```

---

## User Endpoints (`/api/users`)

### Register

```http
POST /api/users/register
Content-Type: application/json

{
    "username": "string",
    "email": "string",
    "password": "string"
}
```

**Response (200)**:
```json
{
    "status": "success",
    "message": "Registration successful",
    "data": {
        "user": { ... }
    }
}
```

---

### Login

```http
POST /api/users/login
Content-Type: application/json

{
    "username": "string",
    "password": "string"
}
```

**Response (200)**:
```json
{
    "status": "success",
    "data": {
        "access_token": "jwt_token_here",
        "token_type": "bearer",
        "user": { ... }
    }
}
```

---

### Get Current User

```http
GET /api/users/me
Authorization: Bearer <token>
```

**Response (200)**:
```json
{
    "status": "success",
    "data": {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com",
        "level": 10,
        "role": "super_admin",
        "is_active": true
    }
}
```

---

### Change Password

```http
POST /api/users/me/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
    "old_password": "string",
    "new_password": "string"
}
```

---

## Game Server Operation Endpoints

All game server operations follow a unified interface pattern.

### Unified Request Format

```http
POST /api/{module}
Authorization: Bearer <token>
Content-Type: application/json

{
    "function": "method_name",
    "args": {
        "param1": "value1",
        "param2": "value2"
    }
}
```

### Unified Response Format

```json
{
    "status": "success",
    "data": { ... },
    "message": "optional message"
}
```

---

## Account Module (`/api/account`)

### Available Functions

| Function | Description | Required Args |
|----------|-------------|---------------|
| `recharge_currency` | Recharge currency | `player_id`, `amount`, `currency_type` |
| `send_travel_fee` | Send travel fee | `player_id`, `amount` |
| `recharge_gm_level` | Set GM level | `player_id`, `gm_level` |
| `manage_account` | Ban/Unban account | `player_id`, `action` |
| `change_password` | Change password | `player_id`, `new_password` |
| `give_title` | Give title | `player_id`, `title_id` |
| `recharge_skill` | Recharge crafting skill | `player_id`, `skill_type`, `amount` |
| `recharge_faction` | Recharge faction contribution | `player_id`, `amount` |
| `recharge_gm_coin` | Recharge GM coins | `player_id`, `amount` |
| `recharge_record` | Get player info | `player_id` |
| `set_bagua` | Set bagua | `player_id`, `bagua_data` |

### Example: Recharge Currency

```http
POST /api/account
Authorization: Bearer <token>
Content-Type: application/json

{
    "function": "recharge_currency",
    "args": {
        "player_id": "10001",
        "amount": 10000,
        "currency_type": "gold"
    }
}
```

---

## Pet Module (`/api/pet`)

### Available Functions

| Function | Description | Required Args |
|----------|-------------|---------------|
| `get_pet_info` | Get pet information | `player_id` |
| `modify_pet` | Modify pet attributes | `player_id`, `pet_id`, `modifications` |
| `custom_pet_equip` | Customize pet equipment | `player_id`, `pet_id`, `equipment_data` |
| `get_mount` | Get mount info | `player_id` |
| `modify_mount` | Modify mount | `player_id`, `mount_data` |

### Example: Get Pet Info

```http
POST /api/pet
Authorization: Bearer <token>
Content-Type: application/json

{
    "function": "get_pet_info",
    "args": {
        "player_id": "10001"
    }
}
```

---

## Equipment Module (`/api/equipment`)

### Available Functions

| Function | Description | Required Args |
|----------|-------------|---------------|
| `get_equipment` | Get equipment | `player_id`, `equipment_type` |
| `send_equipment` | Send custom equipment | `player_id`, `equipment_data` |
| `get_ornament` | Get ornament | `player_id` |
| `send_ornament` | Send ornament | `player_id`, `ornament_data` |
| `get_pet_equipment` | Get pet equipment | `player_id`, `pet_id` |
| `send_pet_equipment` | Send pet equipment | `player_id`, `pet_id`, `equipment_data` |
| `get_affix` | Get custom affix | `player_id` |
| `send_affix` | Send custom affix | `player_id`, `affix_data` |

---

## Gift Module (`/api/gift`)

### Available Functions

| Function | Description | Required Args |
|----------|-------------|---------------|
| `give_item` | Give item to player | `player_id`, `item_id`, `count` |
| `give_gem` | Give gem to player | `player_id`, `gem_id`, `count` |
| `get_recharge_types` | Get recharge types | - |
| `get_recharge_card` | Get recharge cards | `type_id` |
| `generate_cdk` | Generate CDK codes | `type_id`, `count` |
| `generate_custom_cdk` | Generate custom CDK | `custom_code`, `type_id` |
| `new_recharge_type` | Create recharge type | `type_data` |
| `del_recharge_type` | Delete recharge type | `type_id` |

### Example: Give Item

```http
POST /api/gift
Authorization: Bearer <token>
Content-Type: application/json

{
    "function": "give_item",
    "args": {
        "player_id": "10001",
        "item_id": "item_001",
        "count": 10
    }
}
```

---

## Character Module (`/api/character`)

### Available Functions

| Function | Description | Required Args |
|----------|-------------|---------------|
| `get_character_info` | Get character info | `player_id` |
| `recover_character_props` | Recover character props | `player_id` |
| `modify_character` | Modify character | `player_id`, `modifications` |

---

## Game Module (`/api/game`)

### Available Functions

| Function | Description | Required Args |
|----------|-------------|---------------|
| `send_broadcast` | Send server broadcast | `message` |
| `send_announcement` | Send announcement | `title`, `content` |
| `set_exp_rate` | Set experience rate | `rate` |
| `set_difficulty` | Set game difficulty | `difficulty` |
| `set_level_cap` | Set level cap | `level` |
| `trigger_activity` | Trigger activity | `activity_id` |

### Example: Send Broadcast

```http
POST /api/game
Authorization: Bearer <token>
Content-Type: application/json

{
    "function": "send_broadcast",
    "args": {
        "message": "Server maintenance in 10 minutes!"
    }
}
```

---

## Permission Endpoints

### Get All Permissions

```http
GET /api/permissions/all
Authorization: Bearer <token>
```

### Get Level Permissions

```http
GET /api/permissions/level/{level}
Authorization: Bearer <token>
```

### Update Level Permissions

```http
PUT /api/levels/{level}/permissions
Authorization: Bearer <token>
Content-Type: application/json

{
    "permissions": ["permission.code.1", "permission.code.2"]
}
```

---

## Activation Code Endpoints

### Generate Activation Codes

```http
POST /api/activation/generate
Authorization: Bearer <token>
Content-Type: application/json

{
    "level": 5,
    "count": 10,
    "expires_days": 30
}
```

### List Activation Codes

```http
GET /api/activation/list?page=1&limit=20
Authorization: Bearer <token>
```

### Use Activation Code

```http
POST /api/activation/use
Authorization: Bearer <token>
Content-Type: application/json

{
    "code": "XXXX-XXXX-XXXX"
}
```

### Delete Activation Code

```http
DELETE /api/activation/{code}
Authorization: Bearer <token>
```

---

## Error Responses

### 400 Bad Request

```json
{
    "detail": "Invalid arguments: description"
}
```

### 401 Unauthorized

```json
{
    "detail": "Could not validate credentials"
}
```

### 403 Forbidden

```json
{
    "detail": "Permission denied: required permission_code"
}
```

### 500 Internal Server Error

```json
{
    "detail": "Failed to send command"
}
```

---

## Permission Codes Reference

### Account Permissions

| Code | Description |
|------|-------------|
| `recharge.currency` | Recharge currency |
| `recharge.gm_level` | Set GM level |
| `recharge.crafting_skill` | Recharge crafting skill |
| `recharge.faction_contribution` | Recharge faction contribution |
| `recharge.gm_coin` | Recharge GM coins |
| `recharge.bagua` | Set bagua |
| `account.ban` | Ban/Unban account |
| `account.change_password` | Change password |
| `account.give_title` | Give title |
| `account.player_info` | View player info |
| `account.send_travel_fee` | Send travel fee |

### Pet Permissions

| Code | Description |
|------|-------------|
| `pet.get_info` | Get pet info |
| `pet.modify` | Modify pet |
| `pet.custom_equip` | Customize pet equipment |
| `pet.get_mount` | Get mount info |
| `pet.modify_mount` | Modify mount |

### Equipment Permissions

| Code | Description |
|------|-------------|
| `equipment.custom` | Custom equipment |
| `equipment.ornament` | Ornament operations |
| `equipment.affix` | Affix operations |

### Gift Permissions

| Code | Description |
|------|-------------|
| `gift.give_item` | Give item |
| `gift.give_gem` | Give gem |
| `gift.get_recharge_types` | Get recharge types |
| `gift.get_recharge_cards` | Get recharge cards |
| `gift.generate_cdk` | Generate CDK |
| `gift.generate_custom_cdk` | Generate custom CDK |
| `gift.new_recharge_type` | Create recharge type |
| `gift.del_recharge_type` | Delete recharge type |

### Character Permissions

| Code | Description |
|------|-------------|
| `character.get_info` | Get character info |
| `character.recover_props` | Recover props |
| `character.modify` | Modify character |

### Game Permissions

| Code | Description |
|------|-------------|
| `game.broadcast` | Send broadcast |
| `game.announcement` | Send announcement |
| `game.exp_rate` | Set experience rate |
| `game.difficulty` | Set difficulty |
| `game.level_cap` | Set level cap |
| `game.activity` | Trigger activity |

---

**© 2024 GMTools Python Project. All Rights Reserved.**
