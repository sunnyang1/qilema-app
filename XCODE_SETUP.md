# Xcode 配置指南

## ✅ 已完成配置

### 1. Flutter 环境
- Flutter SDK: 3.38.9 ✓
- Dart SDK: 3.10.8 ✓
- iOS 项目已创建 ✓

### 2. 项目依赖
- flutter pub get 已完成 ✓
- share_plus 已添加 ✓

---

## 🔧 需要手动执行的步骤

### 步骤 1: 配置 Xcode 命令行工具

```bash
# 设置 Xcode 路径
sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer

# 验证配置
xcode-select --print-path
# 应输出: /Applications/Xcode.app/Contents/Developer
```

### 步骤 2: 安装 CocoaPods

```bash
# 安装 CocoaPods
sudo gem install cocoapods

# 验证安装
pod --version
```

### 步骤 3: 配置 iOS 项目

```bash
# 进入 iOS 目录
cd /Users/michelleye/CodeBuddy/qilema-app/frontend/ios

# 初始化 Pod（如没有 Podfile）
pod init

# 编辑 Podfile，设置平台版本
# 将 `platform :ios, '12.0'` 改为 `platform :ios, '14.0'`

# 安装依赖
pod install --repo-update
```

### 步骤 4: 接受 Xcode 许可协议

```bash
sudo xcodebuild -license accept
```

### 步骤 5: 验证配置

```bash
flutter doctor
```

预期输出：
```
[✓] Flutter (Channel stable, 3.38.9, ...)
[✓] Android toolchain
[✓] Xcode - develop for iOS and macOS
[✓] Chrome
[✓] Connected device
```

---

## 🚀 运行 iOS 应用

### 方法 1: 使用 Flutter 命令

```bash
cd /Users/michelleye/CodeBuddy/qilema-app/frontend

# 列出可用设备
flutter devices

# 运行 iOS 模拟器
flutter run -d ios
```

### 方法 2: 使用 Xcode

1. 打开 Xcode:
   ```bash
   open ios/Runner.xcworkspace
   ```

2. 选择目标设备（模拟器或真机）

3. 点击运行按钮 (Cmd+R)

---

## 🔧 推荐 Podfile 配置

```ruby
platform :ios, '14.0'

# 禁用 CocoaPods 的静态库警告
install! 'cocoapods', :warn_for_unused_master_specs_repo => false

ENV['COCOAPODS_DISABLE_STATS'] = 'true'

project 'Runner', {
  'Debug' => :debug,
  'Profile' => :release,
  'Release' => :release,
}

def flutter_root
  generated_xcode_build_settings_path = File.expand_path(File.join('..', 'Flutter', 'Generated.xcconfig'), __FILE__)
  unless File.exist?(generated_xcode_build_settings_path)
    raise "#{generated_xcode_build_settings_path} must exist. If you're running pod install manually, make sure flutter pub get is executed first"
  end

  File.foreach(generated_xcode_build_settings_path) do |line|
    matches = line.match(/FLUTTER_ROOT\=(.*)/)
    return matches[1].strip if matches
  end
  raise "Missing FLUTTER_ROOT in #{generated_xcode_build_settings_path}. Try deleting Generated.xcconfig, then run flutter pub get"
end

require File.expand_path(File.join('packages', 'flutter_tools', 'bin', 'podhelper'), flutter_root)

flutter_ios_podfile_setup

target 'Runner' do
  use_frameworks!
  use_modular_headers!

  flutter_install_all_ios_pods File.dirname(File.realpath(__FILE__))
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    flutter_additional_ios_build_settings(target)
    
    # 设置最低 iOS 版本
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '14.0'
    end
  end
end
```

---

## ❗ 常见问题

### 问题 1: "CocoaPods not installed"

**解决**:
```bash
sudo gem install cocoapods
```

### 问题 2: "CommandLineTools is not installed"

**解决**:
```bash
xcode-select --install
```

### 问题 3: "Pod install fails"

**解决**:
```bash
cd ios
rm -rf Pods Podfile.lock
pod repo update
pod install
```

### 问题 4: "iOS deployment target mismatch"

**解决**: 在 Podfile 中设置正确的版本:
```ruby
platform :ios, '14.0'
```

---

## 📱 设备要求

- **iOS 版本**: 最低 iOS 14.0
- **Xcode 版本**: 建议 Xcode 15.0 或更高
- **macOS 版本**: macOS 13.5 或更高

---

## ✅ 验证清单

- [ ] `sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer`
- [ ] `sudo gem install cocoapods`
- [ ] `cd ios && pod install`
- [ ] `sudo xcodebuild -license accept`
- [ ] `flutter doctor` 显示所有检查通过
- [ ] `flutter run -d ios` 成功启动应用
