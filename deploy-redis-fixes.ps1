# Deploy Redis Fixes and Fallback Session Management

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

Write-Host "DEPLOYING REDIS FIXES AND FALLBACK SESSION MANAGEMENT" -ForegroundColor Red
Write-Host "Critical fixes applied:" -ForegroundColor Yellow
Write-Host "- Fixed Redis WebSocket manager 'NoneType' errors" -ForegroundColor Green
Write-Host "- Added fallback in-memory session management" -ForegroundColor Green
Write-Host "- Modified Google session creation to use fallback" -ForegroundColor Green
Write-Host "- Updated main request handler to use fallback sessions" -ForegroundColor Green
Write-Host "- Added Redis connection validation" -ForegroundColor Green

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:$timestamp"

Write-Host "Building backend with Redis fixes..." -ForegroundColor Yellow

Set-Location "Backend"
try {
    docker build -t $backendImage .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Build successful!" -ForegroundColor Green
    
    Write-Host "Pushing image..." -ForegroundColor Yellow
    docker push $backendImage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Push failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Push successful!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow

$deployCmd = "gcloud run deploy $SERVICE_PREFIX-backend " +
    "--image `"$backendImage`" " +
    "--platform managed " +
    "--region $Region " +
    "--allow-unauthenticated " +
    "--port 8080 " +
    "--memory 1Gi " +
    "--cpu 1 " +
    "--concurrency 100 " +
    "--timeout 300 " +
    "--max-instances 10 " +
    "--set-env-vars `"GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID`" " +
    "--set-env-vars `"DB_HOST=miano.h.filess.io`" " +
    "--set-env-vars `"DB_PORT=3305`" " +
    "--set-env-vars `"DB_USER=easyshiftsdb_danceshall`" " +
    "--set-env-vars `"DB_NAME=easyshiftsdb_danceshall`" " +
    "--set-env-vars `"DB_PASSWORD=a61d15d9b4f2671739338d1082cc7b75c0084e21`" " +
    "--set-env-vars `"REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com`" " +
    "--set-env-vars `"REDIS_PORT=12649`" " +
    "--set-env-vars `"REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa`" " +
    "--set-env-vars `"REDIS_DB=0`" " +
    "--set-env-vars `"SESSION_SECRET_KEY=K8mP9vN2xQ7wE5tR1yU6iO3pA8sD4fG9hJ2kL5nM7bV0cX1zQ6wE9rT3yU8iO5pA`" " +
    "--set-env-vars `"CSRF_SECRET_KEY=X9mN2bV5cQ8wE1rT4yU7iO0pA3sD6fG2hJ5kL8nM1bV4cX7zQ0wE3rT6yU9iO2pA`" " +
    "--set-env-vars `"ENVIRONMENT=production`""

Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    
    $backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)'
    
    Write-Host "Backend URL: $backendUrl" -ForegroundColor Green
    Write-Host "REDIS FIXES AND FALLBACK SESSION MANAGEMENT DEPLOYED!" -ForegroundColor Green
    
    Write-Host "`nCritical fixes applied:" -ForegroundColor Cyan
    Write-Host "1. Redis WebSocket Manager - Fixed NoneType errors" -ForegroundColor Green
    Write-Host "2. Fallback Session Manager - In-memory sessions when Redis fails" -ForegroundColor Green
    Write-Host "3. Google Session Creation - Uses fallback when Redis unavailable" -ForegroundColor Green
    Write-Host "4. Main Request Handler - Validates sessions with fallback" -ForegroundColor Green
    Write-Host "5. Connection Validation - Proper Redis connection checking" -ForegroundColor Green
    
    Write-Host "`nExpected Results:" -ForegroundColor Cyan
    Write-Host "- No more Redis WebSocket manager errors" -ForegroundColor White
    Write-Host "- Sessions work even when Redis is unavailable" -ForegroundColor White
    Write-Host "- Google session creation succeeds consistently" -ForegroundColor White
    Write-Host "- Session validation works with fallback" -ForegroundColor White
    Write-Host "- 'current_session: None' errors should be resolved" -ForegroundColor White
    
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "1. Test Google OAuth login" -ForegroundColor White
    Write-Host "2. Check server logs for session validation" -ForegroundColor White
    Write-Host "3. Navigate to manager-jobs page" -ForegroundColor White
    Write-Host "4. Should see job data loading successfully" -ForegroundColor White
    
    Write-Host "`nMonitor logs with:" -ForegroundColor Yellow
    Write-Host "gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=holi-timesheets-backend' --limit=10 --freshness=5m" -ForegroundColor White
    
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}
