# Update Environment Variables for HOLI Timesheets Cloud Run Services

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "🔧 Updating Environment Variables for HOLI Timesheets" -ForegroundColor Green

# Set the project
gcloud config set project $ProjectId

# Update backend environment variables
Write-Host "🔧 Updating backend environment variables..." -ForegroundColor Yellow

gcloud run services update holi-timesheets-backend `
    --platform managed `
    --region $Region `
    --update-env-vars "GOOGLE_CLIENT_ID=444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com" `
    --update-env-vars "DB_HOST=miano.h.filess.io" `
    --update-env-vars "DB_PORT=3305" `
    --update-env-vars "DB_USER=easyshiftsdb_danceshall" `
    --update-env-vars "DB_NAME=easyshiftsdb_danceshall" `
    --update-env-vars "DB_PASSWORD=a61d15d9b4f2671739338d1082cc7b75c0084e21" `
    --update-env-vars "REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com" `
    --update-env-vars "REDIS_PORT=12649" `
    --update-env-vars "REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa" `
    --update-env-vars "REDIS_DB=0" `
    --update-env-vars "SESSION_SECRET_KEY=K8mP9vN2xQ7wE5tR1yU6iO3pA8sD4fG9hJ2kL5nM7bV0cX1zQ6wE9rT3yU8iO5pA" `
    --update-env-vars "CSRF_SECRET_KEY=X9mN2bV5cQ8wE1rT4yU7iO0pA3sD6fG2hJ5kL8nM1bV4cX7zQ0wE3rT6yU9iO2pA" `
    --update-env-vars "ENVIRONMENT=production" `
    --update-env-vars "DEBUG=false" `
    --update-env-vars "HOST=0.0.0.0" `
    --update-env-vars "PORT=8080"

# Update frontend environment variables
Write-Host "🔧 Updating frontend environment variables..." -ForegroundColor Yellow

$BackendUrl = gcloud run services describe holi-timesheets-backend --platform managed --region $Region --format 'value(status.url)'
$WsUrl = ($BackendUrl -replace "https:", "wss:") + "/ws"

gcloud run services update holi-timesheets-frontend `
    --platform managed `
    --region $Region `
    --update-env-vars "REACT_APP_GOOGLE_CLIENT_ID=444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com" `
    --update-env-vars "REACT_APP_API_URL=$WsUrl" `
    --update-env-vars "REACT_APP_ENV=production"

# Get URLs
$FrontendUrl = gcloud run services describe holi-timesheets-frontend --platform managed --region $Region --format 'value(status.url)'

Write-Host "✅ Environment variables updated successfully!" -ForegroundColor Green
Write-Host "📱 Frontend URL: $FrontendUrl" -ForegroundColor Green
Write-Host "🔧 Backend URL: $BackendUrl" -ForegroundColor Green
Write-Host "🔌 WebSocket URL: $WsUrl" -ForegroundColor Green

# Test the backend
Write-Host "🧪 Testing backend health..." -ForegroundColor Yellow
Start-Sleep -Seconds 5  # Wait for deployment to complete

try {
    $response = Invoke-RestMethod -Uri "$BackendUrl/health" -Method GET -TimeoutSec 10
    Write-Host "✅ Backend health check passed!" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Backend health check failed. Checking basic connectivity..." -ForegroundColor Yellow
    try {
        $headers = Invoke-WebRequest -Uri $BackendUrl -Method HEAD -TimeoutSec 10
        Write-Host "✅ Backend is responding (Status: $($headers.StatusCode))" -ForegroundColor Green
    } catch {
        Write-Host "❌ Backend is not responding: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Cyan
Write-Host "1. Open: $FrontendUrl" -ForegroundColor Cyan
Write-Host "2. Test Google OAuth with the new Client ID" -ForegroundColor Cyan
Write-Host "3. Check WebSocket connections" -ForegroundColor Cyan
