# 起了吗 App - 部署文档

## 1. 环境要求

### 1.1 服务器要求

| 组件 | 最低配置 | 推荐配置 |
|-----|---------|---------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 存储 | 20GB SSD | 50GB SSD+ |
| 带宽 | 5Mbps | 10Mbps+ |

### 1.2 软件要求

- **操作系统**：Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **Docker**：20.10+
- **Docker Compose**：2.0+
- **Python**：3.11+（非Docker部署）
- **PostgreSQL**：15+（非Docker部署）
- **Redis**：7+（非Docker部署）

---

## 2. Docker部署（推荐）

### 2.1 快速启动

```bash
# 1. 克隆项目
git clone https://github.com/your-org/qilema-app.git
cd qilema-app

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库、JWT密钥等

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 停止服务
docker-compose down
```

### 2.2 服务说明

| 服务 | 端口 | 说明 |
|-----|------|------|
| backend | 8000 | FastAPI后端服务 |
| postgres | 5432 | PostgreSQL数据库 |
| redis | 6379 | Redis缓存服务 |

---

## 3. 手动部署

### 3.1 安装依赖

```bash
# 安装Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv

# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 安装Redis
sudo apt install redis-server
```

### 3.2 配置数据库

```bash
# 创建数据库和用户
sudo -u postgres psql

CREATE DATABASE qilema;
CREATE USER qilema_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE qilema TO qilema_user;
\q
```

### 3.3 部署后端

```bash
cd /opt/qilema-app/backend

# 创建虚拟环境
python3.11 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
export DATABASE_URL=postgresql://qilema_user:your_password@localhost:5432/qilema
export REDIS_URL=redis://localhost:6379/0
export SECRET_KEY=your-secret-key
export ENCRYPTION_KEY=your-fernet-key

# 初始化数据库
python -c "from app.core.database import init_db; init_db()"

# 启动服务
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3.4 使用Systemd管理

创建服务文件 `/etc/systemd/system/qilema.service`：

```ini
[Unit]
Description=Qilema App Backend
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=qilema
WorkingDirectory=/opt/qilema-app/backend
Environment=DATABASE_URL=postgresql://qilema_user:your_password@localhost:5432/qilema
Environment=REDIS_URL=redis://localhost:6379/0
Environment=SECRET_KEY=your-secret-key
Environment=ENCRYPTION_KEY=your-fernet-key
ExecStart=/opt/qilema-app/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable qilema
sudo systemctl start qilema
sudo systemctl status qilema
```

---

## 4. Nginx反向代理

### 4.1 安装Nginx

```bash
sudo apt install nginx
```

### 4.2 配置Nginx

创建配置文件 `/etc/nginx/sites-available/qilema`：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/qilema /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 5. SSL证书配置（HTTPS）

### 5.1 使用Certbot

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo systemctl enable certbot.timer
```

### 5.2 手动配置

编辑Nginx配置文件添加SSL：

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 6. 监控与日志

### 6.1 日志配置

应用日志位于：
- 应用日志：`/opt/qilema-app/logs/`
- Nginx日志：`/var/log/nginx/`

### 6.2 使用Prometheus监控

安装Node Exporter和配置Prometheus抓取应用指标。

---

## 7. 备份策略

### 7.1 数据库备份

```bash
# 创建备份脚本
#!/bin/bash
BACKUP_DIR=/opt/backups/qilema
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
pg_dump qilema > $BACKUP_DIR/qilema_$DATE.sql

# 保留最近30天的备份
find $BACKUP_DIR -name "qilema_*.sql" -mtime +30 -delete
```

添加到Crontab：

```bash
# 每天凌晨2点备份
0 2 * * * /opt/qilema-app/scripts/backup.sh
```

### 7.2 Redis备份

Redis默认开启RDB持久化，确保配置文件中已启用：

```conf
save 900 1
save 300 10
save 60 10000
```

---

## 8. 故障排查

### 8.1 服务无法启动

```bash
# 检查日志
sudo journalctl -u qilema -f

# 检查端口占用
sudo netstat -tlnp | grep 8000

# 检查依赖
python -c "import app.main"
```

### 8.2 数据库连接失败

```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 检查连接
psql -U qilema_user -d qilema -h localhost

# 检查防火墙
sudo ufw status
```

### 8.3 Redis连接失败

```bash
# 检查Redis状态
sudo systemctl status redis

# 测试连接
redis-cli ping
```

---

## 9. 更新部署

### 9.1 代码更新

```bash
cd /opt/qilema-app

# 拉取最新代码
git pull origin main

# 更新依赖
source backend/venv/bin/activate
pip install -r backend/requirements.txt

# 重启服务
sudo systemctl restart qilema
```

### 9.2 数据库迁移

```bash
cd /opt/qilema-app/backend
python -c "from app.core.database import init_db; init_db()"
```

---

## 10. 安全建议

1. **修改默认密码**：确保所有默认密码已修改
2. **配置防火墙**：仅开放必要的端口（80, 443, 22）
3. **定期更新**：及时更新系统和依赖的安全补丁
4. **启用日志**：确保所有关键操作都有日志记录
5. **HTTPS强制**：生产环境必须使用HTTPS
6. **密钥管理**：使用环境变量或密钥管理服务管理敏感信息
