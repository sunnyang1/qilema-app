# 开发文档

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/yourorg/qilema-app.git
cd qilema-app

# 启动开发环境
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# 访问 API
http://localhost:8000/docs
```

## 项目结构

```
backend/     # Python FastAPI 后端
mobile/      # React Native 移动端
nginx/       # Nginx 反向代理
scripts/     # 运维脚本
docs/        # 项目文档
```

## 开发指南

### 后端开发

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 移动端开发

```bash
cd mobile
pnpm install
cd client
pnpm dev
```

## 测试

```bash
# 后端测试
cd backend
pytest

# 移动端测试
cd mobile/client
pnpm test
```

## 代码规范

- Python: Black, Flake8, MyPy
- JavaScript/TypeScript: ESLint, Prettier

提交前运行:
```bash
pre-commit run --all-files
```

## 更多信息

- [API 文档](http://localhost:8000/docs)
- [部署文档](../deployment/)
- [CI/CD 文档](../cicd/)
