#!/bin/bash
# SamePageDating Deployment Script

set -e  # Exit on any error

echo "🔄 Pulling latest code from GitHub..."
git pull origin main

echo "🛑 Stopping existing containers..."
docker compose -f docker-compose.prod.yml down || true

echo "🏗️  Building and starting containers..."
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d --build

echo "⏳ Waiting for database to be ready..."
sleep 10

echo "🗄️  Initializing database..."
docker exec deal_finder_backend python -m app.db.init_db || true

echo "📊 Checking container status..."
docker compose -f docker-compose.prod.yml ps

echo "✅ Deployment complete!"
echo "🌐 Visit https://samepagedating.com"
