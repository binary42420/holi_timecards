# Fix Frontend Google Session Request Format

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"
$BACKEND_URL = "wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws"

Write-Host "🔧 FIXING FRONTEND GOOGLE SESSION REQUEST FORMAT" -ForegroundColor Red
Write-Host "The frontend was sending Google session data in wrong format" -ForegroundColor Yellow
Write-Host "Fixed: Wrapped user data in 'data' field as expected by backend" -ForegroundColor Green

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

Write-Host "Building frontend with Google session fix..." -ForegroundColor Yellow

Set-Location "app"
try {
    # Set environment variables
    $env:REACT_APP_GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID
    $env:REACT_APP_API_URL = $BACKEND_URL
    $env:REACT_APP_ENV = "production"
    
    # Build image
    docker build -t $frontendImage .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Build successful!" -ForegroundColor Green
    
    # Push image
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

# Deploy to Cloud Run
Write-Host "Deploying to Cloud Run..." -ForegroundColor Yellow

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

Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    
    $frontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)'
    
    Write-Host "Frontend URL: $frontendUrl" -ForegroundColor Green
    Write-Host "Backend WebSocket: $BACKEND_URL" -ForegroundColor Green
    
    Write-Host "FRONTEND GOOGLE SESSION FIX DEPLOYED!" -ForegroundColor Green
    Write-Host "Google session creation should now work properly!" -ForegroundColor Yellow
    
    Write-Host "`nWhat was fixed:" -ForegroundColor Cyan
    Write-Host "- Frontend now sends Google session data in correct format" -ForegroundColor Green
    Write-Host "- Backend will receive user data in 'data' field as expected" -ForegroundColor Green
    Write-Host "- Google OAuth login should create sessions successfully" -ForegroundColor Green
    
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "1. Clear browser cache (Ctrl+Shift+R)" -ForegroundColor White
    Write-Host "2. Try Google OAuth login again" -ForegroundColor White
    Write-Host "3. Navigate to manager-jobs page" -ForegroundColor White
    Write-Host "4. Should see 'Connected' and job data" -ForegroundColor White
    
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}
