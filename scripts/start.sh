#!/bin/bash
# Coze 部署启动脚本

set -e

# 检查 Node.js 版本
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed"
    exit 1
fi

echo "Starting Qilema App..."

# 设置环境变量
export NODE_ENV=production
export PORT=${PORT:-5000}

# 进入 server 目录
cd mobile/server

# 启动服务
if [ -f "dist/index.js" ]; then
    echo "Starting server from dist/index.js..."
    exec node dist/index.js
else
    echo "Error: dist/index.js not found. Please run build first."
    exit 1
fi
