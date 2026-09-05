# hex-auth 授权中心系统架构设计

hex-auth 是一个 **统一在线授权中心**，为 GUI / CLI / Service / Plugin 等多形态程序提供 **在线激活、心跳校验、授权吊销与后台管理** 能力。

---

## 1. 项目背景与目标

### 1.1 背景

随着桌面程序、内部工具、商业化 GUI / CLI 程序的增多，需要一个 **统一、可复用、可管控** 的授权中心来解决：

- 授权分散、逻辑重复
- 客户端安全性低
- 授权不可控、不可撤销
- 无统一管理后台

### 1.2 设计目标

- 统一授权入口（多产品）
- 在线授权（实时校验、即时吊销）
- 一卡一实例（或有限实例）
- 强服务端控制
- 全流程可审计
- 支持长期演进

### 1.3 当前版本约束（V1）

- ❌ 不支持离线授权
- ❌ 不提供用户账号体系
- ❌ 不做多管理员角色（仅 SUPER_ADMIN）

---

## 2. 技术选型

### 2.1 后端

| 模块 | 技术 |
|------|------|
| 语言 | Python 3.10+ |
| Web 框架 | FastAPI |
| ORM | SQLAlchemy |
| 数据库 | MySQL 8.x |
| 鉴权 | JWT（Admin） |
| 授权签名 | RSA |

### 2.2 前端

| 模块 | 技术 |
|------|------|
| 框架 | Vue 3 |
| UI | Naive UI |
| 构建 | Vite |
| 状态管理 | Pinia |
| 图标 | @iconify/vue |
| UI 风格 | https://www.qoder.com |

---

## 3. 系统总体架构

```
┌────────────────────────────────────────────┐
│ Admin Web Frontend                         │
│ Vue3 + Naive UI (qoder 风格)               │
└──────────────────────▲─────────────────────┘
                       │ Admin JWT
┌──────────────────────┴─────────────────────┐
│ License Center Backend                     │
│ FastAPI                                   │
├────────────────────────────────────────────┤
│ Admin Module (SUPER_ADMIN)                 │
│  ├─ Auth                                  │
│  ├─ Product Management                    │
│  ├─ License Management                    │
│  ├─ Client Monitor                        │
│  ├─ Revoke / Ban                          │
│  └─ Audit Log                             │
├────────────────────────────────────────────┤
│ License API (Client SDK)                  │
│  ├─ Activate                              │
│  ├─ Heartbeat                             │
│  └─ Status                                │
├────────────────────────────────────────────┤
│ MySQL                                     │
└────────────────────────────────────────────┘
```

---

## 4. 核心设计原则

- 授权逻辑 **全部在服务端**
- 客户端不存密钥，仅存 **公钥**
- 激活与校验解耦
- 管理 API 与授权 API 物理隔离
- 产品 / 授权 / 实例 **强隔离**
- 所有授权行为 **可审计、可追溯**

---

## 5. 核心领域模型

### 5.1 Product（产品）

- 授权的最小隔离单元
- 每个产品拥有 **独立 RSA 密钥对**

**字段：**

| 字段名 | 注释 |
|--------|------|
| product_code | 业务唯一标识 |
| name | 产品名称 |
| public_key | RSA公钥（客户端校验使用） |
| private_key | RSA私钥（服务端签名使用） |
| heartbeat_interval | 心跳间隔（秒） |
| status | 产品状态（启用/禁用） |
| created_at | 创建时间 |
| updated_at | 更新时间 |

### 5.2 License（授权卡密）

- 授权的核心凭证
- 只能绑定一个产品
- 可限制最大实例数

**字段：**

| 字段名 | 注释 |
|--------|------|
| license_key | 授权码（卡密） |
| product_code | 关联产品标识 |
| max_devices | 最大设备数限制 |
| expire_at | 过期时间 |
| status | 状态（未激活/已激活/已过期/已吊销） |
| remark | 备注信息 |
| created_at | 创建时间 |

### 5.3 Client（客户端实例）

- 一次激活对应一个实例
- 与 License 强绑定

