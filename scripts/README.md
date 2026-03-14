# 运维脚本

## 目录结构

```
scripts/
├── deploy/           # 部署脚本
│   ├── local.sh     # 本地部署
│   └── docker-install.sh  # Docker 安装
├── maintenance/     # 维护脚本
│   └── stop-local.sh      # 停止本地服务
└── README.md        # 本文件
```

## 使用说明

### 部署

```bash
# 本地部署
./scripts/deploy/local.sh

# 安装 Docker
./scripts/deploy/docker-install.sh
```

### 维护

```bash
# 停止本地服务
./scripts/maintenance/stop-local.sh
```

## 注意事项

- 所有脚本需要从项目根目录运行
- 确保脚本有执行权限: `chmod +x scripts/deploy/*.sh`
