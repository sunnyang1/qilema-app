# Server Setup Guide

This guide walks you through setting up staging and production servers for deployment.

## Prerequisites

- Access to a Linux server (Ubuntu 20.04+ or CentOS 8+)
- Administrator/sudo privileges
- Domain name or static IP address

## 🔧 Quick Setup (Complete Server from Scratch)

### 1. SSH Setup

```bash
# On your local machine
# Generate deployment SSH key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/qilema_deploy -C "qilema-deploy@github"

# Copy public key
cat ~/.ssh/qilema_deploy.pub
```

### 2. Server Initial Setup

```bash
# SSH into your server
ssh root@your-server-ip

# Update system
apt update && apt upgrade -y

# Create deploy user
useradd -m -s /bin/bash deploy
usermod -aG sudo deploy
usermod -aG docker deploy

# Set up SSH access for deploy user
mkdir -p /home/deploy/.ssh
chmod 700 /home/deploy/.ssh

# Add your public key
echo "your-public-key-content" > /home/deploy/.ssh/authorized_keys
chmod 600 /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh

# Switch to deploy user
su - deploy
```

### 3. Install Docker

```bash
# Run as deploy user
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Verify Docker
docker run hello-world
```

### 4. Create Application Directory

```bash
# As deploy user
sudo mkdir -p /var/www/qilema
sudo chown deploy:deploy /var/www/qilema
cd /var/www/qilema

# Clone repository
git clone https://github.com/yourorg/qilema-app.git .

# Create environment file (edit with your values)
cp .env.example .env.staging  # or .env.prod
nano .env.staging
```

### 5. Create Backup Directory

```bash
# As deploy user
sudo mkdir -p /backups
sudo chown deploy:deploy /backups
chmod 700 /backups

# Create backup subdirectories
mkdir -p /backups/pre-deploy
mkdir -p /backups/post-deploy
```

### 6. Start Services

```bash
cd /var/www/qilema

# For staging
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Or for production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Verify services
docker-compose ps
```

---

## 📋 Detailed Setup Steps

### Step 1: SSH Key Setup

#### On Your Local Machine

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096 -f ~/.ssh/qilema_staging -N "" -C "qilema-staging"

# Get the public key
cat ~/.ssh/qilema_staging.pub
# Output: ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB... qilema-staging
```

#### On the Server

```bash
# Add public key
echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQAB... qilema-staging" >> ~/.ssh/authorized_keys

# Secure permissions
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

#### Verify Connection

```bash
# From your local machine
ssh -i ~/.ssh/qilema_staging deploy@your-server-ip "whoami"
# Should output: deploy
```

### Step 2: Docker Installation

#### Ubuntu/Debian

```bash
# Install dependencies
sudo apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Install Docker Compose standalone
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker --version
docker-compose --version
```

#### CentOS/RHEL

```bash
# Install Docker
sudo yum install -y yum-utils
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo yum install -y docker-ce docker-ce-cli containerd.io

# Start Docker
sudo systemctl start docker
sudo systemctl enable docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Add User to Docker Group

```bash
# Add deploy user to docker group
sudo usermod -aG docker deploy

# Apply group changes (choose one)
newgrp docker              # Temporary
su - deploy                # New login session

# Verify
docker ps
```

### Step 3: Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/qilema
sudo chown deploy:deploy /var/www/qilema
cd /var/www/qilema

# Initialize git repository
git init
git remote add origin https://github.com/yourorg/qilema-app.git
git fetch origin main
git checkout -b main origin/main

# Create environment file
cp .env.example .env.staging
nano .env.staging  # Edit with production values

# Secure environment file
chmod 600 .env.staging
```

### Step 4: Create Backup Structure

```bash
# Create backup directories
sudo mkdir -p /backups/pre-deploy
sudo mkdir -p /backups/post-deploy
sudo mkdir -p /backups/daily
sudo mkdir -p /backups/weekly
sudo mkdir -p /backups/monthly

# Set permissions
sudo chown -R deploy:deploy /backups
chmod 700 /backups

# Create backup script
cat > ~/backup.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/backups/daily/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

cd /var/www/qilema

# Backup database
docker-compose exec -T postgres pg_dump -U qilema qilema_prod | gzip > $BACKUP_DIR/database.sql.gz

# Backup volumes
docker run --rm -v qilema_prod_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/postgres-volume.tar.gz -C /data .

echo "✓ Backup created: $BACKUP_DIR"
EOF

chmod +x ~/backup.sh
```

### Step 5: Start Services

```bash
cd /var/www/qilema

# Pull latest images
docker-compose -f docker-compose.yml -f docker-compose.staging.yml pull

# Start services
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Wait for startup
sleep 10

# Check status
docker-compose ps
docker-compose logs backend | head -20

# Test API
curl http://localhost:8000/health
```

---

## 🔒 Security Hardening

### Firewall Configuration

