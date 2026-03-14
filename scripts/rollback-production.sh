#!/bin/bash
# Rollback production to a previous backup
# Usage: ./scripts/rollback-production.sh <backup-id>
# Example: ./scripts/rollback-production.sh 20240115_143022

set -e

BACKUP_ID=$1
BACKUP_DIR="./backups/pre-deploy-${BACKUP_ID}"
COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"

if [ -z "$BACKUP_ID" ]; then
    echo "❌ Usage: ./scripts/rollback-production.sh <backup-id>"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/ 2>/dev/null | grep pre-deploy || echo "No pre-deploy backups found"
    exit 1
fi

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory not found: $BACKUP_DIR"
    echo ""
    echo "Available backups:"
    ls -lh ./backups/ 2>/dev/null || echo "No backups found"
    exit 1
fi

# Confirm rollback
echo "⚠️  WARNING: This will rollback production to backup $BACKUP_ID"
read -p "Are you absolutely sure? (type 'yes' to continue): " -r
if [ "$REPLY" != "yes" ]; then
    echo "Rollback cancelled"
    exit 1
fi

echo "🔙 Rolling back production to backup: $BACKUP_ID"

# Stop current containers
echo "🛑 Stopping current containers..."
docker-compose -f $COMPOSE_FILE down

# Restore database
echo "📥 Restoring database from backup..."
if [ -f "$BACKUP_DIR/database.sql.gz" ]; then
    gunzip < $BACKUP_DIR/database.sql.gz | docker-compose -f $COMPOSE_FILE exec -T postgres psql -U qilema qilema_prod
    echo "✅ Database restored"
else
    echo "⚠️  Warning: Database backup not found at $BACKUP_DIR/database.sql.gz"
fi

# Restore volumes if available
if [ -f "$BACKUP_DIR/postgres-volume.tar.gz" ]; then
    echo "📥 Restoring volumes..."
    # Note: Volume restoration requires careful handling - stopping containers first
    docker run --rm -v qilema_prod_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar xzf /backup/postgres-volume.tar.gz -C /data
    echo "✅ Volumes restored"
fi

# Start services
echo "🚀 Starting services..."
docker-compose -f $COMPOSE_FILE up -d

# Wait for services
echo "⏳ Waiting for services..."
sleep 15

# Health check
echo "🏥 Running health checks..."
if docker-compose -f $COMPOSE_FILE exec backend curl -f http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed after rollback"
    exit 1
fi

# Verify
echo "📊 Services status:"
docker-compose -f $COMPOSE_FILE ps

echo ""
echo "✅ Rollback completed successfully!"
echo "📊 Services rolled back to state from: $BACKUP_ID"
echo ""
echo "Next steps:"
echo "1. Investigate the issue that caused the deployment to fail"
echo "2. Fix the issue"
echo "3. Create a new version tag and redeploy"
