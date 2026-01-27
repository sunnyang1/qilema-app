#!/bin/bash

echo "=========================================="
echo "   起了吗App - 全量测试脚本"
echo "=========================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

echo "✓ Python版本: $(python3 --version)"
echo ""

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "📥 安装测试依赖..."
pip install -q pytest pytest-asyncio pytest-cov fastapi sqlalchemy pydantic httpx

# 创建测试报告目录
mkdir -p test_reports

echo ""
echo "=========================================="
echo "   开始执行全量测试"
echo "=========================================="
echo ""

# 执行全量测试
pytest tests/ \
    -v \
    --tb=short \
    --disable-warnings \
    --junitxml=test_reports/junit.xml \
    -m "" \
    2>&1 | tee test_reports/test_output.log

# 测试结果处理
EXIT_CODE=${PIPESTATUS[0]}

echo ""
echo "=========================================="
echo "   测试完成"
echo "=========================================="

if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ 所有测试通过!"
else
    echo "❌ 测试失败，退出码: $EXIT_CODE"
fi

echo ""
echo "📊 测试报告位置:"
echo "  - HTML报告: test_reports/report.html"
echo "  - 覆盖率报告: test_reports/coverage/index.html"
echo "  - 完整日志: test_reports/test_output.log"
echo "  - JUnit报告: test_reports/junit.xml"
echo ""

exit $EXIT_CODE
