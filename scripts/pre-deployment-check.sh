#!/bin/bash
# Pre-deployment checklist script
# Run this before deploying to production

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

FAILED=0
PASSED=0

check() {
    local description=$1
    local command=$2

    echo -n "Checking: $description... "

    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC}"
        ((FAILED++))
    fi
}

section() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "$(printf '─%.0s' {1..50})"
}

# Repository checks
section "Repository Status"
check "Git working directory clean" "git diff-index --quiet HEAD --"
check "Git branch is main or develop" "git branch --show-current | grep -E '(main|develop)'"
check "Tags exist" "git tag | grep -E '^v'"
check "No uncommitted changes" "git status --porcelain | wc -l | grep '^0$'"

# Codebase checks
section "Code Quality"
check "Dockerfile exists" "test -f backend/Dockerfile"
check "docker-compose.yml exists" "test -f docker-compose.yml"
check "docker-compose.prod.yml exists" "test -f docker-compose.prod.yml"
check "nginx Dockerfile exists" "test -f nginx/Dockerfile"
check ".env.example exists" "test -f .env.example"
check "requirements.txt exists" "test -f backend/requirements.txt"

# Configuration checks
section "Configuration Files"
check "Deployment scripts exist" "test -f scripts/deploy-staging.sh"
check "Rollback script exists" "test -f scripts/rollback-production.sh"
check "Workflows configured" "test -f .github/workflows/deploy-docker.yml"
check "Deployment documentation exists" "test -f DEPLOYMENT_GUIDE.md"
check "Secrets guide exists" "test -f SECRETS_SETUP.md"

# Docker checks
section "Docker Setup"
check "Docker is running" "docker ps >/dev/null 2>&1"
check "Docker Compose is installed" "docker-compose --version >/dev/null 2>&1"
check "Can build backend image" "docker build -t qilema-backend:test ./backend >/dev/null 2>&1"
check "Can build nginx image" "docker build -t qilema-nginx:test ./nginx >/dev/null 2>&1"

# Docker Compose validation
section "Docker Compose Validation"
check "Dev compose file valid" "docker-compose -f docker-compose.yml -f docker-compose.dev.yml config >/dev/null 2>&1"
check "Staging compose file valid" "docker-compose -f docker-compose.yml -f docker-compose.staging.yml config >/dev/null 2>&1"
check "Prod compose file valid" "docker-compose -f docker-compose.yml -f docker-compose.prod.yml config >/dev/null 2>&1"

# Local deployment test
section "Local Deployment Test"
check "Can start local services" "docker-compose up -d >/dev/null 2>&1 && sleep 5"
check "PostgreSQL is healthy" "docker-compose exec -T postgres pg_isready >/dev/null 2>&1"
check "Redis is healthy" "docker-compose exec -T redis redis-cli ping >/dev/null 2>&1"
check "Backend API responds" "curl -sf http://localhost:8000/health >/dev/null 2>&1"
check "Can stop services" "docker-compose down >/dev/null 2>&1"

# Tests
section "Test Suite"
check "Backend tests exist" "test -d backend/tests"
check "Test configuration exists" "test -f pytest.ini || test -f backend/pyproject.toml"

# Security checks
section "Security Checks"
check "No hardcoded secrets in code" "! grep -r 'password=' . --include='*.py' --include='*.sh' 2>/dev/null | grep -v '.env' | grep -v '#'"
check ".env files in .gitignore" "grep -q '^.env' .gitignore"
check ".env.*.local in .gitignore" "grep -q '.env.*.local' .gitignore"
check "No exposed AWS keys" "! grep -r 'AKIA' . --include='*.py' --include='*.sh' 2>/dev/null"

# GitHub setup
section "GitHub Configuration"
check "GitHub workflows directory exists" "test -d .github/workflows"
check "CI workflow exists" "test -f .github/workflows/ci.yml"
check "Test workflow exists" "test -f .github/workflows/test.yml"
check "Deploy Docker workflow exists" "test -f .github/workflows/deploy-docker.yml"
check "Deploy staging workflow exists" "test -f .github/workflows/deploy-staging.yml"
check "Deploy production workflow exists" "test -f .github/workflows/deploy-production.yml"

# Backup and recovery
section "Backup Configuration"
check "Backup directory exists" "test -d backups || mkdir -p backups"
check "Backups are accessible" "test -w backups"
check "Backup script permissions" "test -x scripts/rollback-production.sh"

# Results
section "Summary"
echo ""
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed! Ready to deploy.${NC}"
    exit 0
else
    echo -e "${RED}✗ Some checks failed. Please review above and fix issues.${NC}"
    exit 1
fi
