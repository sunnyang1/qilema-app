# GitHub Secrets Configuration Guide

This guide explains how to set up all required secrets for the deployment pipeline.

## Access Repository Secrets

1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Click "New repository secret"

## Required Secrets

### Docker Registry Credentials

#### DOCKER_HUB_USERNAME
- **Description**: Your Docker Hub username
- **Value**: `your_docker_username`
- **Where to find**: https://hub.docker.com/settings/account

#### DOCKER_HUB_PASSWORD
- **Description**: Docker Hub access token (NOT your password)
- **Value**: `dckr_pat_xxxxxxxxxxxx`
- **How to create**:
  1. Go to https://hub.docker.com/settings/security
  2. Click "New Access Token"
  3. Name: `GitHub Actions`
  4. Permissions: `Read & Write`
  5. Copy the token

#### REGISTRY_URL (Optional)
- **Description**: Custom container registry URL
- **Default**: `docker.io`
- **Value**: `registry.example.com` (if using private registry)

### Staging Environment Secrets

#### STAGING_SERVER_HOST
- **Description**: Staging server hostname or IP
- **Value**: `staging.example.com`

#### STAGING_DEPLOY_USER
- **Description**: SSH user for staging server
- **Value**: `deploy`
- **Setup**:
  ```bash
  ssh deploy@staging.example.com
  # User must have Docker permissions
  groups deploy  # Should include 'docker'
  ```

#### STAGING_DEPLOY_KEY
- **Description**: SSH private key for staging deployment
- **Value**: (full private key content)
- **How to create**:
  ```bash
  # Generate SSH key
  ssh-keygen -t rsa -b 4096 -f ~/.ssh/qilema_staging

  # Display private key (to copy into GitHub)
  cat ~/.ssh/qilema_staging

  # Copy public key to server
  ssh-copy-id -i ~/.ssh/qilema_staging.pub deploy@staging.example.com
  ```
- **Format**: Should start with `-----BEGIN RSA PRIVATE KEY-----` and end with `-----END RSA PRIVATE KEY-----`

#### STAGING_APP_PATH
- **Description**: Path to application directory on staging server
- **Value**: `/var/www/qilema`
- **Setup**:
  ```bash
  ssh deploy@staging.example.com
  sudo mkdir -p /var/www/qilema
  sudo chown deploy:deploy /var/www/qilema
  chmod 755 /var/www/qilema
  ```

### Production Environment Secrets

#### PROD_SERVER_HOST
- **Description**: Production server hostname or IP
- **Value**: `prod.example.com`

#### PROD_DEPLOY_USER
- **Description**: SSH user for production server
- **Value**: `deploy`

#### PROD_DEPLOY_KEY
- **Description**: SSH private key for production deployment
- **Value**: (full private key content)
- **Security Note**: This is highly sensitive. Consider using a hardware security key.

#### PROD_APP_PATH
- **Description**: Path to application directory on production server
- **Value**: `/var/www/qilema`

#### PROD_DATABASE_URL
- **Description**: Production database connection string
- **Value**: `postgresql://user:password@host:5432/qilema_prod`
- **Security Note**: Never commit to version control. Use GitHub secret.

#### PROD_REDIS_URL
- **Description**: Production Redis connection string
- **Value**: `redis://user:password@host:6379/0`
- **Security Note**: Never commit to version control. Use GitHub secret.

### Notification Secrets

#### SLACK_WEBHOOK
- **Description**: Slack webhook URL for deployment notifications
- **Value**: `https://hooks.slack.com/services/YOUR/WEBHOOK/URL`
- **How to create**:
  1. Go to your Slack workspace
  2. Create a new app or use existing: https://api.slack.com/apps
  3. Enable "Incoming Webhooks"
  4. Click "Add New Webhook to Workspace"
  5. Select channel: `#deployments`
  6. Copy the webhook URL

### AWS Credentials (Optional - for S3 backups)

#### AWS_ACCESS_KEY_ID
- **Description**: AWS access key for S3 backup storage
- **Value**: `AKIAIOSFODNN7EXAMPLE`

#### AWS_SECRET_ACCESS_KEY
- **Description**: AWS secret access key
- **Value**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

---

## Environment Variables Configuration

### .env.staging

Create `.env.staging` on staging server:

