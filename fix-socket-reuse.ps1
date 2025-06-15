# Fix Socket Reuse Issues and Redeploy

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"
$BACKEND_URL = "wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws"

Write-Host "FIXING SOCKET REUSE ISSUES" -ForegroundColor Red
Write-Host "Critical fix:" -ForegroundColor Yellow
Write-Host "- AuthContext now uses existing WebSocket instead of creating new ones" -ForegroundColor Green
Write-Host "- Prevents connection instability during Google session creation" -ForegroundColor Green
Write-Host "- Proper message handler management" -ForegroundColor Green
Write-Host "- Fixed response data structure handling" -ForegroundColor Green

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

Write-Host "Building frontend with socket reuse fixes..." -ForegroundColor Yellow

Set-Location "app"
try {
    $env:REACT_APP_GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID
    $env:REACT_APP_API_URL = $BACKEND_URL
    $env:REACT_APP_ENV = "production"
    
    docker build -t $frontendImage .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Build successful!" -ForegroundColor Green
    
    Write-Host "Pushing image..." -ForegroundColor Yellow
    docker push $frontendImage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Push failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Push successful!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow

$deployCmd = @"
gcloud run deploy $SERVICE_PREFIX-frontend --image "$frontendImage" --platform managed --region $Region --allow-unauthenticated --port 8080 --memory 512Mi --cpu 1 --concurrency 1000 --timeout 300 --max-instances 10 --set-env-vars "REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" --set-env-vars "REACT_APP_API_URL=$BACKEND_URL" --set-env-vars "REACT_APP_ENV=production"
"@

Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    
    $frontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)'
    
    Write-Host "Frontend URL: $frontendUrl" -ForegroundColor Green
    Write-Host "SOCKET REUSE FIXES DEPLOYED!" -ForegroundColor Green
    
    Write-Host "`nCritical fixes applied:" -ForegroundColor Cyan
    Write-Host "- AuthContext uses existing WebSocket connection" -ForegroundColor Green
    Write-Host "- No more creating new sockets during session creation" -ForegroundColor Green
    Write-Host "- Proper message handler restoration" -ForegroundColor Green
    Write-Host "- Fixed response data structure (response.data.success)" -ForegroundColor Green
    Write-Host "- Increased timeout to 15 seconds" -ForegroundColor Green
    
    Write-Host "`nExpected Results:" -ForegroundColor Cyan
    Write-Host "- No more WebSocket connection instability" -ForegroundColor White
    Write-Host "- Google session creation should succeed" -ForegroundColor White
    Write-Host "- No more 'Closing WebSocket connection on cleanup' during auth" -ForegroundColor White
    Write-Host "- Manager jobs page should load properly" -ForegroundColor White
    
    Write-Host "`nAlso update local container:" -ForegroundColor Yellow
    Write-Host "Run: docker stop holi-timecards-app-local && docker rm holi-timecards-app-local" -ForegroundColor White
    Write-Host "Then: powershell -ExecutionPolicy Bypass -File run-local-with-env.ps1" -ForegroundColor White
    
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}
