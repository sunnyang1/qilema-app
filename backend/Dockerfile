# 起了吗 App - 后端Docker镜像（优化版）

# ============ 构建阶段 ============
FROM python:3.12-slim as builder

WORKDIR /build

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    find /opt/venv -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/venv -type f -name '*.pyc' -delete && \
    find /opt/venv -type f -name '*.pyo' -delete

# ============ 运行阶段 ============
FROM python:3.12-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    tini \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean && apt-get autoclean

# 设置Python环境变量
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/opt/venv/bin:$PATH"

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv

# 创建非root用户（更小的UID避免冲突）
RUN groupadd -r -g 1001 appuser && useradd -r -u 1001 -g appuser appuser

# 创建日志目录
RUN mkdir -p /app/logs && chown -R appuser:appuser /app && chmod 755 /app/logs

# 复制应用代码
COPY --chown=appuser:appuser . .

# 删除不必要的文件
RUN rm -rf tests/ docs/ .git .github .gitignore *.md .env* .flake8 .pre-commit-config.yaml \
    && find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true \
    && find . -type f -name '*.pyc' -delete

# 切换到非root用户
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 使用 tini 作为 PID 1，处理信号转发
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--access-log"]
