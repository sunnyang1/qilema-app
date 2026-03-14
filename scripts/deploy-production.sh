#!/bin/bash
# Deploy to production environment
# Usage: ./scripts/deploy-production.sh <version>
# Example: ./scripts/deploy-production.sh v1.2.3

set -e

VERSION=$1
ENVIRONMENT=production
COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"

if [ -z "$VERSION" ]; then
    echo "❌ Usage: ./scripts/deploy-production.sh <version>"
    echo "Example: ./scripts/deploy-production.sh v1.2.3"
    exit 1
fi

# Confirm production deployment
echo "⚠️  WARNING: This will deploy to PRODUCTION"
echo "Version: $VERSION"
read -p "Are you absolutely sure? (type 'yes' to continue): " -r
if [ "$REPLY" != "yes" ]; then
    echo "Deployment cancelled"
    exit 1
fi

echo "🚀 Deploying $VERSION to $ENVIRONMENT..."

# Verify we're in the correct directory
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Are you in the project root?"
    exit 1
fi

# Create pre-deployment backup
echo "💾 Creating pre-deployment backup..."
BACKUP_ID=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/pre-deploy-${BACKUP_ID}"
mkdir -p $BACKUP_DIR

# Backup database
if docker-compose -f $COMPOSE_FILE ps postgres | grep -q postgres; then
    echo "📦 Backing up database..."
    docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U qilema qilema_prod | gzip > $BACKUP_DIR/database.sql.gz
    echo "✅ Database backed up to $BACKUP_DIR/database.sql.gz"
fi

# Backup volumes
echo "📦 Backing up volumes..."
docker run --rm -v qilema_prod_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/postgres-volume.tar.gz -C /data .
echo "✅ Volumes backed up"

# Pull version tag
echo "📥 Checking out version $VERSION..."
git fetch origin tags/$VERSION
git checkout tags/$VERSION

# Load environment variables
if [ -f ".env.prod" ]; then
    set -a
    source .env.prod
    set +a
    echo "✅ Loaded .env.prod"
else
    echo "⚠️  .env.prod not found, using defaults"
fi

# Pull latest images for this version
echo "📦 Pulling Docker images for $VERSION..."
docker-compose -f $COMPOSE_FILE pull

# Run database migrations
echo "🔄 Running database migrations..."
docker-compose -f $COMPOSE_FILE exec -T backend python -m alembic upgrade head

# Deploy backend and nginx (blue-green)
echo "🚀 Deploying backend and nginx..."
docker-compose -f $COMPOSE_FILE up -d backend nginx

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 15

# Health checks
echo "🏥 Running health checks..."
RETRY_COUNT=0
MAX_RETRIES=30
until docker-compose -f $COMPOSE_FILE exec backend curl -f http://localhost:8000/health >/dev/null 2>&1; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Backend health check failed after $MAX_RETRIES attempts"
        echo "Rolling back..."
        ./scripts/rollback-production.sh $BACKUP_ID
        exit 1
    fi
    echo "⏳ Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo "✅ Backend is healthy"

# Verify all services
echo "📊 Verifying all services..."
docker-compose -f $COMPOSE_FILE ps

# Smoke tests
echo "🧪 Running smoke tests..."
if curl -f https://api.qilema.com/health >/dev/null 2>&1; then
    echo "✅ API is accessible"
else
    echo "❌ API health check failed"
    echo "Rolling back..."
    ./scripts/rollback-production.sh $BACKUP_ID
    exit 1
fi

# Cleanup old containers
echo "🧹 Cleaning up old containers..."
docker system prune -f --volumes

# Create post-deployment backup
echo "💾 Creating post-deployment backup..."
POST_BACKUP_DIR="./backups/post-deploy-$(date +%Y%m%d_%H%M%S)"
mkdir -p $POST_BACKUP_DIR
docker-compose -f $COMPOSE_FILE exec -T postgres pg_dump -U qilema qilema_prod | gzip > $POST_BACKUP_DIR/database.sql.gz
echo "✅ Post-deployment backup created"

echo ""
echo "✅ Production deployment completed successfully!"
echo "📊 Version: $VERSION"
echo "🔗 Production URL: https://api.qilema.com"
echo "💾 Pre-deployment backup: $BACKUP_DIR"
echo "💾 Post-deployment backup: $POST_BACKUP_DIR"
echo ""
echo "To rollback: ./scripts/rollback-production.sh $BACKUP_ID"
echo "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
