# Deployment Quick Start Guide

For developers deploying the Qilema App.

---

## 📋 Before You Deploy

```bash
# 1. Make sure your code is committed
git status
# Should be: nothing to commit, working tree clean

# 2. Pull latest changes
git pull origin main

# 3. Run local tests
docker-compose up -d
curl http://localhost:8000/health
docker-compose down
```

---

## 🚀 Deploy to Staging (Automatic)

Staging deploys **automatically** when you push to `main`:

```bash
# Create feature branch
git checkout -b feature/your-feature

# Make changes and commit
git add .
git commit -m "Add your feature"

# Push to feature branch (tests run, no deployment)
git push origin feature/your-feature

# Create Pull Request on GitHub

# After approval, merge to main
# This triggers automatic staging deployment

# Monitor in GitHub
# Actions tab → Deploy to Staging workflow
```

**Staging URL**: https://staging.api.qilema.com

**Verify**:
```bash
curl https://staging.api.qilema.com/health
```

---

## 🎯 Deploy to Production (Manual with Approval)

Production requires a version tag and approval:

```bash
# Step 1: Create a release
git checkout main
git pull origin main

# Create version tag
git tag -a v1.2.3 -m "Release v1.2.3: Brief description of changes"

# Push tag (triggers GitHub Actions)
git push origin v1.2.3

# Step 2: Wait for CI to pass
# Go to: https://github.com/yourorg/qilema-app/actions
# Watch Deploy to Production workflow

# Step 3: Approve deployment
# GitHub will wait for approval from reviewers
# Reviewers click "Approve and deploy" button

# Step 4: Monitor deployment
# Watch logs in GitHub Actions
# Deployment includes:
# - Create backup
# - Deploy containers
# - Run migrations
# - Health checks

# Step 5: Verify production
curl https://api.qilema.com/health
```

**Production URL**: https://api.qilema.com

---

## 📊 Deployment Pipeline Flow

```
Your Code
    ↓
Feature Branch (no deployment)
    ↓
Pull Request (tests run)
    ↓
Merge to main (triggers staging deploy)
    ↓
Staging Deployment (automatic)
    ├─ Build Docker images
    ├─ Run migrations
    ├─ Deploy services
    ├─ Health checks
    └─ Ready for testing
    ↓
Create version tag (manual, triggers production deploy)
    ↓
Production Deployment (awaits approval)
    ├─ Create backup
    ├─ Build Docker images
    ├─ Run migrations
    ├─ Deploy services
    ├─ Health checks
    └─ Post-deployment backup
    ↓
✓ Production Live
```

---

## 🔍 View Deployment Status

### GitHub Actions Dashboard

```
https://github.com/yourorg/qilema-app/actions
```

- View all workflow runs
- Click workflow to see details
- Check logs for errors

### Recent Deployments

```bash
# Git tags (releases)
git tag -l --sort=-version:refname | head -10

# Recent commits to main
git log --oneline main -n 10
```

### Check Service Status

```bash
# Staging
curl https://staging.api.qilema.com/health

# Production
curl https://api.qilema.com/health
```

---

## 🛠️ Troubleshooting Deployments

### Deployment Failed - What to Do

1. **Check GitHub Actions logs**
   - Go to Actions tab
   - Click the failed workflow
   - Review detailed error messages

2. **Check server logs**
   ```bash
   ssh deploy@staging.example.com
   docker-compose logs backend | tail -50
   ```

3. **Check if services are running**
   ```bash
   ssh deploy@staging.example.com
   docker-compose ps
   ```

4. **Common Issues**

| Error | Fix |
|-------|-----|
| "Container unhealthy" | Check health endpoint: `curl http://localhost:8000/health` |
| "Connection refused" | Verify PostgreSQL/Redis started: `docker-compose logs postgres` |
| "Migration failed" | Check database: `docker-compose exec postgres pg_isready` |
| "SSH permission denied" | Verify deploy user has Docker permissions: `groups deploy` |
| "Disk space full" | Clean up: `docker system prune -a` |

### Rollback Production (Emergency)

```bash
# If production is broken, rollback:
ssh deploy@prod.example.com
cd /var/www/qilema
./scripts/rollback-production.sh <backup-id>

# List backups to find backup-id:
ls -lh /backups/pre-deploy-*/

# Example:
./scripts/rollback-production.sh 20240115_143022
```

---

