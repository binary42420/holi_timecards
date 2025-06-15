# Simple retry deployment script for HOLI Timesheets
# Fixes the Cloud Run deployment with corrected environment variables

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

# Configuration
$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"

# Use the existing built images
$backendImage = "us-central1-docker.pkg.dev/holitimecards/holi-timesheets-repo/holi-timesheets-backend:20250614-200324"
$frontendImage = "us-central1-docker.pkg.dev/holitimecards/holi-timesheets-repo/holi-timesheets-frontend:20250614-200324"

Write-Host "Retrying HOLI Timesheets Deployment with Fixed Environment Variables" -ForegroundColor Cyan

# Deploy Backend (without reserved PORT and HOST variables)
Write-Host "`nDeploying Backend Service..." -ForegroundColor Yellow

$backendCmd = "gcloud run deploy $SERVICE_PREFIX-backend " +
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

Write-Host "Running backend deployment..." -ForegroundColor Gray
Invoke-Expression $backendCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backend deployed successfully!" -ForegroundColor Green
} else {
    Write-Host "Backend deployment failed!" -ForegroundColor Red
    exit 1
}

# Get backend URL
$backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)' 2>$null
if ($backendUrl) {
    $websocketUrl = ($backendUrl -replace "https:", "wss:") + "/ws"
    Write-Host "Backend URL: $backendUrl" -ForegroundColor Green
    Write-Host "WebSocket URL: $websocketUrl" -ForegroundColor Green
} else {
    Write-Host "Could not retrieve backend URL" -ForegroundColor Yellow
    $websocketUrl = "wss://holi-timesheets-backend-placeholder.run.app/ws"
}

# Deploy Frontend (without reserved PORT variable)
Write-Host "`nDeploying Frontend Service..." -ForegroundColor Yellow

$frontendCmd = "gcloud run deploy $SERVICE_PREFIX-frontend " +
    "--image `"$frontendImage`" " +
    "--platform managed " +
    "--region $Region " +
    "--allow-unauthenticated " +
    "--port 8080 " +
    "--memory 512Mi " +
    "--cpu 1 " +
    "--concurrency 1000 " +
    "--timeout 300 " +
    "--max-instances 10 " +
    "--set-env-vars `"REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID`" " +
    "--set-env-vars `"REACT_APP_API_URL=$websocketUrl`" " +
    "--set-env-vars `"REACT_APP_ENV=production`""

Write-Host "Running frontend deployment..." -ForegroundColor Gray
Invoke-Expression $frontendCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Frontend deployed successfully!" -ForegroundColor Green
} else {
    Write-Host "Frontend deployment failed!" -ForegroundColor Red
    exit 1
}

# Final Summary
Write-Host "`nDeployment Complete!" -ForegroundColor Cyan

$finalBackendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)' 2>$null
$finalFrontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)' 2>$null
$finalWebsocketUrl = ($finalBackendUrl -replace "https:", "wss:") + "/ws"

Write-Host "`nDeployment Summary:" -ForegroundColor Cyan
Write-Host "Project ID: $ProjectId" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White

if ($finalFrontendUrl) {
    Write-Host "`nApplication URLs:" -ForegroundColor Cyan
    Write-Host "Frontend: $finalFrontendUrl" -ForegroundColor Green
}

if ($finalBackendUrl) {
    Write-Host "Backend: $finalBackendUrl" -ForegroundColor Green
    Write-Host "WebSocket: $finalWebsocketUrl" -ForegroundColor Green
    Write-Host "Health Check: $finalBackendUrl/health" -ForegroundColor Green
}

Write-Host "`nIssues Fixed:" -ForegroundColor Cyan
Write-Host "- Removed reserved PORT environment variable" -ForegroundColor Green
Write-Host "- Removed reserved HOST environment variable" -ForegroundColor Green
Write-Host "- Fixed Dockerfile casing (FROM ... AS)" -ForegroundColor Green

Write-Host "`nHOLI Timesheets deployment completed successfully!" -ForegroundColor Green
