# Deployment Pipeline Documentation

This document describes the complete deployment pipeline for the Qilema App.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Workflows](#workflows)
4. [Setup Instructions](#setup-instructions)
5. [Deployment Procedures](#deployment-procedures)
6. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
7. [Disaster Recovery](#disaster-recovery)

## Overview

The Qilema deployment pipeline follows a **GitOps** approach with:

- **Continuous Integration (CI)**: Automated testing and validation on every push
- **Docker Build & Push**: Multi-platform image builds with security scanning
- **Staging Deployment**: Automatic deployment to staging on `main` branch
- **Production Deployment**: Manual or tag-triggered deployment to production with approval gates
- **Blue-Green Deployment**: Zero-downtime deployments with automatic rollback

### Key Features

- ✅ Automated image building and scanning for vulnerabilities
- ✅ Multi-environment support (dev, staging, production)
- ✅ Database migration automation
- ✅ Health checks and smoke tests
- ✅ Automated backup and restore
- ✅ Slack notifications
- ✅ Zero-downtime deployments

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      GitHub Repository                       │
├─────────────────────────────────────────────────────────────┤
│  main branch → CI Tests → Docker Build → Staging Deploy     │
│  v*.*.* tags → CI Tests → Docker Build → Prod Deploy        │
└─────────────────────────────────────────────────────────────┘
          ↓                      ↓                     ↓
    ┌──────────┐         ┌─────────────┐      ┌──────────────┐
    │    Dev   │         │   Staging   │      │ Production   │
    │ (Local)  │         │  (AWS EC2)  │      │  (AWS EC2)   │
    └──────────┘         └─────────────┘      └──────────────┘
         ↓                     ↓                     ↓
    Docker          Blue-Green Deploy      Blue-Green Deploy
    Compose          Auto Rollback          Manual Rollback
```

## Workflows

### 1. Continuous Integration (CI)

**File**: `.github/workflows/ci.yml`
**Triggers**: Push to `main`/`develop`, Pull Requests

```yaml
Runs:
- Pre-commit hooks (formatting, secrets scanning)
- Backend tests (pytest with coverage)
- Frontend lint and type check
- Docker image validation
- Docker Compose health check
- Container structure tests
```

### 2. Docker Build & Push

**File**: `.github/workflows/deploy-docker.yml`
**Triggers**: Push to any branch, tags, PRs

```yaml
Builds:
- Backend image (Python 3.12 multi-stage)
- Nginx image (Alpine-based reverse proxy)

Features:
- Multi-platform builds (linux/amd64, linux/arm64)
- Trivy security scanning
- GitHub Container Registry integration
- Docker Hub push capability
- GitHub Actions cache optimization
```

### 3. Staging Deployment

**File**: `.github/workflows/deploy-staging.yml`
**Triggers**: Push to `main` branch, Manual workflow dispatch

```yaml
Steps:
1. Checkout code
2. Configure SSH to staging server
3. Pull latest images and code
4. Run database migrations
5. Deploy backend + nginx (blue-green)
6. Health checks
7. Smoke tests
8. Slack notification
```

### 4. Production Deployment

**File**: `.github/workflows/deploy-production.yml`
**Triggers**: Push with `v*` tag, Manual workflow dispatch

```yaml
Steps:
1. Pre-deployment checks
2. Create database backup
3. Deploy with blue-green strategy
4. Run database migrations
5. Health checks and smoke tests
6. Create post-deployment backup
7. Automatic rollback on failure
```

## Setup Instructions

### Prerequisites

- GitHub repository with GitHub Actions enabled
- Docker Hub account (or container registry)
- Staging and Production servers with Docker installed
- SSH access to deployment servers
- PostgreSQL and Redis databases

### 1. Configure GitHub Secrets

Add the following secrets to GitHub repository settings:

#### Docker Registry
```
DOCKER_HUB_USERNAME     # Docker Hub username
DOCKER_HUB_PASSWORD     # Docker Hub access token
REGISTRY_URL            # (optional) Custom registry URL
```

#### Staging Environment
```
STAGING_SERVER_HOST     # e.g., staging.example.com
STAGING_DEPLOY_USER     # SSH user, e.g., deploy
STAGING_DEPLOY_KEY      # SSH private key (begin/end RSA PRIVATE KEY)
STAGING_APP_PATH        # e.g., /var/www/qilema
```

#### Production Environment
```
PROD_SERVER_HOST        # e.g., prod.example.com
PROD_DEPLOY_USER        # SSH user
PROD_DEPLOY_KEY         # SSH private key
PROD_APP_PATH           # e.g., /var/www/qilema
PROD_DATABASE_URL       # PostgreSQL connection URL
PROD_REDIS_URL          # Redis connection URL
```

#### Notifications
```
SLACK_WEBHOOK           # Slack webhook URL for notifications
AWS_ACCESS_KEY_ID       # (optional) For backups to S3
AWS_SECRET_ACCESS_KEY   # (optional) For backups to S3
```

### 2. Add GitHub Environments

Create two GitHub environments with required reviewers:

**Settings → Environments → New Environment**

1. **staging** - No reviewers needed
2. **production** - Add team leads as reviewers

### 3. Configure Deployment Servers

#### SSH Setup
```bash
# On deployment server
sudo useradd -m deploy
sudo usermod -aG docker deploy
sudo mkdir -p /var/www/qilema
sudo chown deploy:deploy /var/www/qilema

# On your local machine
ssh-keygen -t rsa -b 4096 -f ~/.ssh/qilema_deploy
ssh-copy-id -i ~/.ssh/qilema_deploy.pub deploy@staging.example.com
```

#### Application Setup
```bash
# On staging/production server
ssh deploy@staging.example.com
cd /var/www/qilema
git clone https://github.com/yourorg/qilema-app.git .
cp .env.example .env.staging  # or .env.prod
# Edit .env file with production credentials
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d
```

#### Backup Directory
```bash
ssh deploy@staging.example.com
sudo mkdir -p /backups
sudo chown deploy:deploy /backups
chmod 700 /backups
```

## Deployment Procedures

### Local Development

```bash
# Start local environment
docker-compose up -d

# View logs
docker-compose logs -f backend

# Make code changes
# Test with watch mode
docker-compose watch
```

### Deploy to Staging

**Automatic** (on push to main):
```
Push to main → CI passes → Docker build → Auto deploy to staging
```

**Manual**:
```bash
./scripts/deploy-staging.sh main

# Or via GitHub Actions
# Go to Actions → Deploy to Staging → Run workflow
```

### Deploy to Production

**Create release**:
```bash
# Create version tag
git tag v1.2.3
git push origin v1.2.3

# GitHub will:
# 1. Run CI/CD
# 2. Build and push Docker images
# 3. Create deployment PR
# 4. Wait for approval (if configured)
# 5. Deploy to production
```

**Manual script**:
```bash
# Option 1: Direct script
./scripts/deploy-production.sh v1.2.3

# Option 2: GitHub Actions
# Go to Actions → Deploy to Production → Run workflow
# Enter version: v1.2.3
```

### Database Migrations

Migrations run automatically during deployment:

```bash
# Manual migration (if needed)
docker-compose exec backend python -m alembic upgrade head

# View migration history
docker-compose exec backend python -m alembic history

# Create new migration
docker-compose exec backend python -m alembic revision --autogenerate -m "Add column"
```

## Monitoring & Troubleshooting

### View Deployment Status

```bash
# GitHub Actions
open https://github.com/yourorg/qilema-app/actions

# Container status
docker-compose ps

# Service logs
docker-compose logs backend
docker-compose logs nginx
docker-compose logs postgres

# Health checks
curl http://localhost:8000/health
```

### Common Issues

#### Deployment Fails with "Container unhealthy"

```bash
# Check logs
docker-compose logs backend
docker-compose logs postgres

# Verify connectivity
docker-compose exec backend curl -f http://localhost:8000/health

# Check resources
docker stats

# Restart service
docker-compose restart backend
```

#### Database migration fails

```bash
# View migration status
docker-compose exec backend python -m alembic current

# Rollback last migration
docker-compose exec backend python -m alembic downgrade -1

# Check for conflicts
docker-compose exec postgres psql -U qilema -d qilema_prod -c "\dt"
```

#### Nginx routing issues

```bash
# Test nginx config
docker-compose exec nginx nginx -t

# View config
docker-compose exec nginx cat /etc/nginx/nginx.conf

# Check upstream
docker-compose exec nginx curl http://backend:8000/health
```

### Resource Monitoring

```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Cleanup unused images/containers
docker system prune -a
```

## Disaster Recovery

### Automated Rollback

Production deployments automatically rollback on failure:

1. **Pre-deployment backup created**
2. **Deployment proceeds**
3. **Health checks fail** → Automatic rollback triggered
4. **Services restored** to pre-deployment state

### Manual Rollback

```bash
# List available backups
ls -lh ./backups/

# Rollback to specific backup
./scripts/rollback-production.sh 20240115_143022

# Verify rollback
curl https://api.qilema.com/health
```

### Data Recovery

```bash
# List backups
ls -lh ./backups/pre-deploy-*/

# Restore database from backup
gunzip < ./backups/pre-deploy-20240115_143022/database.sql.gz | \
  docker-compose exec -T postgres psql -U qilema -d qilema_prod

# Verify restoration
docker-compose exec postgres psql -U qilema -d qilema_prod -c "SELECT COUNT(*) FROM users;"
```

### Backup Retention Policy

- **Daily automated backups**: 7 days
- **Weekly backups**: 4 weeks
- **Monthly backups**: 12 months
- **Pre-deployment backups**: Kept indefinitely

Configure backup retention:

```bash
# Run cleanup
./scripts/cleanup-old-backups.sh --days 30

# Or manually
find ./backups -type d -mtime +30 -exec rm -rf {} \;
```

## Best Practices

### ✅ DO

- **Tag releases properly**: Use semantic versioning (v1.2.3)
- **Test before deploying**: Run full test suite locally
- **Review changes**: Always create PR before merge to main
- **Monitor deployments**: Watch Slack notifications and logs
- **Backup before production**: Backups created automatically
- **Document changes**: Include migration notes in commits

### ❌ DON'T

- **Push directly to main**: Always use feature branches and PRs
- **Deploy during incidents**: Wait for stability before deploying
- **Skip health checks**: Always verify health endpoints
- **Delete backups**: Keep backups for at least 30 days
- **Hardcode secrets**: Use environment variables and GitHub secrets

## CI/CD Pipeline Status

Check pipeline health at: https://github.com/yourorg/qilema-app/actions

### Expected Behavior

| Event | Branch | Action |
|-------|--------|--------|
| Push | feature/* | Run tests only |
| Push | develop | Run tests + build |
| Push | main | Run tests + build + deploy staging |
| Push tag | v*.*.* | Run tests + build + deploy production |
| Pull Request | any | Run tests |

---

**Last Updated**: 2024-01-15
**Maintained By**: DevOps Team
**Questions?** Check the troubleshooting section or contact DevOps