```bash
# Install UFW
sudo apt-get install -y ufw

# Enable firewall
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Docker (internal only)
sudo ufw allow from 172.17.0.0/16

# Check rules
sudo ufw status verbose
```

### SSL/TLS Certificates

```bash
# Install Certbot
sudo apt-get install -y certbot python3-certbot-nginx

# Get certificate (for your domain)
sudo certbot certonly --standalone \
  -d staging.api.qilema.com \
  -d staging.qilema.com

# Certificates location: /etc/letsencrypt/live/staging.api.qilema.com/

# Auto-renewal
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

### Update Unattended

```bash
# Install unattended-upgrades
sudo apt-get install -y unattended-upgrades

# Enable automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades
```

### Monitor Logs

```bash
# View Docker logs
docker-compose logs -f backend

# View system logs
sudo journalctl -u docker -f

# View nginx logs
docker-compose logs -f nginx
```

---

## 📊 Monitoring & Maintenance

### Daily Maintenance Checklist

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check running containers
docker ps

# View logs for errors
docker-compose logs backend | grep -i error

# Check backups exist
ls -lh /backups/pre-deploy/ | tail -5
```

### Weekly Tasks

```bash
# Update Docker images
docker-compose pull

# Remove old images
docker image prune -a --filter "until=336h"

# Check certificate expiry
sudo certbot certificates

# Verify backups
ls -lh /backups/daily/ | wc -l
```

### Monthly Tasks

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Audit Docker security
docker run --rm --net host aquasec/trivy image -s HIGH,CRITICAL

# Rotate SSH keys (quarterly)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/qilema_staging_new

# Archive old backups
cd /backups && tar czf archive_$(date +%Y%m).tar.gz daily/
```

---

## 🚨 Troubleshooting

### Cannot Connect via SSH

```bash
# Check SSH key permissions
ls -la ~/.ssh/qilema_staging
# Should be: -rw------- (600)

# Check server authorized_keys
ssh -v deploy@server  # Shows detailed connection info

# Fix permissions if wrong
chmod 600 ~/.ssh/qilema_staging
chmod 700 ~/.ssh

# Try with verbose output
ssh -i ~/.ssh/qilema_staging -vvv deploy@server
```

### Docker Commands Fail with Permission Denied

```bash
# Check if user is in docker group
groups deploy
# Should include 'docker'

# Add user to docker group
sudo usermod -aG docker deploy

# Log out and log back in for group changes to take effect
exit  # or
su - deploy
```

### Services Won't Start

```bash
# Check logs
docker-compose logs

# Check port conflicts
sudo lsof -i :8000
sudo lsof -i :5432
sudo lsof -i :6379

# Check disk space
df -h

# Check memory
free -h

# Restart Docker daemon
sudo systemctl restart docker
```

### Database Connection Issues

```bash
# Test database connectivity
docker-compose exec postgres pg_isready

# Check database exists
docker-compose exec postgres psql -U qilema -l

# Check connection string
cat .env.staging | grep DATABASE_URL

# Test connection manually
docker-compose exec postgres psql -U qilema -h postgres -d qilema_staging
```

---

## 🔄 Deployment Server Configuration Summary

### Environment Variables

Create `.env.staging` or `.env.prod`:

```bash
# Required for all deployments
ENVIRONMENT=staging
POSTGRES_USER=qilema
POSTGRES_PASSWORD=<strong_password>
POSTGRES_DB=qilema_staging
DATABASE_URL=postgresql://qilema:<strong_password>@postgres:5432/qilema_staging
REDIS_URL=redis://redis:6379/0
SECRET_KEY=<min_64_chars>
ENCRYPTION_KEY=<32_chars>

# Optional - for email/SMS
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=user@example.com
SMTP_PASSWORD=<email_password>

# Optional - for monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

### Backup Retention

```bash
# Daily backups (7 days)
find /backups/daily -type d -mtime +7 -exec rm -rf {} \;

# Weekly backups (4 weeks)
find /backups/weekly -type d -mtime +28 -exec rm -rf {} \;

# Add to crontab
crontab -e

# Add these lines:
0 2 * * * ~/backup.sh
0 3 * * 0 find /backups/daily -type d -mtime +7 -exec rm -rf {} \;
```

---

## ✅ Verification Checklist

After setup, verify:

- [ ] SSH access working from GitHub Actions (test with GitHub Secrets)
- [ ] Docker running and accessible to deploy user
- [ ] Docker Compose configured and running
- [ ] PostgreSQL database accessible
- [ ] Redis cache accessible
- [ ] Application started successfully
- [ ] Health check endpoint responding
- [ ] Backup directory exists and is writable
- [ ] SSL certificates in place (if using HTTPS)
- [ ] Firewall allowing required ports
- [ ] Logs accessible and monitored

---

For questions, refer to DEPLOYMENT_GUIDE.md or contact DevOps team.
