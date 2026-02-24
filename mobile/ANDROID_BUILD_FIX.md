# Android 构建错误修复说明

## 问题描述

部署时出现以下错误：

```
AssertionError [ERR_ASSERTION]: Invalid format of Android package name. Only alphanumeric characters, '.' and '_' are allowed, and each '.' must be followed by a letter. Reserved Java keywords are not allowed.
```

## 错误原因

Android 包名必须符合以下规范：
1. 只能包含字母、数字、下划线和点
2. **每个点后面必须跟字母**（不能是数字）
3. 不能使用 Java 保留关键字

之前的配置：
```typescript
"package": `com.qilema.${projectId || 'app'}`
```

当 `projectId` 为纯数字时（如 `123`），生成的包名 `com.qilema.123` 是无效的，因为点后面是数字。

## 解决方案

添加了 `getSafePackageName` 函数来生成安全的包名：

```typescript
const getSafePackageName = (id?: string): string => {
  if (!id) return 'app';
  
  // 如果 ID 是纯数字，添加前缀
  if (/^\d+$/.test(id)) {
    return `app${id}`;
  }
  
  // 确保 ID 以字母开头
  if (/^\d/.test(id)) {
    return `app${id}`;
  }
  
  // 移除非法字符，只保留字母、数字和下划线
  return id.replace(/[^a-zA-Z0-9_]/g, '');
};
```

## 修复效果

### 修复前
```
projectId = "123"  → com.qilema.123 ❌ (无效)
projectId = "abc"  → com.qilema.abc ✅ (有效)
projectId = null   → com.qilema.app  ✅ (有效)
```

### 修复后
```
projectId = "123"  → com.qilema.app123 ✅ (有效)
projectId = "abc"  → com.qilema.abc   ✅ (有效)
projectId = null   → com.qilema.app   ✅ (有效)
```

## 验证结果

使用 `npx expo config --type prebuild` 验证：

```bash
cd /workspace/projects/mobile/client
npx expo config --type prebuild
```

输出显示包名已正确生成：
```json
{
  "android": {
    "package": "com.qilema.app7606380677864620078"
  }
}
```

## 修改文件

- `mobile/client/app.config.ts` - 添加 `getSafePackageName` 函数

## 下一步

### 1. 推送代码到 GitHub

由于环境中的 Git 认证配置问题，需要手动推送：

```bash
cd /workspace/projects

# 使用你的 GitHub token 进行认证
export GITHUB_TOKEN="your_github_token_here"

# 或者配置 SSH 密钥
git remote set-url origin git@github.com:sunnyang1/qilema-app.git

# 推送代码
git push origin main
```

### 2. 在 Coze 平台重新部署

推送完成后：
1. 刷新 Coze 项目页面
2. 清除浏览器缓存
3. 重新触发部署

### 3. 预期结果

Android 构建应该成功通过，不再出现包名格式错误。

## 技术细节

### Android 包名规范

根据 Android 官方文档，包名必须：
- 至少包含两个段（例如 `com.example`）
- 每段只能包含字母、数字和下划线
- 每段必须以字母开头
- 每段不能使用 Java 保留关键字

### 为什么需要这个修复

在 Coze 部署环境中，`projectId` 通常是一个长数字（如 `7606380677864620078`），直接使用会生成无效的包名。通过添加 `getSafePackageName` 函数，确保所有情况都能生成有效的 Android 包名。

## 相关资源

- [Android 应用包名规范](https://developer.android.com/studio/build/application-id)
- [Expo 应用配置](https://docs.expo.dev/versions/latest/config/app/)
- [Coze 部署文档](./DEPLOYMENT.md)
