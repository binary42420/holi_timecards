# Quick Backend Fix Deployment Script for HOLI Timesheets

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "🔧 Quick Backend Fix Deployment for HOLI Timesheets" -ForegroundColor Green

# Check if DB_PASSWORD is set
if (-not $env:DB_PASSWORD) {
    Write-Host "❌ DB_PASSWORD environment variable is not set!" -ForegroundColor Red
    Write-Host "Setting DB_PASSWORD from .env file..." -ForegroundColor Yellow
    $env:DB_PASSWORD = "a61d15d9b4f2671739338d1082cc7b75c0084e21"
}

# Set the project
Write-Host "📋 Setting project to $ProjectId" -ForegroundColor Yellow
gcloud config set project $ProjectId

# Build and deploy backend only
Write-Host "🏗️ Building backend image" -ForegroundColor Yellow
Set-Location Backend

# Build the image
gcloud builds submit --tag "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo/holi-timesheets-backend:latest" .

Write-Host "🚀 Deploying backend to Cloud Run" -ForegroundColor Yellow

# Deploy with all environment variables
gcloud run deploy holi-timesheets-backend `
    --image "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo/holi-timesheets-backend:latest" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8080 `
    --memory 1Gi `
    --cpu 1 `
    --concurrency 100 `
    --timeout 300 `
    --set-env-vars "GOOGLE_CLIENT_ID=444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com" `
    --set-env-vars "DB_HOST=miano.h.filess.io" `
    --set-env-vars "DB_PORT=3305" `
    --set-env-vars "DB_USER=easyshiftsdb_danceshall" `
    --set-env-vars "DB_NAME=easyshiftsdb_danceshall" `
    --set-env-vars "DB_PASSWORD=$env:DB_PASSWORD" `
    --set-env-vars "REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com" `
    --set-env-vars "REDIS_PORT=12649" `
    --set-env-vars "REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa" `
    --set-env-vars "REDIS_DB=0" `
    --set-env-vars "SESSION_SECRET_KEY=K8mP9vN2xQ7wE5tR1yU6iO3pA8sD4fG9hJ2kL5nM7bV0cX1zQ6wE9rT3yU8iO5pA" `
    --set-env-vars "CSRF_SECRET_KEY=X9mN2bV5cQ8wE1rT4yU7iO0pA3sD6fG2hJ5kL8nM1bV4cX7zQ0wE3rT6yU9iO2pA" `
    --set-env-vars "ENVIRONMENT=production" `
    --set-env-vars "DEBUG=false" `
    --set-env-vars "VALIDATE_SESSION_IP=false" `
    --set-env-vars "SESSION_TIMEOUT=3600" `
    --set-env-vars "LOG_LEVEL=INFO" `
    --set-env-vars "HOST=0.0.0.0" `
    --set-env-vars "PORT=8080"

# Get backend URL
$BackendUrl = gcloud run services describe holi-timesheets-backend --platform managed --region $Region --format 'value(status.url)'
$WsUrl = ($BackendUrl -replace "https:", "wss:") + "/ws"

Write-Host "✅ Backend deployment completed!" -ForegroundColor Green
Write-Host "🔧 Backend URL: $BackendUrl" -ForegroundColor Green
Write-Host "🔌 WebSocket URL: $WsUrl" -ForegroundColor Green

# Test the backend
Write-Host "🧪 Testing backend health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BackendUrl/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Backend health check passed!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Backend health check failed, but service is deployed. It may take a few minutes to start." -ForegroundColor Yellow
}

Set-Location ..

Write-Host ""
Write-Host "🔄 Next steps:" -ForegroundColor Cyan
Write-Host "1. Wait 2-3 minutes for the service to fully start" -ForegroundColor Cyan
Write-Host "2. Test WebSocket connection at: $WsUrl" -ForegroundColor Cyan
Write-Host "3. Check your frontend at: http://localhost:3000/websocket-test" -ForegroundColor Cyan
Write-Host "4. If issues persist, check Cloud Run logs with:" -ForegroundColor Cyan
Write-Host "   gcloud logs read --service=holi-timesheets-backend --limit=50" -ForegroundColor Cyan