**字段：**

| 字段名 | 注释 |
|--------|------|
| license_id | 关联授权ID |
| client_fp | 设备/实例指纹 |
| client_type | 客户端类型（GUI/CLI/Service/Plugin） |
| ip_address | 客户端IP地址 |
| last_heartbeat | 最后心跳时间 |
| status | 状态（正常/异常/已禁用） |
| created_at | 创建时间 |

### 5.4 AdminUser（管理员）

- 当前系统仅 SUPER_ADMIN
- 后台管理使用

**字段：**

| 字段名 | 注释 |
|--------|------|
| username | 用户名 |
| password_hash | 密码哈希值 |
| status | 状态（启用/禁用） |
| last_login | 最后登录时间 |
| created_at | 创建时间 |

### 5.5 AuditLog（审计日志）

- 记录所有关键管理操作
- 用于追责、回溯、安全审计

**字段：**

| 字段名 | 注释 |
|--------|------|
| admin_username | 操作用户名 |
| action | 操作类型（创建/更新/删除/禁用等） |
| target_type | 操作对象类型（产品/授权/客户端等） |
| target_id | 操作对象ID |
| detail | 操作详情（JSON格式） |
| created_at | 操作时间 |

---

## 6. 数据库表结构设计

### 6.1 products（产品表）

```sql
products(
  id PK COMMENT '主键ID',
  product_code UNIQUE COMMENT '产品唯一标识（业务主键）',
  name COMMENT '产品名称',
  public_key COMMENT 'RSA公钥（客户端校验使用）',
  private_key COMMENT 'RSA私钥（服务端签名使用）',
  heartbeat_interval COMMENT '心跳间隔（秒）',
  status COMMENT '产品状态（启用/禁用）',
  created_at COMMENT '创建时间',
  updated_at COMMENT '更新时间'
)
```

### 6.2 licenses（授权卡密表）

```sql
licenses(
  id PK COMMENT '主键ID',
  license_key UNIQUE COMMENT '授权码（卡密）',
  product_code COMMENT '关联产品标识',
  max_devices COMMENT '最大设备数限制',
  expire_at COMMENT '过期时间',
  status COMMENT '状态（未激活/已激活/已过期/已吊销）',
  remark COMMENT '备注信息',
  created_at COMMENT '创建时间'
)
```

### 6.3 clients（授权实例表）

```sql
clients(
  id PK COMMENT '主键ID',
  license_id FK COMMENT '关联授权ID',
  product_code COMMENT '产品标识',
  client_fp COMMENT '客户端指纹（设备唯一标识）',
  client_type COMMENT '客户端类型（GUI/CLI/Service/Plugin）',
  ip_address COMMENT '客户端IP地址',
  last_heartbeat COMMENT '最后心跳时间',
  status COMMENT '状态（正常/异常/已禁用）',
  created_at COMMENT '创建时间'
)
```

> **约束：** (license_id, client_fp) 唯一

### 6.4 admin_users（管理员表）

```sql
admin_users(
  id PK COMMENT '主键ID',
  username UNIQUE COMMENT '用户名',
  password_hash COMMENT '密码哈希值',
  status COMMENT '状态（启用/禁用）',
  last_login COMMENT '最后登录时间',
  created_at COMMENT '创建时间'
)
```

### 6.5 audit_logs（审计日志表）

```sql
audit_logs(
  id PK COMMENT '主键ID',
  admin_username COMMENT '操作用户名',
  action COMMENT '操作类型（创建/更新/删除/禁用等）',
  target_type COMMENT '操作对象类型（产品/授权/客户端等）',
  target_id COMMENT '操作对象ID',
  detail(JSON) COMMENT '操作详情（JSON格式）',
  created_at COMMENT '操作时间'
)
```

---

## 7. 授权协议设计

### 7.1 激活流程

```
Client
 └─ POST /api/v1/license/activate
      ├─ 校验 License
      ├─ 校验产品
      ├─ 绑定 client_fp
      └─ 返回 License Token
```

### 7.2 License Token 设计

