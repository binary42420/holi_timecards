# Fix WebSocket Lifecycle Issues and Redeploy Frontend

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"
$BACKEND_URL = "wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws"

Write-Host "FIXING WEBSOCKET LIFECYCLE ISSUES" -ForegroundColor Red
Write-Host "Fixed issues:" -ForegroundColor Yellow
Write-Host "- Prevented multiple simultaneous WebSocket connections" -ForegroundColor Green
Write-Host "- Added connection state tracking to prevent race conditions" -ForegroundColor Green
Write-Host "- Improved React component lifecycle handling" -ForegroundColor Green
Write-Host "- Fixed connection cleanup during authentication flows" -ForegroundColor Green

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

Write-Host "Building frontend with WebSocket lifecycle fixes..." -ForegroundColor Yellow

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
    Write-Host "WEBSOCKET LIFECYCLE FIXES DEPLOYED!" -ForegroundColor Green
    
    Write-Host "`nWhat was fixed:" -ForegroundColor Cyan
    Write-Host "- Multiple simultaneous WebSocket connections prevented" -ForegroundColor Green
    Write-Host "- Connection state tracking added (isConnecting flag)" -ForegroundColor Green
    Write-Host "- React component lifecycle properly handled" -ForegroundColor Green
    Write-Host "- Connection cleanup during authentication fixed" -ForegroundColor Green
    Write-Host "- Race conditions in connection management eliminated" -ForegroundColor Green
    
    Write-Host "`nExpected Results:" -ForegroundColor Cyan
    Write-Host "- No more rapid connection/disconnection cycles" -ForegroundColor White
    Write-Host "- Stable WebSocket connection during authentication" -ForegroundColor White
    Write-Host "- Google OAuth should complete without timeouts" -ForegroundColor White
    Write-Host "- Manager jobs page should load properly" -ForegroundColor White
    
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "1. Clear browser cache completely (Ctrl+Shift+R)" -ForegroundColor White
    Write-Host "2. Try Google OAuth login" -ForegroundColor White
    Write-Host "3. Should see stable connection without rapid reconnects" -ForegroundColor White
    Write-Host "4. Navigate to manager-jobs page and verify it works" -ForegroundColor White
    
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}
