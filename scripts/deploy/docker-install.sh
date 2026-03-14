#!/bin/bash

# Docker Desktop 安装脚本 for macOS

set -e

echo "🐳 开始安装 Docker Desktop for Mac..."

# 检查是否已安装
if [ -d "/Applications/Docker.app" ]; then
    echo "✅ Docker Desktop 已安装"
    echo "🚀 正在启动 Docker Desktop..."
    open /Applications/Docker.app
    exit 0
fi

# 使用 Homebrew 安装
echo "📦 使用 Homebrew 安装 Docker Desktop..."
echo "⏳ 这可能需要几分钟时间，请耐心等待..."

brew install --cask docker

echo "✅ Docker Desktop 安装完成"
echo "🚀 正在启动 Docker Desktop..."
open /Applications/Docker.app

echo ""
echo "⏳ 等待 Docker 启动..."
sleep 10

# 验证安装
echo ""
echo "🔍 验证 Docker 安装..."
if command -v docker &> /dev/null; then
    echo "✅ Docker 版本: $(docker --version)"
    echo "✅ Docker Compose 版本: $(docker-compose --version)"
    echo ""
    echo "🎉 Docker 安装成功！"
    echo ""
    echo "📋 常用命令:"
    echo "  docker ps          - 查看运行中的容器"
    echo "  docker images      - 查看本地镜像"
    echo "  docker-compose up  - 启动服务"
else
    echo "⚠️ Docker 命令还不可用，请稍等几秒后重试"
    echo "或手动运行: docker --version"
fi