```json
{
  "iss": "hex-auth",
  "product": "XRAY_GUI",
  "license_key": "XXXX-XXXX",
  "client_fp": "HASH",
  "iat": 1730000000,
  "exp": 1760000000
}
```

> **特性：**
> - RSA 私钥签名
> - 客户端仅校验
> - 不依赖 JWT

### 7.3 心跳机制

```
Client
 └─ POST /api/v1/license/heartbeat
      ├─ 校验 Token
      ├─ 校验 client_fp
      ├─ 更新 last_heartbeat
      └─ 失败即视为失效
```

---

## 8. API 架构设计

### 8.1 API 分区

| 类型 | 前缀 |
|------|------|
| Admin API | /admin/* |
| License API | /api/v1/* |

### 8.2 Admin API 模块

- `/admin/auth`
  - `POST /login` - 管理员登录
  - `GET /me` - 获取当前管理员信息
  - `POST /change-password` - 修改密码
- `/admin/product`
- `/admin/license`
- `/admin/client`
- `/admin/audit`
  - `GET /` - 获取审计日志列表（支持分页和筛选）
  - `GET /{log_id}` - 获取单条审计日志详情
  - `POST /clear` - 清空选中的审计日志
  - `POST /clear-all` - 清空所有审计日志
- `/admin/dashboard` - 仪表盘数据统计

### 8.3 License API 模块

- `/api/v1/license/activate`
- `/api/v1/license/heartbeat`
- `/api/v1/license/status`

---

## 9. 工程结构设计

### 9.1 后端（FastAPI）

```
backend/
├── app/
│   ├── admin/          # 管理后台模块
│   ├── api/            # 授权 API 模块
│   ├── core/           # 核心配置与工具
│   ├── models/         # 数据库模型
│   ├── schemas/        # 数据校验与序列化
│   ├── services/       # 业务逻辑层
│   └── main.py         # 应用入口
└── requirements.txt    # 依赖管理
```

### 9.2 前端（Vue3）

```
frontend/
├── src/
│   ├── api/            # API 调用
│   ├── layout/         # 布局组件
│   ├── pages/          # 页面组件
│   ├── store/          # 状态管理
│   └── router/         # 路由配置
└── vite.config.ts      # 构建配置
```

---

## 10. 安全设计

### 10.1 管理端安全

- JWT 登录认证
- bcrypt / argon2 密码加密
- 操作审计日志
- IP / 行为可扩展风控

### 10.2 授权安全

- RSA 非对称签名
- 公钥客户端校验
- 实时心跳机制
- 服务端即时吊销

---

## 11. 前端 UI 架构（Naive UI）

### 页面结构

- **Dashboard（仪表盘）** - 服务健康状态、统计数据、近期操作
- **Products（产品管理）** - 产品列表、创建/编辑/删除产品
- **Licenses（授权管理）** - 授权卡密列表、生成/吊销授权
- **Clients（客户端管理）** - 客户端实例监控、启用/禁用
- **Audit Logs（审计日志）** - 操作记录查看、批量清理
- **Profile（个人中心）** - 用户信息、修改密码

### UI 组件与特性

#### 全局组件
- **图标系统** - 使用 @iconify/vue 统一图标管理（Ant Design 图标集）
- **消息提示** - 全局 Message/Notification/Dialog 工具
- **骨架屏** - TableSkeleton（表格）、CardSkeleton（卡片）

#### 页面功能
- **搜索与筛选** - 所有列表页面支持实时搜索和多维度筛选
- **分页显示** - 表格数据分页，显示总数和当前页码
- **状态标识** - 可视化状态徽章（正常/异常/禁用等）
- **操作确认** - 关键操作（删除/禁用等）弹出确认对话框
- **批量操作** - 审计日志支持批量选择和删除

#### 布局设计
- **侧边栏导航** - 主要功能菜单（固定左侧）
- **顶部导航** - 页面标题、个人中心、退出登录
- **全屏布局** - 100% 高度，内容区域自适应滚动

### UI 原则

- 冷色 / 深色主题
- 高信息密度
- 表格 + Modal 交互
- 工程化风格优先
- 加载状态友好提示
- 错误处理清晰明确

---

## 12. 演进规划（预留）

- 授权策略插件化

---

## 13. 前端技术实现细节

### 13.1 关键技术问题解决

#### URL 重定向导致的认证丢失
**问题：** FastAPI 对不带尾部斜杠的路径（如 `/admin/dashboard`）会自动重定向到 `/admin/dashboard/`，在 307 重定向过程中会丢失 Authorization 请求头和 POST 请求体，导致 API 返回 401 或 422 错误。

**解决方案：**
- **GET 请求：** 统一使用带尾部斜杠的路径
- **POST/PUT/DELETE 请求：**
  - 根路由（如 `/admin/product/`）使用带尾部斜杠
  - ID 路由（如 `/admin/product/{id}`）不使用尾部斜杠
  - 动作路由（如 `/admin/license/{id}/revoke`）不使用尾部斜杠

**示例：**
```typescript
// ✅ 正确
api.get('/admin/dashboard/')
api.post('/admin/product/', payload)
api.put(`/admin/product/${id}`, data)
api.delete(`/admin/product/${id}`)
api.post(`/admin/license/${id}/revoke`)

// ❌ 错误 - 会导致307重定向，丢失 Authorization 请求头
api.post('/admin/product', payload)
```

#### 路由守卫时序问题
**问题：** 登录后立即跳转，localStorage 写入未完成时路由守卫已执行，导致被重定向回登录页。

**解决方案：**
- 使用 `router.push()` 而不是 `window.location.href`，避免页面刷新
- 在 token 写入后添加 100ms 延迟，确保 localStorage 完全写入
- 在 axios 拦截器中添加路径检查，避免登录页重复处理 401

#### FastAPI 路由顺序问题
**问题：** 在 FastAPI 中，参数化路由（如 `/{log_id}`）会匹配所有路径，包括具名路径（如 `/clear`）。如果 `/{log_id}` 路由定义在 `/clear` 之前，会导致 `POST /clear` 请求被错误地匹配到 `GET /{log_id}`，返回 "Method Not Allowed" 错误。

**解决方案：**
- 将具名路由（如 `/clear`、`/clear-all`）定义在参数化路由（如 `/{log_id}`）**之前**
- FastAPI 按照路由定义顺序进行匹配，先匹配到的优先
- 示例：
  ```python
  # ✅ 正确顺序
  @router.post("/clear")        # 具名路由在前
  @router.post("/clear-all")    # 具名路由在前
  @router.get("/{log_id}")      # 参数化路由在后
  ```

### 13.2 组件设计模式

#### 骨架屏组件
```typescript
// TableSkeleton.vue
withDefaults(defineProps<{
  columns?: number
  rows?: number
}>(), {
  columns: 6,
  rows: 5
})

// CardSkeleton.vue
withDefaults(defineProps<{
  count?: number
}>(), {
  count: 4
})
```

**注意：** 避免重复调用 `defineProps()`，会导致编译错误

#### 图标系统
```typescript
// icons/index.ts
export const icons = {
  dashboard: 'ant-design:dashboard-outlined',
  products: 'ant-design:appstore-outlined',
  // ... 更多图标
}

// 使用方式
<Icon :icon="icons.dashboard" />
```

### 13.3 API 调用最佳实践

#### 统一错误处理
```typescript
// api/index.ts - 响应拦截器
api.interceptors.response.use(
  (response) => {
    NProgress.done()
    return response.data  // 直接返回 data，简化调用
  },
  (error) => {
    NProgress.done()

    // 401 错误处理（仅在非登录页）
    if (error.response?.status === 401) {
      if (window.location.pathname !== '/login') {
        localStorage.removeItem('token')
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)
```

#### Form 数据提交
```typescript
// 使用 URLSearchParams 处理 form-data
await api.post('/admin/auth/login', new URLSearchParams({
  username: 'admin',
  password: 'password'
}))
```

### 13.4 状态管理与交互

#### 搜索与筛选
```typescript
// 实时搜索（防抖可优化）
const handleSearch = () => {
  currentPage.value = 1  // 重置到第一页
}

// 多维度筛选
const filteredData = computed(() => {
  let result = rawData.value

  if (searchText.value) {
    result = result.filter(item =>
      item.name.toLowerCase().includes(searchText.value.toLowerCase())
    )
  }

  if (statusFilter.value) {
    result = result.filter(item => item.status === statusFilter.value)
  }

  return result
})
```

#### 分页实现
```typescript
// 总页数计算
const totalPages = computed(() =>
  Math.ceil(filteredData.value.length / pageSize.value)
)

// 当前页数据
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})
```

### 13.5 前端性能优化建议

1. **骨架屏加载** - 数据加载时显示骨架屏，提升用户体验
2. **分页加载** - 大量数据分页显示，避免一次性渲染过多 DOM
3. **防抖搜索** - 搜索输入添加防抖（推荐 300ms），减少不必要的计算
4. **懒加载路由** - 使用 `import()` 动态导入页面组件
5. **图标按需加载** - @iconify/vue 自动按需加载，无需手动优化
6. **异步刷新列表** - 创建/更新操作后立即响应，列表在后台异步刷新

**异步刷新示例：**
```typescript
// 创建产品
const createProduct = async () => {
  isLoading.value = true
  try {
    await api.post('/admin/product/', payload)

    // 立即关闭模态框和显示成功消息
    showCreateModal.value = false
    Message.success('产品创建成功')

    // 重置表单
    createForm.value = { ... }

    // 立即关闭加载状态，用户可以继续操作
    isLoading.value = false

    // 在后台异步刷新列表（不使用await，不阻塞）
    fetchProducts()
  } catch (error) {
    Message.error('产品创建失败')
    isLoading.value = false
  }
}
```

### 13.6 后端性能优化

#### 审计日志事务优化
**问题：** 之前的实现在创建资源后立即记录审计日志并单独提交，导致每次操作需要两次数据库提交。

**优化方案：**
- 审计日志添加 `commit` 参数控制是否立即提交
- 将资源和审计日志在同一事务中提交
- 减少数据库 I/O 次数，提升性能

**实现：**
```python
# app/utils/audit_utils.py
def create_audit_log(
    db: Session,
    admin_username: str,
    action: str,
    target_type: str,
    target_id: Any,
    detail: Optional[dict] = None,
    target_instance: Optional[Any] = None,
    commit: bool = True  # 新增参数，默认True保持向后兼容
):
    # ... 创建审计日志 ...
    db.add(audit_log)

    if commit:
        db.commit()  # 仅在commit=True时提交

    return audit_log

# app/admin/product.py
@router.post("/")
def create_product(...):
    # ... 创建产品 ...
    db.add(db_product)

    # 记录审计日志（不单独提交）
    create_audit_log(
        db=db,
        admin_username=current_admin.username,
        action="创建",
        target_type="产品",
        target_id=db_product.id,
        target_instance=db_product,
        commit=False  # 不单独提交
    )

    # 统一提交（产品和审计日志一次性提交）
    db.commit()
    db.refresh(db_product)

    return db_product
```

**性能提升：**
- 创建产品从两次提交减少到一次
- 减少数据库往返次数，响应时间显著降低

---

## 14. 部署注意事项

### 14.1 环境变量配置

**后端 (.env)**
```env
DATABASE_URL=mysql+pymysql://user:pass@localhost:3306/hex_auth
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

**安全建议：**
- ⚠️ 生产环境必须修改默认密码和 JWT_SECRET_KEY
- ⚠️ 数据库不要暴露到公网
- ⚠️ 启用 HTTPS
- ⚠️ 配置防火墙规则

### 14.2 前端部署

**开发环境**
```bash
cd frontend
npm install
npm run dev  # 默认端口 3000
```

**生产环境**
```bash
npm run build
# 将 dist 目录部署到 Nginx/Caddy 等 Web 服务器
```

### 14.3 后端部署

**开发环境**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**生产环境**
```bash
# 使用 gunicorn + uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```
