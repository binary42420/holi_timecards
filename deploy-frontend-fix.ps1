# Deploy Frontend Fix for Google OAuth User Data

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

Write-Host "DEPLOYING FRONTEND FIX FOR GOOGLE OAUTH USER DATA" -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# Get backend URL
$backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)'
$BACKEND_WS_URL = $backendUrl -replace "https://", "wss://"
$BACKEND_WS_URL = "$BACKEND_WS_URL/ws"

Write-Host "Backend WebSocket URL: $BACKEND_WS_URL" -ForegroundColor Cyan

Write-Host "`nCritical fix applied:" -ForegroundColor Yellow
Write-Host "- Fixed GoogleSignIn component to pass userId and googleId to googleLogin" -ForegroundColor Green
Write-Host "- This ensures user data is properly stored in localStorage" -ForegroundColor Green
Write-Host "- Manager dashboard should now load data successfully" -ForegroundColor Green

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

Write-Host "`nBuilding frontend..." -ForegroundColor Yellow

Set-Location "app"
try {
    $env:REACT_APP_GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID
    $env:REACT_APP_API_URL = $BACKEND_WS_URL
    $env:REACT_APP_ENV = "production"
    
    docker build -t $frontendImage .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Frontend build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Frontend build successful!" -ForegroundColor Green
    
    Write-Host "Pushing frontend..." -ForegroundColor Yellow
    docker push $frontendImage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Frontend push failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Frontend push successful!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

Write-Host "`nDeploying frontend to Cloud Run..." -ForegroundColor Yellow

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

if ($LASTEXITCODE -eq 0) {
    $frontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)'
    
    Write-Host "`nFRONTEND FIX DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "===================================" -ForegroundColor Green
    
    Write-Host "`nURLs:" -ForegroundColor Cyan
    Write-Host "Frontend: $frontendUrl" -ForegroundColor White
    Write-Host "Backend:  $backendUrl" -ForegroundColor White
    
    Write-Host "`nFix Applied:" -ForegroundColor Cyan
    Write-Host "- GoogleSignIn now passes userId and googleId to googleLogin" -ForegroundColor Green
    Write-Host "- User data will be properly stored in localStorage" -ForegroundColor Green
    Write-Host "- Manager dashboard should load client companies and jobs" -ForegroundColor Green
    
    Write-Host "`nTesting Instructions:" -ForegroundColor Cyan
    Write-Host "1. Visit: $frontendUrl" -ForegroundColor White
    Write-Host "2. Clear browser cache and storage (Ctrl+Shift+R)" -ForegroundColor White
    Write-Host "3. Sign in with Google OAuth" -ForegroundColor White
    Write-Host "4. Navigate to manager-jobs page" -ForegroundColor White
    Write-Host "5. Should see client companies and jobs loading" -ForegroundColor White
    
    Write-Host "`nExpected Results:" -ForegroundColor Cyan
    Write-Host "- Google OAuth login stores complete user data" -ForegroundColor White
    Write-Host "- localStorage contains user data with userId and googleId" -ForegroundColor White
    Write-Host "- Manager dashboard loads client companies and jobs" -ForegroundColor White
    Write-Host "- No more 'User session not found' errors" -ForegroundColor White
    
} else {
    Write-Host "Frontend deployment failed!" -ForegroundColor Red
    exit 1
}
