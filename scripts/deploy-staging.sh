#!/bin/bash
# Deploy to staging environment
# Usage: ./scripts/deploy-staging.sh [branch]

set -e

BRANCH=${1:-main}
ENVIRONMENT=staging
COMPOSE_FILE="docker-compose.yml -f docker-compose.staging.yml"

echo "🚀 Deploying $BRANCH to $ENVIRONMENT..."

# Verify we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Are you in the project root?"
    exit 1
fi

# Pull latest code
echo "📥 Pulling latest code from $BRANCH..."
git fetch origin $BRANCH
git checkout origin/$BRANCH

# Load environment variables
if [ -f ".env.staging" ]; then
    set -a
    source .env.staging
    set +a
    echo "✅ Loaded .env.staging"
else
    echo "⚠️  .env.staging not found, using defaults"
fi

# Pull latest images
echo "📦 Pulling latest Docker images..."
docker-compose -f $COMPOSE_FILE pull

# Run database migrations (if needed)
read -p "Run database migrations? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Running database migrations..."
    docker-compose -f $COMPOSE_FILE exec backend python -m alembic upgrade head
fi

# Deploy
echo "🚀 Deploying containers..."
docker-compose -f $COMPOSE_FILE up -d --no-deps backend nginx

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 10

# Health check
echo "🏥 Running health checks..."
if docker-compose -f $COMPOSE_FILE exec backend curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    docker-compose -f $COMPOSE_FILE logs backend
    exit 1
fi

if docker-compose -f $COMPOSE_FILE exec nginx curl -f http://127.0.0.1/health >/dev/null 2>&1; then
    echo "✅ Nginx is healthy"
else
    echo "❌ Nginx health check failed"
    docker-compose -f $COMPOSE_FILE logs nginx
    exit 1
fi

# Smoke tests
echo "🧪 Running smoke tests..."
if curl -f https://staging.api.qilema.com/health >/dev/null 2>&1; then
    echo "✅ API is accessible"
else
    echo "⚠️  Warning: Could not reach API endpoint"
fi

echo ""
echo "✅ Staging deployment completed successfully!"
echo "📊 Staging URL: https://staging.api.qilema.com"
echo ""
echo "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
echo "To rollback: git checkout main && docker-compose -f $COMPOSE_FILE up -d --no-deps backend nginx"
