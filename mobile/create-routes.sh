#!/bin/bash

# 创建路由文件
routes=(
    "health:健康档案"
    "history:病史"
    "medication:药物"
    "allergies:过敏史"
    "knowledge/categories:知识库分类"
    "knowledge/articles:文章列表"
    "knowledge/article-detail:文章详情"
    "medication/reminders:用药提醒"
    "medication/add:添加药物"
    "devices/list:设备列表"
    "devices/data:设备数据"
    "emergency/hospitals:医院列表"
    "emergency/aed:AED地图"
    "signin/history:签到历史"
)

for route in "${routes[@]}"; do
    path="${route%%:*}"
    title="${route##*:}"
    
    # 将 path 转换为文件路径
    filepath="app/${path}.tsx"
    
    # 将 path 转换为 screen 路径
    screenpath="screens/${path//\//-}"
    
    mkdir -p "app/$(dirname "$path")"
    
    cat > "$filepath" << EOF
export { default } from "@/screens/${screenpath}";
EOF
    
    echo "创建路由: $filepath - $title"
done

echo "所有路由文件已创建！"
