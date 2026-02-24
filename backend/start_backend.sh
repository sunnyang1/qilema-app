#!/bin/bash

# 后端服务启动脚本
# 用于启动 FastAPI 后端服务

echo "=========================================="
echo "后端服务启动脚本"
echo "=========================================="
echo "工作目录: /workspace/projects/backend"
echo "端口: 8000"
echo "日志文件: /tmp/backend.log"
echo ""

# 停止旧的服务
echo "停止旧的服务..."
pkill -f "python.*uvicorn" || true
pkill -f "python.*start_server" || true
sleep 2

# 检查端口是否被占用
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️ 端口 8000 仍被占用，强制终止..."
    lsof -ti :8000 | xargs kill -9 2>/dev/null || true
    sleep 1
fi

# 进入工作目录
cd /workspace/projects/backend

# 启动服务
echo "启动后端服务..."
nohup python3 start_server.py > /tmp/backend.log 2>&1 &
PID=$!

echo "服务进程 ID: $PID"
echo ""

# 等待服务启动
echo "等待服务启动（5秒）..."
sleep 5

# 检查进程状态
if ps -p $PID > /dev/null 2>&1; then
    echo "✅ 服务进程运行中 (PID: $PID)"
else
    echo "❌ 服务进程未运行，请检查日志"
    echo "日志文件: /tmp/backend.log"
    tail -50 /tmp/backend.log
    exit 1
fi

# 测试健康检查
echo ""
echo "测试健康检查..."
HEALTH_RESPONSE=$(curl -s http://localhost:8000/api/v1/health 2>&1)

if echo "$HEALTH_RESPONSE" | grep -q "code.*200"; then
    echo "✅ 服务健康检查通过"
    echo "响应: $HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"
else
    echo "❌ 服务健康检查失败"
    echo "响应: $HEALTH_RESPONSE"
    echo ""
    echo "查看最后 50 行日志:"
    tail -50 /tmp/backend.log
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 后端服务启动成功"
echo "=========================================="
echo ""
echo "服务地址: http://localhost:8000"
echo "健康检查: http://localhost:8000/api/v1/health"
echo "日志文件: /tmp/backend.log"
echo ""
echo "下一步: 执行测试脚本"
echo "  cd /workspace/projects/backend"
echo "  chmod +x test_api.sh"
echo "  ./test_api.sh"
echo ""
