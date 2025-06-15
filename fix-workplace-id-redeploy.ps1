# Fix workplace_id Issue and Redeploy Backend

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

Write-Host "FIXING WORKPLACE_ID ISSUE AND REDEPLOYING BACKEND" -ForegroundColor Red
Write-Host "Fixed: Removed non-existent workplace_id attribute from Google session creation" -ForegroundColor Green

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:$timestamp"

Write-Host "Building backend with workplace_id fix..." -ForegroundColor Yellow

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
    Write-Host "WORKPLACE_ID FIX DEPLOYED!" -ForegroundColor Green
    
    Write-Host "`nWhat was fixed:" -ForegroundColor Cyan
    Write-Host "- Removed non-existent workplace_id attribute from User model access" -ForegroundColor Green
    Write-Host "- Fixed Google session creation handler" -ForegroundColor Green
    Write-Host "- Google OAuth login should now work properly" -ForegroundColor Green
    
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "1. Test Google session creation in debug tool" -ForegroundColor White
    Write-Host "2. Try Google OAuth login in main app" -ForegroundColor White
    Write-Host "3. Navigate to manager-jobs page" -ForegroundColor White
    Write-Host "4. Should see job data without 'User session not found' errors" -ForegroundColor White
    
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}
