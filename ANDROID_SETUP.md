# Android 配置指南

## ✅ 已完成配置

### 1. 环境变量
已添加到 `~/.zshrc`:
```bash
# Android SDK 配置
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$ANDROID_HOME/cmdline-tools/9.0/bin:$PATH"
export PATH="$ANDROID_HOME/platform-tools:$PATH"
export PATH="$ANDROID_HOME/build-tools:$PATH"
```

### 2. 已安装组件
- Android SDK: ~/Library/Android/sdk ✓
- Android API 34 (android-34) ✓
- Android API 36 (android-36) ✓
- Platform Tools ✓
- Build Tools ✓
- Java 17 (OpenJDK) ✓

---

## 🔧 需要执行的步骤

### 步骤 1: 应用环境变量

```bash
source ~/.zshrc
```

### 步骤 2: 创建 Android 项目

```bash
cd /Users/michelleye/CodeBuddy/qilema-app/frontend
flutter create --platforms=android --org=com.qilema .
```

### 步骤 3: 获取依赖

```bash
flutter pub get
```

### 步骤 4: 验证配置

```bash
flutter doctor
```

预期输出：
```
[✓] Flutter (Channel stable, 3.38.9, ...)
[✓] Android toolchain - develop for Android devices (Android SDK version 36.0.0)
[✓] Java binary at: /opt/homebrew/opt/openjdk@17/bin/java
```

---

## 🚀 运行 Android 应用

### 方法 1: 使用 Flutter 命令

```bash
cd /Users/michelleye/CodeBuddy/qilema-app/frontend

# 列出可用设备
flutter devices

# 运行 Android 应用
flutter run -d android
```

### 方法 2: 使用 Android Studio

1. 打开 Android Studio
2. 选择 "Open an Existing Project"
3. 选择 `frontend/android` 文件夹
4. 点击运行按钮

---

## 📱 配置 Android 模拟器

### 创建模拟器

```bash
# 列出可用系统镜像
sdkmanager --list | grep system-images

# 创建 AVD（Android Virtual Device）
avdmanager create avd -n Pixel_7 -k "system-images;android-34;google_apis_playstore;arm64-v8a" -d pixel_7

# 启动模拟器
emulator -avd Pixel_7
```

### 使用 Android Studio 创建

1. 打开 Android Studio
2. Tools > Device Manager
3. 点击 "Create Device"
4. 选择设备定义和系统镜像

---

## 🔧 推荐配置

### android/app/build.gradle

```gradle
plugins {
    id "com.android.application"
    id "kotlin-android"
    id "dev.flutter.flutter-gradle-plugin"
}

def localProperties = new Properties()
def localPropertiesFile = rootProject.file('local.properties')
if (localPropertiesFile.exists()) {
    localPropertiesFile.withReader('UTF-8') { reader ->
        localProperties.load(reader)
    }
}

def flutterVersionCode = localProperties.getProperty('flutter.versionCode')
if (flutterVersionCode == null) {
    flutterVersionCode = '1'
}

def flutterVersionName = localProperties.getProperty('flutter.versionName')
if (flutterVersionName == null) {
    flutterVersionName = '1.0'
}

android {
    namespace "com.qilema.qilema_app"
    compileSdkVersion flutter.compileSdkVersion
    ndkVersion flutter.ndkVersion

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = '17'
    }

    sourceSets {
        main.java.srcDirs += 'src/main/kotlin'
    }

    defaultConfig {
        applicationId "com.qilema.qilema_app"
        minSdkVersion 21
        targetSdkVersion flutter.targetSdkVersion
        versionCode flutterVersionCode.toInteger()
        versionName flutterVersionName
    }

    buildTypes {
        release {
            signingConfig signingConfigs.debug
        }
    }
}

flutter {
    source '../..'
}

dependencies {}
```

### android/build.gradle

```gradle
allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.buildDir = '../build'

subprojects {
    project.buildDir = "${rootProject.buildDir}/${project.name}"
}

subprojects {
    project.evaluationDependsOn(':app')
}

tasks.register("clean", Delete) {
    delete rootProject.buildDir
}
```

### android/settings.gradle

```gradle
pluginManagement {
    def flutterSdkPath = {
        def properties = new Properties()
        file("local.properties").withInputStream { properties.load(it) }
        def flutterSdkPath = properties.getProperty("flutter.sdk")
        assert flutterSdkPath != null, "flutter.sdk not set in local.properties"
        return flutterSdkPath
    }()

    includeBuild("$flutterSdkPath/packages/flutter_tools/gradle")

    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

plugins {
    id "dev.flutter.flutter-plugin-loader" version "1.0.0"
    id "com.android.application" version "8.1.0" apply false
    id "org.jetbrains.kotlin.android" version "1.8.10" apply false
}

include ":app"
```

---

## ❗ 常见问题

### 问题 1: "ANDROID_HOME not set"

**解决**:
```bash
echo 'export ANDROID_HOME="$HOME/Library/Android/sdk"' >> ~/.zshrc
source ~/.zshrc
```

### 问题 2: "Java version mismatch"

**解决**:
```bash
# 检查 Java 版本
java -version

# 设置 JAVA_HOME
export JAVA_HOME="/opt/homebrew/opt/openjdk@17"
```

### 问题 3: "Gradle build failed"

**解决**:
```bash
cd android
./gradlew clean
./gradlew build
```

### 问题 4: "SDK license not accepted"

**解决**:
```bash
yes | sdkmanager --licenses
```

---

## ✅ 验证清单

- [ ] `source ~/.zshrc` 应用环境变量
- [ ] `flutter create --platforms=android --org=com.qilema .` 创建项目
- [ ] `flutter pub get` 获取依赖
- [ ] `flutter doctor` 显示所有检查通过
- [ ] `flutter run -d android` 成功启动应用
