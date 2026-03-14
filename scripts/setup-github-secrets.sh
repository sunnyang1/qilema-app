#!/bin/bash
# Interactive GitHub Secrets Configuration Helper
# This script guides you through setting up all required GitHub secrets

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

REPO_URL=""
SECRETS_SET=0

header() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     🚀 GitHub Secrets Configuration Helper                   ║
║        Qilema App Deployment Pipeline                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "$(printf '═%.0s' {1..60})"
}

prompt_yes_no() {
    local question=$1
    local response
    read -p "$(echo -e ${YELLOW}$question' (y/n): '${NC})" -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

copy_to_clipboard() {
    local text=$1
    if command -v pbcopy &> /dev/null; then
        echo "$text" | pbcopy
        echo -e "${GREEN}✓ Copied to clipboard${NC}"
    elif command -v xclip &> /dev/null; then
        echo "$text" | xclip -selection clipboard
        echo -e "${GREEN}✓ Copied to clipboard${NC}"
    else
        echo "Please copy manually: $text"
    fi
}

get_repo_url() {
    header
    section "Repository Information"
    
    echo "Enter your GitHub repository URL"
    echo "Example: https://github.com/yourorg/qilema-app"
    read -p "Repository URL: " REPO_URL
    
    if [[ ! $REPO_URL =~ ^https://github.com/.+/.+ ]]; then
        echo -e "${RED}✗ Invalid repository URL${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Repository: $REPO_URL${NC}"
}

setup_docker_credentials() {
    header
    section "Docker Hub Credentials"
    
    echo "You need Docker Hub credentials for pushing images."
    echo ""
    echo "1. Go to: https://hub.docker.com/settings/account"
    echo "2. Username: Your Docker Hub username"
    echo ""
    echo "3. To create an access token:"
    echo "   - Go to: https://hub.docker.com/settings/security"
    echo "   - Click 'New Access Token'"
    echo "   - Name: 'GitHub Actions'"
    echo "   - Permissions: 'Read & Write'"
    echo "   - Copy the token"
    echo ""
    
    read -p "Enter your Docker Hub username: " DOCKER_USERNAME
    read -sp "Enter your Docker Hub access token (will not be displayed): " DOCKER_TOKEN
    echo ""
    
    if [ -z "$DOCKER_USERNAME" ] || [ -z "$DOCKER_TOKEN" ]; then
        echo -e "${RED}✗ Docker credentials required${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Docker Hub credentials ready${NC}"
    echo ""
    
    # Open GitHub secrets page
    if prompt_yes_no "Open GitHub secrets page in browser?"; then
        REPO_PATH=$(echo $REPO_URL | sed 's|https://github.com/||')
        open "https://github.com/$REPO_PATH/settings/secrets/actions" 2>/dev/null || \
        echo "Open: https://github.com/$REPO_PATH/settings/secrets/actions"
        
        echo ""
        echo "Add these secrets:"
        echo "  Name: DOCKER_HUB_USERNAME"
        echo "  Value: $DOCKER_USERNAME"
        echo ""
        echo "  Name: DOCKER_HUB_PASSWORD"
        echo "  Value: $DOCKER_TOKEN"
        echo ""
        read -p "Press Enter after adding secrets..."
    fi
}

setup_staging_server() {
    header
    section "Staging Server Configuration"
    
    echo "You need SSH access to your staging server."
    echo ""
    echo "If you don't have a staging server yet, see: DEPLOYMENT_GUIDE.md"
    echo ""
    
    if ! prompt_yes_no "Do you have a staging server configured?"; then
        echo -e "${YELLOW}⚠ Skipping staging setup. Configure later.${NC}"
        return 0
    fi
    
    read -p "Staging server hostname/IP (e.g., staging.example.com): " STAGING_HOST
    read -p "SSH username (typically 'deploy'): " STAGING_USER
    read -p "Application path (e.g., /var/www/qilema): " STAGING_PATH
    
    echo ""
    echo "SSH key setup:"
    echo "1. Generate SSH key:"
    echo "   ssh-keygen -t rsa -b 4096 -f ~/.ssh/qilema_staging"
    echo ""
    echo "2. Copy to server:"
    echo "   ssh-copy-id -i ~/.ssh/qilema_staging.pub $STAGING_USER@$STAGING_HOST"
    echo ""
    echo "3. Get private key for GitHub (copy output below):"
    echo ""
    
    if [ -f ~/.ssh/qilema_staging ]; then
        echo "$(cat ~/.ssh/qilema_staging)"
    else
        echo -e "${YELLOW}⚠ SSH key not found. Generate it first with commands above.${NC}"
        return 1
    fi
    
    echo ""
    read -p "Press Enter after setting up SSH..."
    
    echo -e "${GREEN}✓ Staging server configuration ready${NC}"
    echo ""
    echo "Add these secrets to GitHub:"
    echo "  STAGING_SERVER_HOST = $STAGING_HOST"
    echo "  STAGING_DEPLOY_USER = $STAGING_USER"
    echo "  STAGING_APP_PATH = $STAGING_PATH"
    echo "  STAGING_DEPLOY_KEY = <private key from ~/.ssh/qilema_staging>"
    echo ""
    read -p "Press Enter after adding secrets..."
}

setup_production_server() {
    header
    section "Production Server Configuration"
    
    echo "Production setup requires careful security consideration."
    echo ""
    
    if ! prompt_yes_no "Do you have a production server configured?"; then
        echo -e "${YELLOW}⚠ Skipping production setup. Configure later.${NC}"
        return 0
    fi
    
    read -p "Production server hostname/IP: " PROD_HOST
    read -p "SSH username: " PROD_USER
    read -p "Application path: " PROD_PATH
    
    echo ""
    echo "🔒 SECURITY WARNING 🔒"
    echo "The SSH private key will be stored in GitHub secrets."
    echo "This is sensitive! Consider using deploy keys instead."
    echo ""
    
    echo "SSH key setup:"
    echo "1. Generate SSH key:"
    echo "   ssh-keygen -t rsa -b 4096 -f ~/.ssh/qilema_prod"
    echo ""
    echo "2. Copy to server:"
    echo "   ssh-copy-id -i ~/.ssh/qilema_prod.pub $PROD_USER@$PROD_HOST"
    echo ""
    echo "3. Get private key for GitHub:"
    echo ""
    
    if [ -f ~/.ssh/qilema_prod ]; then
        echo "$(cat ~/.ssh/qilema_prod)"
    else
        echo -e "${YELLOW}⚠ SSH key not found. Generate it first.${NC}"
        return 1
    fi
    
    echo ""
    read -p "Press Enter after setting up SSH..."
    
    echo -e "${GREEN}✓ Production server configuration ready${NC}"
    echo ""
    echo "Add these secrets to GitHub:"
    echo "  PROD_SERVER_HOST = $PROD_HOST"
    echo "  PROD_DEPLOY_USER = $PROD_USER"
    echo "  PROD_APP_PATH = $PROD_PATH"
    echo "  PROD_DEPLOY_KEY = <private key from ~/.ssh/qilema_prod>"
    echo ""
    read -p "Press Enter after adding secrets..."
}

setup_slack_webhook() {
    header
    section "Slack Notifications (Optional)"
    
    if ! prompt_yes_no "Do you want Slack notifications for deployments?"; then
        echo -e "${YELLOW}✓ Skipping Slack setup${NC}"
        return 0
    fi
    
    echo ""
    echo "Create a Slack webhook for notifications:"
    echo "1. Go to: https://api.slack.com/apps"
    echo "2. Create New App or use existing"
    echo "3. Enable 'Incoming Webhooks'"
    echo "4. Click 'Add New Webhook to Workspace'"
    echo "5. Select channel: #deployments (or your channel)"
    echo "6. Copy the webhook URL"
    echo ""
    read -p "Enter Slack webhook URL: " SLACK_WEBHOOK
    
    if [ -z "$SLACK_WEBHOOK" ]; then
        echo -e "${RED}✗ Webhook URL required${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✓ Slack webhook ready${NC}"
    echo ""
    echo "Add this secret to GitHub:"
    echo "  SLACK_WEBHOOK = $SLACK_WEBHOOK"
    echo ""
    read -p "Press Enter after adding secret..."
}

create_github_environments() {
    header
    section "Creating GitHub Environments"
    
    REPO_PATH=$(echo $REPO_URL | sed 's|https://github.com/||')
    
    echo "You need to create two environments in GitHub:"
    echo ""
    echo "1. Staging (no approval required)"
    echo "   URL: https://github.com/$REPO_PATH/settings/environments"
    echo "   - Click 'New environment'"
    echo "   - Name: 'staging'"
    echo "   - No deployment branches restriction needed"
    echo ""
    echo "2. Production (with approval)"
    echo "   URL: https://github.com/$REPO_PATH/settings/environments"
    echo "   - Click 'New environment'"
    echo "   - Name: 'production'"
    echo "   - Add required reviewers (team leads)"
    echo "   - Set deployment branches to protected branches only"
    echo ""
    
    if prompt_yes_no "Open GitHub environments page?"; then
        open "https://github.com/$REPO_PATH/settings/environments" 2>/dev/null || \
        echo "Open: https://github.com/$REPO_PATH/settings/environments"
        
        read -p "Press Enter after creating environments..."
    fi
    
    echo -e "${GREEN}✓ GitHub environments created${NC}"
}

setup_env_files() {
    header
    section "Environment Files Setup"
    
    echo "You need to create .env files on your deployment servers."
    echo ""
    
    if prompt_yes_no "Create .env.staging template locally first?"; then
        echo "Creating .env.staging template..."
        
        cat > .env.staging.template << 'EOF'
# Staging Environment Configuration
ENVIRONMENT=staging
DEBUG=True
LOG_LEVEL=INFO

# Database
POSTGRES_USER=qilema
POSTGRES_PASSWORD=staging_password_change_this
POSTGRES_DB=qilema_staging
DATABASE_URL=postgresql://qilema:staging_password_change_this@postgres:5432/qilema_staging

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

# Features
ENABLE_DEBUG_ENDPOINTS=True
ENABLE_MOCK_SMS=True
EOF
        
        echo -e "${GREEN}✓ Created .env.staging.template${NC}"
    fi
    
    if prompt_yes_no "Create .env.prod template locally first?"; then
        echo "Creating .env.prod template..."
        
        cat > .env.prod.template << 'EOF'
# Production Environment Configuration
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
        
        echo -e "${GREEN}✓ Created .env.prod.template${NC}"
    fi
}

test_setup() {
    header
    section "Testing Your Setup"
    
    echo "Let's verify your deployment configuration..."
    echo ""
    
    # Check git
    echo -n "Checking Git... "
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
    
    # Check Docker
    echo -n "Checking Docker... "
    if docker --version > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
    
    # Check Docker Compose
    echo -n "Checking Docker Compose... "
    if docker-compose --version > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${GREEN}✓ All tools are available${NC}"
}

final_checklist() {
    header
    section "Final Deployment Checklist"
    
    cat << 'EOF'
✅ IMMEDIATE ACTIONS (Before First Deployment)

Before pushing to GitHub and triggering deployments, verify:

1. GitHub Secrets Configuration
   ☐ DOCKER_HUB_USERNAME
   ☐ DOCKER_HUB_PASSWORD
   ☐ STAGING_SERVER_HOST
   ☐ STAGING_DEPLOY_USER
   ☐ STAGING_DEPLOY_KEY
   ☐ STAGING_APP_PATH
   ☐ PROD_SERVER_HOST
   ☐ PROD_DEPLOY_USER
   ☐ PROD_DEPLOY_KEY
   ☐ PROD_APP_PATH
   ☐ SLACK_WEBHOOK (optional)

2. Server Setup
   ☐ Staging server has Docker installed
   ☐ Production server has Docker installed
   ☐ SSH keys copied to both servers
   ☐ Deploy user created with Docker permissions
   ☐ Backup directories created (/backups)
   ☐ Application directories created and cloned
   ☐ .env files created on both servers

3. GitHub Configuration
   ☐ Created 'staging' environment
   ☐ Created 'production' environment
   ☐ Added reviewers to production environment
   ☐ Enabled required status checks

4. Local Testing
   ☐ Run: ./scripts/pre-deployment-check.sh
   ☐ Run: docker-compose up -d
   ☐ Verify: curl http://localhost:8000/health

✅ FIRST DEPLOYMENT (Testing)

1. Create feature branch:
   git checkout -b test/deployment-setup
   git add .github/workflows/ scripts/ DEPLOYMENT*.md SECRETS_SETUP.md
   git commit -m "Add deployment pipeline"
   git push origin test/deployment-setup

2. Create pull request and merge to main

3. Wait for GitHub Actions:
   - CI tests should pass
   - Docker build should complete
   - Staging deployment should trigger

4. Verify staging:
   curl https://staging.api.qilema.com/health

✅ PRODUCTION DEPLOYMENT (After Verification)

1. Create version tag:
   git tag v0.1.0
   git push origin v0.1.0

2. GitHub Actions will:
   - Run tests
   - Build images
   - Wait for approval
   - Deploy to production

3. Verify production:
   curl https://api.qilema.com/health

✅ TROUBLESHOOTING REFERENCES

- DEPLOYMENT_GUIDE.md - Complete troubleshooting
- SECRETS_SETUP.md - Secret configuration details
- DEPLOYMENT_PIPELINE_STATUS.md - Quick reference

EOF
    
    echo ""
    read -p "Press Enter to finish..."
}

# Main flow
main() {
    get_repo_url
    setup_docker_credentials
    setup_staging_server
    setup_production_server
    setup_slack_webhook
    create_github_environments
    setup_env_files
    test_setup
    final_checklist
    
    echo ""
    echo -e "${GREEN}✅ Setup Complete!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Verify all GitHub secrets are added"
    echo "2. Set up deployment servers"
    echo "3. Create and push to GitHub"
    echo "4. Monitor first deployment in GitHub Actions"
    echo ""
}

main
