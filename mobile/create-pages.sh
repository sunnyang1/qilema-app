#!/bin/bash

# 页面列表
declare -A pages
pages=(
    ["health"]="健康档案主页"
    ["history"]="病史页面"
    ["medication"]="药物页面"
    ["allergies"]="过敏史页面"
    ["knowledge-categories"]="知识库分类页面"
    ["knowledge-articles"]="文章列表页面"
    ["knowledge-detail"]="文章详情页面"
    ["medication-reminders"]="用药提醒页面"
    ["medication-add"]="添加药物页面"
    ["devices-list"]="设备列表页面"
    ["devices-data"]="设备数据页面"
    ["hospitals"]="医院列表页面"
    ["aed"]="AED地图页面"
    ["signin-history"]="签到历史页面"
)

# 创建页面基础文件
for key in "${!pages[@]}"; do
    title="${pages[$key]}"
    filename="screens/${key}/index.tsx"
    
    mkdir -p "screens/${key}"
    
    cat > "$filename" << 'EOF'
/**
 * 页面占位符
 * 温暖守护风格 + UI/UX Pro Max 优化
 */
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Screen } from '@/components/Screen';
import { ThemedText } from '@/components/ThemedText';
import { Colors, Spacing, Typography } from '@/constants/theme-warm';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: Spacing.xl,
  },
  title: {
    ...Typography.h1,
    color: Colors.textPrimary,
    marginBottom: Spacing.md,
  },
  subtitle: {
    ...Typography.body,
    color: Colors.textSecondary,
    textAlign: 'center',
  },
});

export default function PlaceholderPage() {
  return (
    <Screen backgroundColor={Colors.backgroundRoot}>
      <View style={styles.container}>
        <ThemedText variant="h1" color={Colors.textPrimary} style={styles.title}>
          页面待实现
        </ThemedText>
        <ThemedText variant="body" color={Colors.textSecondary} style={styles.subtitle}>
          此页面正在开发中...
        </ThemedText>
      </View>
    </Screen>
  );
}
EOF
    
    echo "创建: $filename - $title"
done

echo "所有页面基础文件已创建！"
