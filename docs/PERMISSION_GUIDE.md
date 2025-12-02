# GMTools 权限系统指南

本文档详细说明了 GMTools 的 Level-Based 权限系统，包括权限定义、配置方法和开发指南。

## 1. 权限系统概述

GMTools 采用基于 Level 的 RBAC（Role-Based Access Control）模型。
- **Level (1-10)**: 每个等级相当于一个角色。
- **Permission**: 细粒度的功能权限（如 `account.recharge`）。
- **LevelPermission**: 定义了每个 Level 拥有的权限集合。

用户被分配一个 Level，从而继承该 Level 的所有权限。

## 2. 权限列表

系统预定义了以下权限：

### 账号管理 (account)
- `account.view`: 查看账号信息
- `account.recharge`: 充值操作 (货币/GM等级)
- `account.freeze`: 冻结/解冻账号

### 宠物管理 (pet)
- `pet.give`: 发送宝宝
- `pet.modify`: 修改宝宝属性
- `pet.delete`: 删除宝宝

### 装备管理 (equipment)
- `equipment.give`: 发送装备
- `equipment.modify`: 修改装备属性
- `equipment.delete`: 删除装备

### 礼物道具 (gift)
- `gift.send`: 发送物品/宝石
- `gift.batch`: 批量生成/管理充值卡

### 角色管理 (character)
- `character.view`: 查看角色信息
- `character.modify`: 修改角色属性
- `character.delete`: 删除角色

### 游戏管理 (game)
- `game.announcement`: 发送公告/广播
- `game.maintenance`: 维护操作
- `game.config`: 游戏参数配置

## 3. 管理员指南

### 配置权限
1. 登录 GMTools 管理后台。
2. 进入 **用户管理** 页面。
3. 点击右上角的 **⚙️ 权限配置** 按钮。
4. 选择要配置的 **Level** (1-10)。
5. 勾选/取消勾选相应的权限。
6. 点击 **保存配置**。

### 用户管理
- **创建用户**: 指定用户的 Level，用户将自动获得该 Level 的权限。
- **修改 Level**: 修改用户的 Level 后，其权限会立即更新。

## 4. 开发指南

### 权限检查
在后端 API 中，使用 `require_permission` 依赖或 `check_function_permission` 函数进行权限控制。

#### 方式 1: 依赖注入 (适用于简单接口)
```python
from auth.permission_checker import require_permission

@router.post("/some-action")
async def some_action(user: User = Depends(require_permission("account.view"))):
    ...
```

#### 方式 2: 动态检查 (适用于多功能接口)
```python
from auth.permission_checker import has_permission

def check_function_permission(user, module, function):
    # 映射逻辑...
    if not has_permission(user, required_perm):
        raise HTTPException(status_code=403, detail="权限不足")
```

### 添加新权限
1. 在 `database/permissions.py` 或初始化脚本中添加新权限定义。
2. 运行初始化脚本更新数据库。
3. 在前端 `level-permissions.html` 中，新权限会自动显示（基于数据库数据）。

## 5. 默认权限模板

初始化时，系统会应用以下默认模板（可随时修改）：

- **Level 1**: 基础查看权限 (`account.view`, `gift.send`)
- **Level 2**: + 充值权限 (`account.recharge`, `pet.give`, `equipment.give`)
- **Level 3**: + 角色管理 (`character.view`, `character.modify`)
- **Level 5**: + 游戏管理 (`game.*`)
- **Level 10**: 所有权限 (`*`)
