# 🎉 GMTools 用户管理系统 - 升级完成!

## ✅ 已完成的升级

您的 GMTools 系统已经完全升级为**基于 JWT 和用户等级的权限控制系统**!

---

## 🔄 主要变更

### 1️⃣ **用户表结构变更**

| 变更 | 旧字段 | 新字段 |
|------|--------|--------|
| ❌ 移除 | `full_name` (全名) | - |
| ✅ 新增 | - | `level` (用户等级 1-10) |

**用户等级说明**:
- **Level 1-2**: 普通用户
- **Level 3-4**: 中级用户
- **Level 5-6**: 高级用户
- **Level 7-9**: 资深用户
- **Level 10**: 最高等级(超级管理员)

---

### 2️⃣ **认证方式完全替换**

#### ❌ 旧方式(已移除):
```python
# 使用固定的 AUTH_TOKEN
token: bool = Depends(verify_token)
```

#### ✅ 新方式(JWT + Level):
```python
# 使用 JWT Token + 用户等级控制
current_user: User = Depends(require_level(1))
```

---

### 3️⃣ **API 接口权限等级**

所有 GM 工具接口现在都需要**用户登录**并满足**等级要求**:

| 接口 | 最低等级 | 说明 |
|------|---------|------|
| `/api/account` | Level 1 | 账号充值 |
| `/api/pet` | Level 1 | 宝宝管理 |
| `/api/equipment` | Level 1 | 装备管理 |
| `/api/gift` | Level 1 | 物品赠送 |
| `/api/character` | Level 3 | 角色管理(需要中级权限) |
| `/api/game` | Level 5 | 游戏管理(需要高级权限) |

---

### 4️⃣ **自动审计日志**

所有 GM 工具操作现在都会**自动记录**:
- ✅ 操作用户
- ✅ 操作时间
- ✅ 操作类型
- ✅ IP 地址
- ✅ 详细信息

---

## 🚀 如何使用

### 1. 启动 API 服务

```bash
cd d:\MENG20251006\allgmtools\gmtools_python
python api_main.py
```

### 2. 登录获取 Token

**方式 A: 使用 Swagger UI (推荐)**

1. 访问 http://localhost:8000/docs
2. 找到 `/api/users/login` 接口
3. 点击 "Try it out"
4. 输入:
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
5. 复制返回的 `access_token`
6. 点击页面右上角 "Authorize" 按钮
7. 输入: `Bearer <your_token>`
8. 现在可以访问所有接口了!

**方式 B: 使用 curl**

```bash
# 1. 登录获取 Token
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 返回:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "user": {...}
# }

# 2. 使用 Token 访问 GM 工具接口
curl -X POST http://localhost:8000/api/account \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"function":"recharge","args":{"account":"test","amount":1000}}'
```

**方式 C: 使用 Python**

```python
import requests

# 1. 登录
response = requests.post(
    "http://localhost:8000/api/users/login",
    json={"username": "admin", "password": "admin123"}
)
data = response.json()
token = data["access_token"]

# 2. 使用 Token 调用 GM 工具
headers = {"Authorization": f"Bearer {token}"}

# 账号充值
response = requests.post(
    "http://localhost:8000/api/account",
    headers=headers,
    json={
        "function": "recharge",
        "args": {"account": "test", "amount": 1000}
    }
)
print(response.json())
```

---

## 👥 用户管理

### 创建新用户

```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "operator1",
    "email": "operator1@example.com",
    "password": "password123",
    "level": 3
  }'
```

### 管理员操作(需要 admin 登录)

```bash
# 设置用户等级
curl -X PUT http://localhost:8000/api/users/{user_id}/level \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"level": 5}'

# 查看所有用户
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer <admin_token>"

# 查看操作日志
curl -X GET http://localhost:8000/api/users/logs/all \
  -H "Authorization: Bearer <admin_token>"
```

---

## 🎯 等级权限设计建议