## 📝 Version Tags (Semantic Versioning)

Use semantic versioning for tags:

```
v MAJOR . MINOR . PATCH

v 1.0.0   = First release
v 1.1.0   = New feature (minor version)
v 1.0.1   = Bug fix (patch version)
v 2.0.0   = Breaking changes (major version)
```

### Examples

```bash
# First release
git tag -a v1.0.0 -m "Initial production release"

# New feature
git tag -a v1.1.0 -m "Add user authentication"

# Bug fix
git tag -a v1.0.1 -m "Fix login issue"

# Hot fix
git tag -a v1.0.2 -m "Security patch"
```

---

## ✅ Pre-Deployment Checklist

Before pushing to main or creating a tag:

```bash
# 1. All code committed
git status

# 2. Tests passing locally
docker-compose up -d
npm run test  # or your test command
docker-compose down

# 3. No linting errors
npm run lint  # or your lint command

# 4. Code review approved
# (wait for PR approval before merging)

# 5. Changelog updated (optional)
# Add entry to CHANGELOG.md

# 6. Ready to push
git push origin main
```

---

## 📞 Questions?

- **Deployment Help**: See DEPLOYMENT_GUIDE.md
- **Server Setup**: See SERVER_SETUP.md
- **Secrets Setup**: See SECRETS_SETUP.md
- **Full Checklist**: See DEPLOYMENT_SETUP_CHECKLIST.md

---

## 🎯 Typical Deployment Day

### Morning: Check Status
```bash
# Check recent deployments
gh run list --limit 5

# Verify production is healthy
curl https://api.qilema.com/health
```

### Feature Development
```bash
# Create feature branch
git checkout -b feature/add-check-in-history

# Develop and test
# Commit changes
git commit -m "Add check-in history to dashboard"

# Push for testing
git push origin feature/add-check-in-history
```

### Code Review
```bash
# Create PR on GitHub (after tests pass)
# Reviewers approve
# Merge to main (automatic staging deploy)

# Verify on staging
curl https://staging.api.qilema.com/health
```

### Release to Production
```bash
# After staging verified (usually next day or after soak period)
git tag -a v1.2.0 -m "Add check-in history feature"
git push origin v1.2.0

# Wait for approval in GitHub
# Monitor deployment
# Verify production
curl https://api.qilema.com/health
```

---

## 🆘 Emergency - Production Is Down

**Do this immediately:**

1. **Identify the issue**
   ```bash
   curl https://api.qilema.com/health
   # Check response and error messages
   ```

2. **SSH to server**
   ```bash
   ssh -i ~/.ssh/qilema_prod deploy@prod.example.com
   cd /var/www/qilema
   docker-compose ps
   docker-compose logs backend | tail -50
   ```

3. **Quick fix (if obvious)**
   ```bash
   # Restart services
   docker-compose restart backend
   
   # Or restart everything
   docker-compose down
   docker-compose up -d
   ```

4. **If problem persists - ROLLBACK**
   ```bash
   # Find backup ID
   ls -lh /backups/pre-deploy-*/
   
   # Rollback
   ./scripts/rollback-production.sh 20240115_143022
   
   # Verify
   curl https://api.qilema.com/health
   ```

5. **Notify team**
   - Post in #incidents Slack channel
   - Include what happened and what you did

6. **Post-incident**
   - Review logs to understand what went wrong
   - Fix the issue
   - Test fix on staging
   - Deploy fix to production

---

## 📊 Deployment Workflow Summary

| Action | Trigger | Auto? | Approval |
|--------|---------|-------|----------|
| Push to feature branch | Manual | No | N/A |
| Create PR | Manual | Yes (tests) | Manual review |
| Merge to main | Manual | Yes (tests + staging deploy) | N/A |
| Create version tag | Manual | Yes (tests) | Production |
| Deploy to production | Tag created | Yes (with approval) | Manual |
| Rollback | Manual | No | Manual |

---

## 🎓 Learning More

- **Full Guide**: See `DEPLOYMENT_GUIDE.md`
- **Troubleshooting**: See section in `DEPLOYMENT_GUIDE.md`
- **Server Info**: See `SERVER_SETUP.md`
- **Setup Steps**: See `DEPLOYMENT_SETUP_CHECKLIST.md`

---

**Last Updated**: January 15, 2024
**Questions?** Ask in #deployments or #devops Slack channel
