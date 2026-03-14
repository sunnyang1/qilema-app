#!/bin/bash

# 起了吗App - 本地部署脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        起了吗App - 本地 Docker 部署脚本                     ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker 未安装${NC}"
    echo "请先安装 Docker Desktop:"
    echo "  1. 访问 https://docs.docker.com/desktop/setup/install/mac-install/"
    echo "  2. 下载并安装 Docker Desktop for Mac"
    exit 1
fi

# 检查 Docker 是否运行
if ! docker info &> /dev/null; then
    echo -e "${YELLOW}⚠️  Docker 未运行${NC}"
    echo "正在启动 Docker Desktop..."
    open /Applications/Docker.app

    # 等待 Docker 启动
    echo -n "等待 Docker 启动"
    for i in {1..30}; do
        if docker info &> /dev/null; then
            echo ""
            echo -e "${GREEN}✅ Docker 已启动${NC}"
            break
        fi
        echo -n "."
        sleep 2
    done

    if ! docker info &> /dev/null; then
        echo ""
        echo -e "${RED}❌ Docker 启动超时，请手动启动 Docker Desktop${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Docker 版本: $(docker --version)${NC}"
echo -e "${GREEN}✅ Docker Compose 版本: $(docker-compose --version)${NC}"
echo ""

# 选择部署模式
echo -e "${BLUE}请选择部署模式:${NC}"
echo "  1) 开发环境 (推荐，支持热重载)"
echo "  2) 生产环境 (完整配置)"
echo "  3) 仅基础设施 (仅 PostgreSQL + Redis)"
echo ""
read -p "请输入选项 [1-3]: " choice

case $choice in
    1)
        echo -e "${BLUE}🚀 启动开发环境...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
        ;;
    2)
        echo -e "${BLUE}🚀 启动生产环境...${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
        ;;
    3)
        echo -e "${BLUE}🚀 启动基础设施...${NC}"
        docker-compose up -d postgres redis
        ;;
    *)
        echo -e "${YELLOW}⚠️  无效选项，使用默认开发环境${NC}"
        docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
        ;;
esac

echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""

# 显示服务状态
echo -e "${BLUE}📊 服务状态:${NC}"
docker-compose ps

echo ""
echo -e "${BLUE}🔗 访问地址:${NC}"
echo "  • API 服务: http://localhost:8000"
echo "  • Nginx 代理: http://localhost"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis: localhost:6379"

echo ""
echo -e "${BLUE}📋 常用命令:${NC}"
echo "  查看日志:     docker-compose logs -f"
echo "  停止服务:     docker-compose down"
echo "  重启服务:     docker-compose restart"
echo "  进入容器:     docker-compose exec backend bash"
echo ""

# 健康检查
echo -e "${BLUE}🏥 健康检查...${NC}"
sleep 5

if curl -s http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✅ 后端服务健康${NC}"
else
    echo -e "${YELLOW}⚠️  后端服务启动中，请稍后再检查${NC}"
fi
