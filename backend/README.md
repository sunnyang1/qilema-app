# 起了吗App - 后端服务

为独居人群提供紧急医疗救助服务的后端API服务。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- PostgreSQL 12+
- Redis 6+

### 安装依赖
```bash
# 使用 pip
pip install -r requirements.txt

# 或者使用 poetry
pip install poetry
poetry install
```

### 环境配置
1. 复制环境变量文件：
```bash
cp .env.example .env
```

2. 配置环境变量：
```env
# 安全配置
SECRET_KEY=your-secret-key-here

# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/qilema_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 应用配置
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

3. 生成安全密钥：
```bash
python scripts/generate_secret_key.py
```

### 运行应用
```bash
# 开发模式
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

## 📁 项目结构

```
backend/
├── app/                 # 应用代码
│   ├── api/            # API路由
│   ├── core/           # 核心配置和工具
│   ├── models/         # 数据库模型
│   ├── schemas/        # Pydantic模型
│   └── services/       # 业务逻辑服务
├── tests/              # 测试代码
├── migrations/         # 数据库迁移
├── scripts/            # 工具脚本
├── main.py            # 应用入口
├── requirements.txt   # 依赖列表
└── pyproject.toml     # 现代Python配置
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 运行测试并生成覆盖率报告
pytest --cov=app

# 运行集成测试
pytest -m integration
```

## 🔧 开发工具

### 代码格式化
```bash
# 格式化代码
black app/ tests/

# 排序导入
isort app/ tests/

# 检查代码质量
flake8 app/ tests/

# 类型检查
mypy app/
```

### 预提交钩子
```bash
# 安装预提交钩子
pre-commit install

# 手动运行所有钩子
pre-commit run --all-files
```

## 📚 API文档

启动应用后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🚢 部署

### Docker部署
```bash
# 构建镜像
docker build -t qilema-app .

# 运行容器
docker run -p 8000:8000 qilema-app
```

### 使用docker-compose
```bash
docker-compose up -d
```

## 🔒 安全特性

- JWT认证
- 密码哈希（bcrypt）
- CORS配置
- 请求ID追踪
- 结构化日志
- 输入验证
- SQL注入防护

## 📈 监控和日志

应用提供以下端点：
- `/health` - 健康检查
- `/metrics` - 性能指标

日志配置：
- 结构化JSON日志
- 文件轮转
- 多级别日志

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 📞 支持

如有问题请联系：dev@qilema.com
