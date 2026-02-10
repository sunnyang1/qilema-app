#!/bin/bash

# Xcode 配置脚本

echo "🔧 开始配置 Xcode..."

# 1. 切换 Xcode 路径
echo "1. 设置 Xcode 路径..."
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# 2. 安装 CocoaPods
echo "2. 安装 CocoaPods..."
sudo gem install cocoapods

# 3. 安装 iOS 依赖
echo "3. 安装 iOS Pod 依赖..."
cd /Users/michelleye/CodeBuddy/qilema-app/frontend/ios
pod install --repo-update

# 4. 接受许可协议
echo "4. 接受 Xcode 许可协议..."
sudo xcodebuild -license accept

echo "✅ Xcode 配置完成！"
echo ""
echo "运行 flutter doctor 验证配置："
flutter doctor
