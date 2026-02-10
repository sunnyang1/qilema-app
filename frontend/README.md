# 起了吗 App - 前端

Flutter前端应用，为独居人群提供紧急医疗服务。

## 开发环境

- Flutter SDK: 3.16+
- Dart SDK: 3.2+

## 快速开始

```bash
# 安装依赖
flutter pub get

# 运行调试
flutter run

# 构建Android
flutter build apk --release

# 构建iOS
flutter build ios --release
```

## 项目结构

```
lib/
├── main.dart              # 应用入口
├── core/                  # 核心模块
│   ├── constants/         # 常量定义
│   ├── theme/            # 主题配置
│   ├── utils/            # 工具函数
│   └── network/          # 网络层
├── features/             # 功能模块
│   ├── auth/             # 认证模块
│   ├── signin/           # 签到模块
│   ├── sos/              # SOS模块
│   ├── contacts/         # 联系人模块
│   ├── health/           # 健康档案模块
│   └── devices/          # 设备模块
├── shared/               # 共享组件
│   ├── widgets/          # 通用组件
│   └── models/           # 共享模型
└── l10n/                 # 国际化
```

## 开发中

前端界面正在开发中，目前为占位状态。
