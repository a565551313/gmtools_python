
### 3. 启动 API 服务

```bash
python api_main.py
```

或指定端口:

```bash
python api_main.py --host 0.0.0.0 --port 8000
```

### 4. 访问 API 文档

打开浏览器访问:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API 接口说明

### 公开接口 (无需认证)

#### 1. 用户注册
```http
POST /api/users/register
Content-Type: application/json

{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123",
  "full_name": "测试用户"
}
```

#### 2. 用户登录
```http
POST /api/users/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

响应:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@gmtools.com",
    "role": "super_admin",
    ...
  }
}
```

### 需要认证的接口

所有需要认证的接口都需要在请求头中携带 Token:

```http
Authorization: Bearer <your_access_token>
```

#### 3. 获取当前用户信息
```http
GET /api/users/me
Authorization: Bearer <token>
```

#### 4. 更新当前用户信息
```http
PUT /api/users/me
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "full_name": "新名字"
}
```

#### 5. 修改密码
```http
POST /api/users/me/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "oldpassword123",
  "new_password": "newpassword123"
}
```

#### 6. 获取操作日志
```http
GET /api/users/me/logs?limit=50
Authorization: Bearer <token>
```

### 管理员接口

#### 7. 获取用户列表
```http
GET /api/users/?limit=100&offset=0
Authorization: Bearer <admin_token>
```

#### 8. 获取指定用户
```http
GET /api/users/{user_id}
Authorization: Bearer <admin_token>
```

#### 9. 更新用户角色
```http
PUT /api/users/{user_id}/role
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "role": "admin"
}
```

#### 10. 更新用户状态 (启用/禁用)
```http
PUT /api/users/{user_id}/status
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "is_active": false
}
```

#### 11. 重置用户密码
```http
POST /api/users/{user_id}/reset-password
Authorization: Bearer <admin_token>
Content-Type: application/json

{
  "new_password": "newpassword123"
}
```

#### 12. 删除用户
```http
DELETE /api/users/{user_id}
Authorization: Bearer <admin_token>
```

#### 13. 获取所有操作日志
```http
GET /api/users/logs/all?limit=100&offset=0
Authorization: Bearer <admin_token>
```

## 🔐 安全配置

### 修改 JWT 密钥

编辑 `auth/__init__.py` 文件:

```python
SECRET_KEY = "your-secret-key-change-this-in-production-gmtools-2024"
```

**⚠️ 重要**: 生产环境请务必修改为强随机密钥!

### 修改 Token 过期时间

编辑 `auth/__init__.py` 文件:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 小时
```

## 📊 数据库结构

### users 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| username | VARCHAR(50) | 用户名 (唯一) |
| email | VARCHAR(100) | 邮箱 (唯一) |
| password_hash | VARCHAR(255) | 密码哈希 |
| full_name | VARCHAR(100) | 全名 |
| role | VARCHAR(20) | 角色 |
| is_active | BOOLEAN | 是否激活 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| last_login | TIMESTAMP | 最后登录时间 |

### audit_logs 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 用户ID |
| action | VARCHAR(100) | 操作类型 |
| resource | VARCHAR(100) | 资源类型 |
| details | TEXT | 详细信息 |
| ip_address | VARCHAR(45) | IP地址 |
| created_at | TIMESTAMP | 创建时间 |

## 🧪 测试示例

### 使用 curl 测试

1. **注册用户**
```bash
curl -X POST http://localhost:8000/api/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

2. **登录获取 Token**
```bash
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

3. **使用 Token 访问受保护接口**
```bash
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <your_token>"
```

### 使用 Python 测试

```python
import requests

# 登录
response = requests.post(
    "http://localhost:8000/api/users/login",
    json={"username": "admin", "password": "admin123"}
)
data = response.json()
token = data["access_token"]

# 获取用户信息
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/users/me",
    headers=headers
)
print(response.json())
```

## 🔧 集成到现有 GMTools

用户管理系统已集成到 `api_main.py`,可以与现有的 GM 工具功能配合使用:

1. **保护现有 API** - 使用 `Depends(get_current_active_user)` 保护路由
2. **权限控制** - 使用 `Depends(get_current_admin_user)` 限制管理员操作
3. **审计日志** - 记录所有重要操作

示例:
```python
from auth.dependencies import get_current_active_user

@app.post("/api/account")
async def account_endpoint(
    request: ModuleRequest,
    current_user: User = Depends(get_current_active_user)
):
    # 只有登录用户才能访问
    return await handle_service_request(account_service, request)
```

## 📝 注意事项

1. **数据库文件**: SQLite 数据库文件位于 `gmtools_python/gmtools.db`
2. **备份**: 定期备份数据库文件
3. **密码安全**: 使用 bcrypt 加密,不可逆
4. **Token 安全**: Token 包含用户信息,请妥善保管
5. **生产部署**: 修改 SECRET_KEY 和其他安全配置

## 🎯 下一步

- [ ] 添加邮箱验证
- [ ] 添加忘记密码功能
- [ ] 添加双因素认证 (2FA)
- [ ] 添加 OAuth2 第三方登录
- [ ] 添加用户权限细粒度控制
- [ ] 添加 API 访问频率限制

## 📞 支持

如有问题,请查看:
- API 文档: http://localhost:8000/docs
- 日志文件: 查看控制台输出
- 数据库: 使用 SQLite 客户端查看 `gmtools.db`