```bash
ssh deploy@staging.example.com
cat > /var/www/qilema/.env.staging << 'EOF'
ENVIRONMENT=staging
DEBUG=True
LOG_LEVEL=INFO

# Database
POSTGRES_USER=qilema
POSTGRES_PASSWORD=staging_password_here
POSTGRES_DB=qilema_staging
DATABASE_URL=postgresql://qilema:staging_password_here@postgres:5432/qilema_staging

# Redis
REDIS_URL=redis://redis:6379/0

# Application
SECRET_KEY=your-secret-key-min-64-chars-here-very-long-string-for-staging
ENCRYPTION_KEY=your-encryption-key-32-chars-here

# API
API_BASE_URL=https://staging.api.qilema.com

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=staging@example.com
SMTP_PASSWORD=staging_email_password

# Features (enable testing features in staging)
ENABLE_DEBUG_ENDPOINTS=True
ENABLE_MOCK_SMS=True
EOF
```

### .env.prod

Create `.env.prod` on production server:

```bash
ssh deploy@prod.example.com
cat > /var/www/qilema/.env.prod << 'EOF'
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING

# Database
POSTGRES_USER=qilema
POSTGRES_PASSWORD=very_strong_password_here_change_this
POSTGRES_DB=qilema_prod
DATABASE_URL=postgresql://qilema:very_strong_password_here_change_this@postgres:5432/qilema_prod

# Redis
REDIS_URL=redis://redis:6379/0

# Application
SECRET_KEY=your-production-secret-key-min-64-chars-here-very-long-string
ENCRYPTION_KEY=your-production-encryption-key-32-chars-here

# API
API_BASE_URL=https://api.qilema.com

# Email
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=noreply@example.com
SMTP_PASSWORD=production_email_password

# Monitoring
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id

# Features
ENABLE_DEBUG_ENDPOINTS=False
ENABLE_MOCK_SMS=False
EOF

# Secure the file
chmod 600 /var/www/qilema/.env.prod
```

---

## Verification Checklist

Run these commands to verify secrets are configured correctly:

```bash
# 1. Test Docker Hub credentials
docker login -u $DOCKER_HUB_USERNAME -p $DOCKER_HUB_PASSWORD

# 2. Test SSH connection to staging
ssh -i ~/.ssh/qilema_staging deploy@$STAGING_SERVER_HOST "docker ps"

# 3. Test SSH connection to production
ssh -i ~/.ssh/qilema_prod deploy@$PROD_SERVER_HOST "docker ps"

# 4. Verify environment files exist
ssh deploy@$STAGING_SERVER_HOST "test -f $STAGING_APP_PATH/.env.staging && echo 'OK'"
ssh deploy@$PROD_SERVER_HOST "test -f $PROD_APP_PATH/.env.prod && echo 'OK'"

# 5. Test Slack webhook
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test notification"}' \
  $SLACK_WEBHOOK
```

---

## Security Best Practices

### ✅ DO

- **Rotate SSH keys quarterly**
- **Use strong, unique passwords** for all services
- **Enable 2FA** on Docker Hub and GitHub
- **Audit secret access** logs regularly
- **Keep backups encrypted** and stored securely
- **Rotate production secrets** after any security incident
- **Use environment-specific credentials** (don't reuse secrets)

### ❌ DON'T

- **Commit secrets to version control**
- **Share secrets via email or chat**
- **Use test secrets in production**
- **Store unencrypted backups**
- **Leave old SSH keys lying around**
- **Use personal credentials** for CI/CD

---

## Troubleshooting

### Docker Login Fails
```bash
# Verify credentials
echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKER_HUB_USERNAME --password-stdin

# Create new access token if needed
# https://hub.docker.com/settings/security
```

### SSH Connection Fails
```bash
# Test SSH key
ssh -i ~/.ssh/qilema_staging -v deploy@staging.example.com

# Common issue: Wrong permissions
# Fix: chmod 600 ~/.ssh/qilema_staging
```

### Deployment Hangs
```bash
# Check GitHub Actions logs
# May be waiting for approval in production environment

# Check if SSH server is responding
ssh -v deploy@prod.example.com "echo ok"
```

---

## Secret Rotation

### Quarterly Rotation Checklist

```bash
# 1. Generate new SSH keys
ssh-keygen -t rsa -b 4096 -f ~/.ssh/qilema_prod_new

# 2. Update authorized_keys on server
ssh-copy-id -i ~/.ssh/qilema_prod_new.pub deploy@prod.example.com

# 3. Update GitHub secret
# Settings → Secrets → PROD_DEPLOY_KEY → Update

# 4. Remove old key
rm ~/.ssh/qilema_prod
rm ~/.ssh/qilema_prod.pub

# 5. Test new key
ssh -i ~/.ssh/qilema_prod_new deploy@prod.example.com "docker ps"
```

---

For questions or issues, contact your DevOps team.
