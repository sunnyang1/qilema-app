#!/bin/bash

# 停止本地部署

echo "🛑 停止起了吗App本地服务..."

# 停止开发环境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml down 2>/dev/null || true

# 停止生产环境
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down 2>/dev/null || true

# 停止基础服务
docker-compose down 2>/dev/null || true

echo "✅ 服务已停止"

# 显示状态
docker-compose ps 2>/dev/null || echo "所有容器已停止"
