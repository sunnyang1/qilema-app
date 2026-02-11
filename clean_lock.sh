#!/bin/bash

echo "🔓 释放 Flutter 启动锁定..."

# 1. 终止所有 Flutter/Dart 进程
echo "1. 终止 Flutter 进程..."
pkill -f "flutter_tools.snapshot" 2>/dev/null
pkill -f "dart" 2>/dev/null
pkill -f "flutter" 2>/dev/null

# 2. 清理锁定文件
echo "2. 清理锁定文件..."
cd /Users/michelleye/CodeBuddy/qilema-app/frontend

# 删除 Flutter 相关的临时文件和锁定文件
rm -f .flutter-plugins 2>/dev/null
rm -f .flutter-plugins-dependencies 2>/dev/null
rm -f .packages 2>/dev/null
rm -rf .dart_tool 2>/dev/null

# 3. 清理构建缓存
echo "3. 清理构建缓存..."
rm -rf build/ 2>/dev/null
rm -rf ios/Pods/ 2>/dev/null
rm -f ios/Podfile.lock 2>/dev/null

# 4. 等待进程完全终止
sleep 2

# 5. 验证
echo "4. 验证清理结果..."
REMAINING=$(ps aux | grep -E "flutter|dart" | grep -v grep | wc -l)

if [ "$REMAINING" -eq 0 ]; then
    echo "✅ 启动锁定已释放！"
    echo ""
    echo "现在可以重新运行:"
    echo "  flutter clean"
    echo "  flutter pub get"
    echo "  flutter run"
else
    echo "⚠️  还有 $REMAINING 个进程在运行"
    echo "请手动终止: kill -9 <PID>"
fi