根据您的业务需求,可以这样分配等级:

### 推荐配置

| 等级 | 角色 | 权限 |
|------|------|------|
| 1-2 | 客服 | 账号充值、宝宝管理、装备管理、物品赠送 |
| 3-4 | 运营 | + 角色管理 |
| 5-6 | 高级运营 | + 游戏管理 |
| 7-9 | 技术管理 | 所有功能 |
| 10 | 超级管理员 | 所有功能 + 用户管理 |

### 自定义等级要求

您可以随时修改 `api_main.py` 中的等级要求:

```python
@app.post("/api/character")
async def character_endpoint(
    current_user: AuthUser = Depends(require_level(3))  # 改成你想要的等级
):
    ...
```

或使用动态等级:

```python
from auth.level_permissions import require_level

@app.post("/api/custom-feature")
async def custom_feature(
    current_user: AuthUser = Depends(require_level(7))  # 需要等级 7
):
    ...
```

---

## 📊 查看审计日志

所有操作都会被记录,管理员可以查看:

```bash
# 查看所有日志
curl -X GET "http://localhost:8000/api/users/logs/all?limit=100" \
  -H "Authorization: Bearer <admin_token>"

# 查看自己的日志
curl -X GET "http://localhost:8000/api/users/me/logs?limit=50" \
  -H "Authorization: Bearer <your_token>"
```

日志包含:
- 用户名
- 操作类型 (ACCOUNT_OPERATION, PET_OPERATION, etc.)
- 资源类型
- 详细信息
- IP 地址
- 时间戳

---

## 🔧 配置说明

### 修改 JWT 密钥(重要!)

编辑 `auth/__init__.py`:

```python
SECRET_KEY = "your-super-secret-key-change-this"  # 改成强随机密钥
```

### 修改 Token 过期时间

编辑 `auth/__init__.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 默认 24 小时
```

---

## 🆕 新增功能

### 1. 基于等级的权限控制

```python
from auth.level_permissions import require_level

# 要求等级 >= 5
@app.post("/api/advanced")
async def advanced_feature(
    user: User = Depends(require_level(5))
):
    return {"message": f"欢迎,{user.username}!"}
```

### 2. 自动审计日志

```python
from database.models import AuditLog

AuditLog.create(
    user_id=current_user.id,
    action="CUSTOM_ACTION",
    resource="custom_resource",
    details="操作详情",
    ip_address="127.0.0.1"
)
```

### 3. 用户信息获取

```python
from auth.dependencies import get_current_active_user

@app.get("/api/profile")
async def get_profile(
    current_user: User = Depends(get_current_active_user)
):
    return {
        "username": current_user.username,
        "level": current_user.level,
        "role": current_user.role
    }
```

---

## ⚠️ 重要提醒

### 1. 旧的 Token 认证已移除

如果您有使用旧 `AUTH_TOKEN` 的客户端,需要更新为:
1. 先调用 `/api/users/login` 获取 JWT Token
2. 使用 JWT Token 访问其他接口

### 2. 所有接口都需要登录

现在**所有 GM 工具接口**都需要:
- ✅ 有效的 JWT Token
- ✅ 满足最低等级要求

### 3. 数据库已重置

旧的用户数据已清空,当前只有默认管理员:
- 用户名: `admin`
- 密码: `admin123`
- 等级: `10`
- 角色: `super_admin`

---

## 📚 完整文档

- **用户管理**: `USER_MANAGEMENT_README.md`
- **快速开始**: `QUICK_START.md`
- **API 文档**: http://localhost:8000/docs

---

## 🎊 升级完成!

您的系统现在拥有:
- ✅ 完整的用户认证系统
- ✅ 基于等级的权限控制
- ✅ 自动审计日志
- ✅ JWT Token 安全认证
- ✅ 灵活的权限配置

立即启动并体验新系统:

```bash
python api_main.py
```

访问: http://localhost:8000/docs

有任何问题随时问我! 😊
