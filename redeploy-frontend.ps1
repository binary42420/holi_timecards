# Redeploy frontend with correct WebSocket URL
# This script rebuilds and redeploys only the frontend with the fixed WebSocket URL

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

# Configuration
$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"
$BACKEND_URL = "wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws"

Write-Host "Redeploying Frontend with Correct WebSocket URL" -ForegroundColor Cyan
Write-Host "WebSocket URL: $BACKEND_URL" -ForegroundColor Yellow

# Generate new timestamp for the image
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

Write-Host "`nStep 1: Building Frontend Docker Image..." -ForegroundColor Yellow

# Build the frontend image
$buildCmd = "docker build -t `"$frontendImage`" ."
Write-Host "Running: $buildCmd" -ForegroundColor Gray

Set-Location "app"
try {
    Invoke-Expression $buildCmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Frontend build failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "Frontend image built successfully!" -ForegroundColor Green
} finally {
    Set-Location ".."
}

Write-Host "`nStep 2: Pushing Frontend Image to Artifact Registry..." -ForegroundColor Yellow

$pushCmd = "docker push `"$frontendImage`""
Write-Host "Running: $pushCmd" -ForegroundColor Gray

Invoke-Expression $pushCmd
if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend push failed!" -ForegroundColor Red
    exit 1
}
Write-Host "Frontend image pushed successfully!" -ForegroundColor Green

Write-Host "`nStep 3: Deploying Frontend to Cloud Run..." -ForegroundColor Yellow

$deployCmd = "gcloud run deploy $SERVICE_PREFIX-frontend " +
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
    "--set-env-vars `"REACT_APP_API_URL=$BACKEND_URL`" " +
    "--set-env-vars `"REACT_APP_ENV=production`""

Write-Host "Running frontend deployment..." -ForegroundColor Gray
Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Frontend deployed successfully!" -ForegroundColor Green
} else {
    Write-Host "Frontend deployment failed!" -ForegroundColor Red
    exit 1
}

# Get the final frontend URL
$frontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)' 2>$null

Write-Host "`nFrontend Redeployment Complete!" -ForegroundColor Cyan
Write-Host "`nUpdated URLs:" -ForegroundColor Cyan
Write-Host "Frontend: $frontendUrl" -ForegroundColor Green
Write-Host "Backend WebSocket: $BACKEND_URL" -ForegroundColor Green

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Clear your browser cache and refresh the page" -ForegroundColor White
Write-Host "2. Test the WebSocket connection" -ForegroundColor White
Write-Host "3. Verify Google OAuth login works" -ForegroundColor White

Write-Host "`nFrontend redeployment completed successfully!" -ForegroundColor Green
