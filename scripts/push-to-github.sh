#!/bin/bash

# Coze 部署修复推送脚本
# 用于推送代码到 GitHub 远程仓库

set -e

echo "========================================="
echo "   Coze 部署修复 - 代码推送脚本"
echo "========================================="
echo ""

# 检查当前目录
if [ ! -f "package.json" ]; then
    echo "❌ 错误：必须在项目根目录运行此脚本"
    echo "   当前目录: $(pwd)"
    exit 1
fi

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    echo "⚠️  检测到未提交的更改"
    echo ""
    git status --short
    echo ""
    read -p "是否先提交这些更改? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📝 提交更改..."
        git add .
        git commit -m "chore: 部署前的最终调整"
    else
        echo "❌ 取消推送"
        exit 1
    fi
fi

# 检查远程仓库
echo "📋 检查远程仓库..."
git remote -v
echo ""

# 检查待推送的提交
AHEAD=$(git rev-list --count @{u}..HEAD 2>/dev/null || echo "0")
if [ "$AHEAD" -eq "0" ]; then
    echo "✅ 没有需要推送的提交"
    echo "   本地与远程已同步"
    exit 0
fi

echo "📤 发现 $AHEAD 个待推送的提交"
echo ""
git log @{u}..HEAD --oneline 2>/dev/null || git log --oneline -5
echo ""

# 尝试推送
echo "🚀 开始推送到远程仓库..."
echo ""

# 尝试使用不同的方法推送

# 方法 1: 直接推送
if git push origin main 2>/dev/null; then
    echo ""
    echo "✅ 推送成功！"
    echo ""
    echo "下一步："
    echo "1. 刷新 Coze 项目页面"
    echo "2. 清除浏览器缓存"
    echo "3. 重新触发部署"
    exit 0
fi

# 方法 1 失败，提示用户手动操作
echo "❌ 推送失败，需要手动认证"
echo ""
echo "请选择以下方式之一："
echo ""
echo "方式 1: 使用 GitHub CLI (推荐)"
echo "--------------------------------"
echo "  gh auth login"
echo "  git push origin main"
echo ""
echo "方式 2: 使用 Personal Access Token"
echo "--------------------------------"
echo "  1. 访问: https://github.com/settings/tokens"
echo "  2. 创建 token 并复制"
echo "  3. 运行: git remote set-url origin https://<TOKEN>@github.com/sunnyang1/qilema-app.git"
echo "  4. 运行: git push origin main"
echo ""
echo "方式 3: 使用 SSH 密钥"
echo "--------------------------------"
echo "  1. 生成 SSH 密钥: ssh-keygen -t ed25519 -C \"your_email@example.com\""
echo "  2. 添加到 GitHub: https://github.com/settings/keys"
echo "  3. 运行: git remote set-url origin git@github.com:sunnyang1/qilema-app.git"
echo "  4. 运行: git push origin main"
echo ""

# 提供临时配置建议
read -p "是否尝试配置并推送? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "请输入你的 GitHub Personal Access Token:"
    echo "(输入将被隐藏，创建 token: https://github.com/settings/tokens)"
    read -s TOKEN

    if [ -n "$TOKEN" ]; then
        echo ""
        echo "🔧 配置远程仓库..."
        git remote set-url origin "https://$TOKEN@github.com/sunnyang1/qilema-app.git"

        echo "🚀 推送代码..."
        if git push origin main; then
            echo ""
            echo "✅ 推送成功！"
            echo ""
            echo "下一步："
            echo "1. 刷新 Coze 项目页面"
            echo "2. 清除浏览器缓存"
            echo "3. 重新触发部署"

            # 恢复原始 URL（出于安全考虑）
            git remote set-url origin "https://github.com/sunnyang1/qilema-app.git"
            exit 0
        else
            echo "❌ 推送仍然失败"
        fi
    fi
fi

echo ""
echo "========================================="
echo "   需要手动完成推送操作"
echo "========================================="
echo ""
echo "详细说明请查看: DEPLOYMENT_FIX_SUMMARY.md"
echo ""
