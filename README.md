# hex-auth 授权中心系统

hex-auth 是一个功能完整的授权中心系统，用于管理软件产品的授权、客户端设备和审计日志。

## 技术栈

### 后端
- **框架**: FastAPI 0.104.1
- **ORM**: SQLAlchemy 2.0.23
- **数据库**: MySQL
- **认证**: JWT (JSON Web Tokens)
- **依赖管理**: pip

### 前端
- **框架**: Vue 3.5.13
- **语言**: TypeScript 5.6.2
- **构建工具**: Vite 6.0.5
- **状态管理**: Pinia 2.2.5
- **UI库**: Naive UI 2.39.0
- **HTTP客户端**: Axios 1.7.7

## 项目结构

```
hex-auth/
├── backend/                  # 后端代码
│   ├── alembic/              # 数据库迁移工具
│   ├── app/                  # 应用主目录
│   │   ├── admin/            # 管理员API
│   │   ├── api/              # 客户端API
│   │   ├── core/             # 核心配置
│   │   ├── models/           # 数据模型
│   │   ├── schemas/          # 数据验证
│   │   └── main.py           # 应用入口
│   ├── .env                  # 环境变量配置
│   ├── create_db.py          # 数据库初始化脚本
│   └── requirements.txt      # 依赖列表
├── frontend/                 # 前端代码
│   ├── dist/                 # 构建输出
│   ├── public/               # 静态资源
│   ├── src/                  # 源代码
│   │   ├── api/              # API请求
│   │   ├── components/       # Vue组件
│   │   ├── layouts/          # 布局组件
│   │   ├── pages/            # 页面组件
│   │   ├── router/           # 路由配置
│   │   └── stores/           # 状态管理
│   └── package.json          # 依赖配置
└── docker-compose.yml        # Docker部署配置
```

## 功能特性

### 管理员功能
- 仪表盘：显示系统概览和统计数据
- 产品管理：创建、编辑和删除产品
- 授权管理：生成、编辑和吊销授权码
- 客户端管理：查看和管理客户端设备
- 审计日志：记录系统操作日志

### 客户端API
- 授权验证：验证授权码有效性
- 设备激活：激活客户端设备
- 状态检查：检查授权状态

## 快速开始

### 后端运行

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   创建 `.env` 文件，添加以下内容：
   ```
   # 数据库配置
   DATABASE_URL="mysql+pymysql://root:password@localhost:3306/hex_auth"
   
   # JWT配置
   SECRET_KEY="your-secret-key"
   ALGORITHM="HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   
   # RSA配置
   RSA_PRIVATE_KEY_PATH="./keys/private.pem"
   RSA_PUBLIC_KEY_PATH="./keys/public.pem"
   ```

3. **初始化数据库**
   ```bash
   python create_db.py
   ```

4. **启动开发服务器**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

### 前端运行

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

3. **构建生产版本**
   ```bash
   npm run build
   ```

## 部署

### Docker部署

1. **创建docker-compose.yml文件**
   ```yaml
   version: '3.8'
   
   services:
     # 数据库服务
     mysql:
       image: mysql:8.0
       container_name: hex-auth-mysql
       restart: always
       environment:
         MYSQL_ROOT_PASSWORD: root
         MYSQL_DATABASE: hex_auth
       ports:
         - "3306:3306"
       volumes:
         - mysql-data:/var/lib/mysql
     
     # 后端服务
     backend:
       build:
         context: ./backend
         dockerfile: Dockerfile
       container_name: hex-auth-backend
       restart: always
       depends_on:
         - mysql
       environment:
         DATABASE_URL: "mysql+pymysql://root:root@mysql:3306/hex_auth"
         SECRET_KEY: "your-secret-key"
       ports:
         - "8000:8000"
     
     # 前端服务
     frontend:
       build:
         context: ./frontend
         dockerfile: Dockerfile
       container_name: hex-auth-frontend
       restart: always
       depends_on:
         - backend
       ports:
         - "80:80"
   
   volumes:
     mysql-data:
   ```

2. **创建后端Dockerfile**
   ```dockerfile
   # backend/Dockerfile
   FROM python:3.12
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

3. **创建前端Dockerfile**
   ```dockerfile
   # frontend/Dockerfile
   FROM node:20 as build
   
   WORKDIR /app
   
   COPY package*.json ./
   RUN npm install
   
   COPY . .
   RUN npm run build
   
   # 使用Nginx部署
   FROM nginx:alpine
   
   COPY --from=build /app/dist /usr/share/nginx/html
   COPY nginx.conf /etc/nginx/conf.d/default.conf
   
   EXPOSE 80
   
   CMD ["nginx", "-g", "daemon off;"]
   ```

4. **创建前端Nginx配置**
   ```nginx
   # frontend/nginx.conf
   server {
       listen 80;
       server_name localhost;
       
       location / {
           root /usr/share/nginx/html;
           index index.html;
           try_files $uri $uri/ /index.html;
       }
       
       location /api {
           proxy_pass http://backend:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

5. **启动Docker服务**
   ```bash
   docker-compose up -d
   ```

## API文档

### 管理员API
- **仪表盘**: GET /admin/dashboard
- **产品管理**: GET/POST/PUT/DELETE /admin/product
- **授权管理**: GET/POST/PUT/DELETE /admin/license
- **客户端管理**: GET /admin/client
- **审计日志**: GET /admin/audit

### 客户端API
- **授权验证**: POST /api/v1/license/verify
- **设备激活**: POST /api/v1/license/activate
- **状态检查**: GET /api/v1/license/status

## 开发流程

### 后端开发
1. 创建数据模型 (`app/models/`)
2. 创建数据验证模式 (`app/schemas/`)
3. 创建API路由 (`app/admin/` 或 `app/api/`)
4. 运行数据库迁移: `alembic revision --autogenerate -m "message"`
5. 应用迁移: `alembic upgrade head`

### 前端开发
1. 创建页面组件 (`src/pages/`)
2. 配置路由 (`src/router/index.ts`)
3. 创建API请求 (`src/api/index.ts`)
4. 开发UI组件和交互逻辑

## 贡献指南

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目地址：https://github.com/yourusername/hex-auth
- 邮箱：your.email@example.com
