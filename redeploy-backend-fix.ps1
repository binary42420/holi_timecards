# Redeploy Backend with Google Session Fix

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

Write-Host "🔧 Redeploying Backend with Google Session Fix" -ForegroundColor Cyan

# Database Configuration
$DB_CONFIG = @{
    HOST = "miano.h.filess.io"
    PORT = "3305"
    USER = "easyshiftsdb_danceshall"
    NAME = "easyshiftsdb_danceshall"
    PASSWORD = "a61d15d9b4f2671739338d1082cc7b75c0084e21"
}

# Redis Configuration
$REDIS_CONFIG = @{
    HOST = "redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com"
    PORT = "12649"
    PASSWORD = "AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa"
    DB = "0"
}

# Security Keys
$SECURITY_CONFIG = @{
    SESSION_SECRET = "K8mP9vN2xQ7wE5tR1yU6iO3pA8sD4fG9hJ2kL5nM7bV0cX1zQ6wE9rT3yU8iO5pA"
    CSRF_SECRET = "X9mN2bV5cQ8wE1rT4yU7iO0pA3sD6fG2hJ5kL8nM1bV4cX7zQ0wE3rT6yU9iO2pA"
}

Write-Host "Building backend with Google session fix..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:$timestamp"

Set-Location "Backend"
try {
    # Build image
    docker build -t $backendImage .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Backend build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Backend build successful!" -ForegroundColor Green
    
    # Push image
    Write-Host "Pushing backend image..." -ForegroundColor Yellow
    docker push $backendImage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Backend push failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Backend push successful!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

# Deploy to Cloud Run
Write-Host "Deploying backend to Cloud Run..." -ForegroundColor Yellow

$deployCmd = @"
gcloud run deploy $SERVICE_PREFIX-backend --image "$backendImage" --platform managed --region $Region --allow-unauthenticated --port 8080 --memory 1Gi --cpu 1 --concurrency 100 --timeout 300 --max-instances 10 --set-env-vars "GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" --set-env-vars "DB_HOST=$($DB_CONFIG.HOST)" --set-env-vars "DB_PORT=$($DB_CONFIG.PORT)" --set-env-vars "DB_USER=$($DB_CONFIG.USER)" --set-env-vars "DB_NAME=$($DB_CONFIG.NAME)" --set-env-vars "DB_PASSWORD=$($DB_CONFIG.PASSWORD)" --set-env-vars "REDIS_HOST=$($REDIS_CONFIG.HOST)" --set-env-vars "REDIS_PORT=$($REDIS_CONFIG.PORT)" --set-env-vars "REDIS_PASSWORD=$($REDIS_CONFIG.PASSWORD)" --set-env-vars "REDIS_DB=$($REDIS_CONFIG.DB)" --set-env-vars "SESSION_SECRET_KEY=$($SECURITY_CONFIG.SESSION_SECRET)" --set-env-vars "CSRF_SECRET_KEY=$($SECURITY_CONFIG.CSRF_SECRET)" --set-env-vars "ENVIRONMENT=production"
"@

Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backend deployment successful!" -ForegroundColor Green
    
    $backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)'
    
    Write-Host "Backend URL: $backendUrl" -ForegroundColor Green
    Write-Host "WebSocket URL: $($backendUrl -replace 'https:', 'wss:')/ws" -ForegroundColor Green
    
    Write-Host "BACKEND FIX DEPLOYED!" -ForegroundColor Green
    Write-Host "Google session issues should now be resolved!" -ForegroundColor Yellow
    
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "1. Clear browser cache and refresh the app" -ForegroundColor White
    Write-Host "2. Try Google OAuth login again" -ForegroundColor White
    Write-Host "3. Check browser console for session creation logs" -ForegroundColor White
    Write-Host "4. Test manager-jobs page access" -ForegroundColor White
    
} else {
    Write-Host "Backend deployment failed!" -ForegroundColor Red
    exit 1
}
