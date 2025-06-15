# Rebuild and Deploy Both Frontend and Backend

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

Write-Host "REBUILDING AND DEPLOYING BOTH SERVICES" -ForegroundColor Cyan
Write-Host "=======================================" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:$timestamp"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

# Deploy Backend First
Write-Host "`nSTEP 1: BACKEND DEPLOYMENT" -ForegroundColor Yellow
Write-Host "Building backend..." -ForegroundColor White

Set-Location "Backend"
docker build -t $backendImage .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend build failed!" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Write-Host "Pushing backend..." -ForegroundColor White
docker push $backendImage
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend push failed!" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Set-Location ".."

Write-Host "Deploying backend to Cloud Run..." -ForegroundColor White
gcloud run deploy $SERVICE_PREFIX-backend `
    --image $backendImage `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8080 `
    --memory 1Gi `
    --cpu 1 `
    --concurrency 100 `
    --timeout 300 `
    --max-instances 10 `
    --set-env-vars "GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" `
    --set-env-vars "DB_HOST=miano.h.filess.io" `
    --set-env-vars "DB_PORT=3305" `
    --set-env-vars "DB_USER=easyshiftsdb_danceshall" `
    --set-env-vars "DB_NAME=easyshiftsdb_danceshall" `
    --set-env-vars "DB_PASSWORD=a61d15d9b4f2671739338d1082cc7b75c0084e21" `
    --set-env-vars "REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com" `
    --set-env-vars "REDIS_PORT=12649" `
    --set-env-vars "REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa" `
    --set-env-vars "REDIS_DB=0" `
    --set-env-vars "SESSION_SECRET_KEY=K8mP9vN2xQ7wE5tR1yU6iO3pA8sD4fG9hJ2kL5nM7bV0cX1zQ6wE9rT3yU8iO5pA" `
    --set-env-vars "CSRF_SECRET_KEY=X9mN2bV5cQ8wE1rT4yU7iO0pA3sD6fG2hJ5kL8nM1bV4cX7zQ0wE3rT6yU9iO2pA" `
    --set-env-vars "ENVIRONMENT=production"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend deployment failed!" -ForegroundColor Red
    exit 1
}

$backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)'
$BACKEND_WS_URL = $backendUrl -replace "https://", "wss://"
$BACKEND_WS_URL = "$BACKEND_WS_URL/ws"

Write-Host "Backend deployed successfully!" -ForegroundColor Green
Write-Host "Backend URL: $backendUrl" -ForegroundColor Cyan
Write-Host "WebSocket URL: $BACKEND_WS_URL" -ForegroundColor Cyan

# Deploy Frontend
Write-Host "`nSTEP 2: FRONTEND DEPLOYMENT" -ForegroundColor Yellow
Write-Host "Building frontend..." -ForegroundColor White

Set-Location "app"

$env:REACT_APP_GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID
$env:REACT_APP_API_URL = $BACKEND_WS_URL
$env:REACT_APP_ENV = "production"

docker build -t $frontendImage .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend build failed!" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Write-Host "Pushing frontend..." -ForegroundColor White
docker push $frontendImage
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend push failed!" -ForegroundColor Red
    Set-Location ".."
    exit 1
}

Set-Location ".."

Write-Host "Deploying frontend to Cloud Run..." -ForegroundColor White
gcloud run deploy $SERVICE_PREFIX-frontend `
    --image $frontendImage `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8080 `
    --memory 512Mi `
    --cpu 1 `
    --concurrency 1000 `
    --timeout 300 `
    --max-instances 10 `
    --set-env-vars "REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" `
    --set-env-vars "REACT_APP_API_URL=$BACKEND_WS_URL" `
    --set-env-vars "REACT_APP_ENV=production"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend deployment failed!" -ForegroundColor Red
    exit 1
}

$frontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)'

Write-Host "`nDEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green

Write-Host "`nURLs:" -ForegroundColor Cyan
Write-Host "Frontend: $frontendUrl" -ForegroundColor White
Write-Host "Backend:  $backendUrl" -ForegroundColor White
Write-Host "WebSocket: $BACKEND_WS_URL" -ForegroundColor White

Write-Host "`nFixes Included:" -ForegroundColor Cyan
Write-Host "- Redis WebSocket manager fixes" -ForegroundColor Green
Write-Host "- Fallback session management" -ForegroundColor Green
Write-Host "- Socket availability fixes" -ForegroundColor Green
Write-Host "- Manager dashboard fixes" -ForegroundColor Green
Write-Host "- Enhanced error handling" -ForegroundColor Green

Write-Host "`nTest Instructions:" -ForegroundColor Cyan
Write-Host "1. Visit: $frontendUrl" -ForegroundColor White
Write-Host "2. Clear browser cache" -ForegroundColor White
Write-Host "3. Try Google OAuth login" -ForegroundColor White
Write-Host "4. Navigate to manager-jobs page" -ForegroundColor White
Write-Host "5. Should see job data loading" -ForegroundColor White

Write-Host "`nMonitor logs:" -ForegroundColor Cyan
Write-Host "gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=holi-timesheets-backend' --limit=10 --freshness=5m" -ForegroundColor Gray
