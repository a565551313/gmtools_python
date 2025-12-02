# 🎉 GMTools 用户管理系统 - 快速开始

## ✅ 已完成的工作

您的 FastAPI + SQLite 用户管理系统已经完全集成到 `gmtools_python` 项目中!

### 📁 新增文件结构

```
gmtools_python/
├── database/                    # 数据库层
│   ├── __init__.py
│   ├── connection.py           # SQLite 连接管理
│   └── models.py               # 用户和日志模型
├── auth/                        # 认证层
│   ├── __init__.py             # JWT 工具
│   ├── user_service.py         # 用户认证服务
│   └── dependencies.py         # FastAPI 依赖项
├── routes/                      # API 路由
│   ├── __init__.py
│   └── user_routes.py          # 用户管理路由
├── init_db.py                   # 交互式初始化脚本
├── init_db_quick.py            # 快速初始化脚本
├── test_user_system.py         # 完整测试脚本
├── USER_MANAGEMENT_README.md   # 详细文档
├── gmtools.db                  # SQLite 数据库文件
└── api_main.py                 # 已更新,集成用户管理
```

## 🚀 立即开始使用

### 1️⃣ 启动 API 服务

```bash
cd d:\MENG20251006\allgmtools\gmtools_python
python api_main.py
```

### 2️⃣ 访问 API 文档

打开浏览器访问: **http://localhost:8000/docs**

### 3️⃣ 默认管理员账号

- **用户名**: `admin`
- **密码**: `admin123`
- **邮箱**: `admin@gmtools.com`
- **角色**: `super_admin`

## 📝 快速测试

### 方式 1: 使用 Swagger UI (推荐)

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
5. 点击 "Execute"
6. 复制返回的 `access_token`
7. 点击页面右上角的 "Authorize" 按钮
8. 输入: `Bearer <your_token>`
9. 现在可以测试所有需要认证的接口了!

### 方式 2: 使用测试脚本

```bash
# 确保 API 服务正在运行
python test_user_system.py
```

这个脚本会自动测试所有功能:
- ✅ 用户注册
- ✅ 用户登录
- ✅ 获取用户信息
- ✅ 更新用户信息
- ✅ 修改密码
- ✅ 管理员操作(角色管理、禁用用户等)
- ✅ 操作日志

### 方式 3: 使用 curl

```bash
# 登录获取 Token
curl -X POST http://localhost:8000/api/users/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"admin123\"}"

# 使用 Token 访问受保护接口
curl -X GET http://localhost:8000/api/users/me \
  -H "Authorization: Bearer <your_token>"
```

## 🎯 核心功能

### 🔐 认证功能
- [x] JWT Token 认证
- [x] bcrypt 密码加密
- [x] Token 自动过期 (24小时)
- [x] 安全的密码哈希存储

### 👤 用户管理
- [x] 用户注册
- [x] 用户登录
- [x] 获取/更新用户信息
- [x] 修改密码
- [x] 查看操作日志

### 👨‍💼 管理员功能
- [x] 查看所有用户
- [x] 更新用户角色
- [x] 启用/禁用用户
- [x] 重置用户密码
- [x] 删除用户
- [x] 查看所有操作日志

### 📊 审计日志
- [x] 自动记录所有重要操作
- [x] 记录 IP 地址
- [x] 按用户查询日志
- [x] 全局日志查询

## 🔧 配置说明

### 修改 JWT 密钥 (重要!)

编辑 `auth/__init__.py`:

```python
SECRET_KEY = "your-secret-key-change-this-in-production"  # 改成强随机密钥
```

### 修改 Token 过期时间

编辑 `auth/__init__.py`:

```python
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 默认 24 小时
```

## 📖 API 接口列表

### 公开接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/users/register` | 用户注册 |
| POST | `/api/users/login` | 用户登录 |

### 用户接口 (需要认证)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users/me` | 获取当前用户信息 |
| PUT | `/api/users/me` | 更新当前用户信息 |
| POST | `/api/users/me/change-password` | 修改密码 |
| GET | `/api/users/me/logs` | 获取操作日志 |

### 管理员接口 (需要管理员权限)
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users/` | 获取用户列表 |
| GET | `/api/users/{user_id}` | 获取指定用户 |
| PUT | `/api/users/{user_id}/role` | 更新用户角色 |
| PUT | `/api/users/{user_id}/status` | 启用/禁用用户 |
| POST | `/api/users/{user_id}/reset-password` | 重置密码 |
| DELETE | `/api/users/{user_id}` | 删除用户 |
| GET | `/api/users/logs/all` | 获取所有日志 |

## 🔗 集成到现有 GMTools

用户管理系统已经集成到 `api_main.py`,您可以轻松保护现有的 GM 工具接口:

### 示例 1: 保护现有接口

```python
from auth.dependencies import get_current_active_user
from database.models import User

@app.post("/api/account")
async def account_endpoint(
    request: ModuleRequest,
    current_user: User = Depends(get_current_active_user)  # 添加这行
):
    """只有登录用户才能访问"""
    return await handle_service_request(account_service, request)
```

### 示例 2: 限制管理员权限

```python
from auth.dependencies import get_current_admin_user

@app.post("/api/game")
async def game_endpoint(
    request: ModuleRequest,
    admin_user: User = Depends(get_current_admin_user)  # 只有管理员
):
    """只有管理员才能访问"""
    return await handle_service_request(game_service, request)
```

### 示例 3: 记录操作日志

```python
from database.models import AuditLog
from auth.dependencies import get_client_ip

@app.post("/api/account")
async def account_endpoint(
    request_data: ModuleRequest,
    http_request: Request,
    current_user: User = Depends(get_current_active_user)
):
    result = await handle_service_request(account_service, request_data)
    
    # 记录操作
    AuditLog.create(
        user_id=current_user.id,
        action="ACCOUNT_OPERATION",
        resource="account",
        details=f"{current_user.username} 执行了 {request_data.function}",
        ip_address=get_client_ip(http_request)
    )
    
    return result
```

## 📚 更多文档

详细文档请查看: `USER_MANAGEMENT_README.md`

## ⚠️ 注意事项

1. **生产环境部署**:
   - 修改 `SECRET_KEY` 为强随机密钥
   - 使用 HTTPS
   - 配置防火墙
   - 定期备份 `gmtools.db`

2. **数据库备份**:
   ```bash
   # 备份数据库
   copy gmtools.db gmtools.db.backup
   ```

3. **重置管理员密码**:
   ```bash
   python init_db.py
   # 选择重置密码
   ```

## 🎊 完成!

您的用户管理系统已经准备就绪!

- ✅ 数据库已初始化
- ✅ 管理员账号已创建
- ✅ API 路由已注册
- ✅ 文档已生成

现在就启动 API 服务开始使用吧! 🚀

```bash
python api_main.py
```

访问: http://localhost:8000/docs
