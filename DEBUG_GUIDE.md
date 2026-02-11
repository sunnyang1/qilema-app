# 项目调试和构建指南

## 📦 依赖更新

### 1. 获取最新依赖

```bash
cd /Users/michelleye/CodeBuddy/qilema-app/frontend

# 获取依赖
flutter pub get

# 检查过时的依赖
flutter pub outdated

# 升级所有依赖到最新兼容版本
flutter pub upgrade
```

### 2. 已更新的依赖版本

| 包名 | 旧版本 | 新版本 |
|------|--------|--------|
| dio | ^5.4.0 | ^5.8.0 |
| go_router | ^17.1.0 | ^14.8.1 |
| url_launcher | ^6.2.0 | ^6.3.1 |
| shared_preferences | ^2.2.0 | ^2.5.2 |
| permission_handler | ^12.0.1 | ^11.4.0 |
| geolocator | ^14.0.2 | ^13.0.2 |
| flutter_local_notifications | ^20.0.0 | ^19.1.0 |
| intl | ^0.20.2 | ^0.19.0 |
| cupertino_icons | ^1.0.6 | ^1.0.8 |
| flutter_screenutil | ^5.9.0 | ^5.9.3 |
| fl_chart | ^1.1.1 | ^0.70.2 |
| flutter_blue_plus | ^2.1.0 | ^1.35.3 |
| share_plus | ^10.0.0 | ^10.1.4 |

---

## 🔧 平台配置

### Android 配置

已创建/更新以下文件：
- `android/app/src/main/AndroidManifest.xml` - 添加所有必要权限
- `android/build.gradle` - 项目级构建配置
- `android/settings.gradle` - 插件管理配置
- `android/app/build.gradle` - 应用级构建配置

**Android 权限：**
- 网络和位置权限
- 蓝牙权限（扫描、连接、广播）
- 电话和通知权限
- 闹钟和唤醒权限

### iOS 配置

已更新 `ios/Runner/Info.plist`：
- 位置权限（使用时和始终）
- 蓝牙权限
- 后台模式（fetch, location, bluetooth-central）
- 相机和麦克风权限

---

## 🐛 调试步骤

### 步骤 1: 清理项目

```bash
# 清理 Flutter 构建缓存
flutter clean

# 获取依赖
flutter pub get
```

### 步骤 2: 检查代码问题

```bash
# 分析代码
flutter analyze

# 格式化代码
flutter format lib/
```

### 步骤 3: 验证环境

```bash
# 检查 Flutter 环境
flutter doctor

# 检查设备
flutter devices
```

---

## 📱 运行应用

### Android

```bash
# 连接设备或启动模拟器后
flutter run -d android

# 或者指定设备 ID
flutter run -d <device-id>
```

### iOS

```bash
# 确保已配置 Xcode
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# 安装 iOS 依赖
cd ios
pod install
cd ..

# 运行 iOS 应用
flutter run -d ios
```

### Web

```bash
flutter run -d chrome
```

---

## 🔍 常见问题解决

### 问题 1: 依赖冲突

**症状**: `flutter pub get` 失败

**解决**:
```bash
# 删除锁定文件
rm pubspec.lock

# 重新获取依赖
flutter pub get
```

### 问题 2: Android 构建失败

**症状**: Gradle 构建错误

**解决**:
```bash
cd android
./gradlew clean
./gradlew build
cd ..
flutter clean
flutter pub get
```

### 问题 3: iOS 构建失败

**症状**: CocoaPods 错误

**解决**:
```bash
cd ios
rm -rf Pods Podfile.lock
pod repo update
pod install
cd ..
```

### 问题 4: 权限问题

**症状**: 位置或蓝牙功能不工作

**解决**:
- Android: 检查 `AndroidManifest.xml` 中的权限
- iOS: 检查 `Info.plist` 中的权限描述

### 问题 5: 热重载不工作

**解决**:
```bash
# 停止应用后重新运行
flutter clean
flutter pub get
flutter run
```

---

## 📊 构建发布版本

### Android APK

```bash
flutter build apk --release

# 或构建 App Bundle
flutter build appbundle --release
```

### iOS

```bash
flutter build ios --release
```

---

## ✅ 验证清单

- [ ] `flutter pub get` 成功
- [ ] `flutter analyze` 无错误
- [ ] `flutter doctor` 所有检查通过
- [ ] Android 应用能正常编译和运行
- [ ] iOS 应用能正常编译和运行
- [ ] 所有主要功能测试通过

---

## 🔗 相关文档

- [Xcode 配置指南](XCODE_SETUP.md)
- [Android 配置指南](ANDROID_SETUP.md)
- [Flutter 官方文档](https://docs.flutter.dev/)
