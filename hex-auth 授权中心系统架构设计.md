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
| 缓存 | Redis |
| 鉴权 | JWT（Admin） |
| 授权签名 | RSA |
| 数据迁移 | Alembic |

### 2.2 前端

| 模块 | 技术 |
|------|------|
| 框架 | Vue 3 |
| UI | Naive UI |
| 构建 | Vite |
| 状态管理 | Pinia |
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
│ MySQL / Redis                             │
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
- `/admin/product`
- `/admin/license`
- `/admin/client`
- `/admin/audit`

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
├── alembic/            # 数据迁移
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

- Dashboard（仪表盘）
- Products（产品管理）
- Licenses（授权管理）
- Clients（客户端管理）
- Audit Logs（审计日志）

### UI 原则

- 冷色 / 深色主题
- 高信息密度
- 表格 + Drawer / Modal 交互
- 工程化风格优先

---

## 12. 演进规划（预留）

- 多管理员角色（RBAC）
- 授权策略插件化
- 离线授权（独立模块）
- 客户端 SDK 标准化
- SaaS 化部署
