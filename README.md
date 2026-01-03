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

hex-auth支持两种主要部署方式，根据您的环境和需求选择合适的方案：

### 部署方式1：前后端Docker部署（连接已有的MySQL和Nginx）

如果您的服务器已经安装了MySQL和Nginx，可以使用此方案，只部署前后端服务。

#### 1. 准备工作
- 确保服务器已安装Docker和Docker Compose
- 确保MySQL已创建数据库 `hex_auth`
- 确保Nginx已配置好反向代理

#### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 数据库连接配置（连接到已有的MySQL）
DATABASE_URL="mysql+pymysql://root:password@localhost:3306/hex_auth"

# JWT配置
SECRET_KEY="your-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# RSA配置
RSA_PRIVATE_KEY_PATH="./keys/private.pem"
RSA_PUBLIC_KEY_PATH="./keys/public.pem"
```

#### 3. 构建并启动前后端容器

```bash
# 构建后端容器
docker build -t hex-auth-backend ./backend

# 构建前端容器
docker build -t hex-auth-frontend ./frontend

# 运行后端容器
docker run -d --name hex-auth-backend -p 8000:8000 --env-file ./.env hex-auth-backend

# 运行前端容器
docker run -d --name hex-auth-frontend -p 8080:80 hex-auth-frontend
```

#### 4. 配置服务器Nginx

在 `/etc/nginx/conf.d/` 目录下创建 `hex-auth.conf` 文件：

```nginx
server {
    listen 80;
    server_name www.shiliu.icu;  # 替换为您的域名
    
    # 前端代理
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # 管理员API代理
    location /admin {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_connect_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

#### 5. 重启Nginx服务

```bash
# 检查Nginx配置语法
nginx -t

# 重启Nginx服务
systemctl restart nginx
```

### 部署方式2：Docker Compose部署（含MySQL容器）

如果您的服务器没有安装MySQL，可以使用此方案，一键部署完整的服务栈，包括MySQL数据库。

#### 1. 创建docker-compose.yml文件

在项目根目录创建 `docker-compose.yml` 文件：

```yaml
version: '3.8'

# 数据库服务
services:
  # MySQL数据库
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
    networks:
      - hex-auth-network

  # 后端API服务
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: hex-auth-backend
    restart: always
    depends_on:
      - mysql
    environment:
      # 数据库连接配置（连接到容器内的MySQL）
      DATABASE_URL: "mysql+pymysql://root:root@mysql:3306/hex_auth"
      SECRET_KEY: "your-secret-key"
      ALGORITHM: "HS256"
      ACCESS_TOKEN_EXPIRE_MINUTES: "30"
    ports:
      - "8000:8000"
    networks:
      - hex-auth-network

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
    networks:
      - hex-auth-network

# 网络配置
networks:
  hex-auth-network:
    driver: bridge

# 数据卷配置
volumes:
  mysql-data:
```

#### 2. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

#### 3. 访问服务

- 前端地址：`http://your-server-ip`
- 后端API：`http://your-server-ip:8000`

### Dockerfile说明

#### 后端Dockerfile (backend/Dockerfile)

```dockerfile
FROM python:3.12

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用代码
COPY . .

# 创建密钥目录
RUN mkdir -p /app/keys

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 前端Dockerfile (frontend/Dockerfile)

```dockerfile
FROM node:20 as build

# 设置工作目录
WORKDIR /app

# 安装依赖
COPY package*.json ./
RUN npm install

# 复制应用代码
COPY . .

# 构建生产版本
RUN npm run build

# 使用Nginx作为前端服务器
FROM nginx:alpine

# 复制构建产物到Nginx静态目录
COPY --from=build /app/dist /usr/share/nginx/html

# 复制Nginx配置文件
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动Nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### 前端Nginx配置 (frontend/nginx.conf)

```nginx
server {
    listen 80;
    server_name localhost;
    
    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # 静态资源缓存配置
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /usr/share/nginx/html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
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
- 项目地址：https://github.com/HexLabX/hex-auth
- 邮箱：yshiliu@126.com
