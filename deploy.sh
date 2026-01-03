#!/bin/bash

# 一键部署脚本 - 适用于已安装MySQL和Nginx的服务器

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== hex-auth 授权中心一键部署脚本 ===${NC}"

# 1. 检查依赖
echo -e "${YELLOW}1. 检查依赖...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: 未安装Docker！${NC}"
    echo -e "${YELLOW}请先安装Docker: https://docs.docker.com/get-docker/${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}错误: 未安装Docker Compose！${NC}"
    echo -e "${YELLOW}请先安装Docker Compose: https://docs.docker.com/compose/install/${NC}"
    exit 1
fi

# 2. 配置环境变量
echo -e "${YELLOW}2. 配置环境变量...${NC}"

# 检查是否存在.env文件
if [ ! -f .env ]; then
    echo -e "${YELLOW}创建.env文件...${NC}"
    cat > .env << EOF
# 数据库配置
DATABASE_URL=mysql+pymysql://root:password@host.docker.internal:3306/hex_auth

# JWT配置
SECRET_KEY=your-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# RSA配置
RSA_PRIVATE_KEY_PATH=./keys/private.pem
RSA_PUBLIC_KEY_PATH=./keys/public.pem
EOF
    echo -e "${GREEN}.env文件创建成功！${NC}"
    echo -e "${YELLOW}请编辑.env文件，配置正确的数据库连接信息${NC}"
    echo -e "${YELLOW}提示: 可以使用 host.docker.internal 或宿主机IP连接MySQL${NC}"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 3. 创建简化的docker-compose文件
echo -e "${YELLOW}3. 创建简化的docker-compose文件...${NC}"

cat > docker-compose-easy.yml << EOF
version: '3.8'

services:
  # 后端服务
  backend:
    build: ./backend
    container_name: hex-auth-backend
    restart: always
    env_file: .env
    ports:
      - "8000:8000"
    extra_hosts:
      - "host.docker.internal:host-gateway"
  
  # 前端服务
  frontend:
    build: ./frontend
    container_name: hex-auth-frontend
    restart: always
    ports:
      - "8080:80"
    depends_on:
      - backend
EOF

echo -e "${GREEN}docker-compose-easy.yml创建成功！${NC}"

# 4. 检查并创建后端密钥目录
echo -e "${YELLOW}4. 检查密钥目录...${NC}"
mkdir -p backend/keys

# 5. 构建并启动服务
echo -e "${YELLOW}5. 构建并启动服务...${NC}"
echo -e "${YELLOW}提示: 首次构建可能需要较长时间，请耐心等待${NC}"
docker-compose -f docker-compose-easy.yml up -d --build

# 6. 等待服务启动
echo -e "${YELLOW}6. 等待服务启动...${NC}"
sleep 5

# 7. 检查服务状态
echo -e "${YELLOW}7. 检查服务状态...${NC}"
docker-compose -f docker-compose-easy.yml ps

# 8. 显示访问地址
echo -e "${GREEN}=== 部署完成！ ===${NC}"
echo -e "${GREEN}后端API地址: http://localhost:8000${NC}"
echo -e "${GREEN}前端访问地址: http://localhost:8080${NC}"
echo -e "${GREEN}API文档地址: http://localhost:8000/docs${NC}"
echo -e "${YELLOW}=== 宿主机Nginx配置建议 ===${NC}"
echo -e "${YELLOW}请在宿主机Nginx中添加以下配置:${NC}"
echo -e "server {
    listen 80;
    server_name your-domain.com;
    
    # 前端代理
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # 后端API代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}"
echo -e "${GREEN}=== 部署脚本执行完成！ ===${NC}"
