# Run Local Container with Correct Environment Variables

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$BACKEND_URL = "wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws"

Write-Host "STOPPING EXISTING CONTAINER AND RUNNING WITH CORRECT ENVIRONMENT" -ForegroundColor Red

# Stop and remove existing container
Write-Host "Stopping existing container..." -ForegroundColor Yellow
docker stop holi-timecards-app-local 2>$null
docker rm holi-timecards-app-local 2>$null

Write-Host "Building fresh local image..." -ForegroundColor Yellow
Set-Location "app"
try {
    # Build with environment variables
    $env:REACT_APP_GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID
    $env:REACT_APP_API_URL = $BACKEND_URL
    $env:REACT_APP_ENV = "production"
    
    docker build -t holi-timecards-app:local .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Build successful!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

Write-Host "Running container with correct environment variables..." -ForegroundColor Yellow

# Run container with environment variables
docker run -d `
    --name holi-timecards-app-local `
    -p 3000:8080 `
    -e "REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" `
    -e "REACT_APP_API_URL=$BACKEND_URL" `
    -e "REACT_APP_ENV=production" `
    holi-timecards-app:local

if ($LASTEXITCODE -eq 0) {
    Write-Host "Container started successfully!" -ForegroundColor Green
    Write-Host "Local URL: http://localhost:3000" -ForegroundColor Green
    Write-Host "Environment configured:" -ForegroundColor Cyan
    Write-Host "- GOOGLE_CLIENT_ID: $GOOGLE_CLIENT_ID" -ForegroundColor White
    Write-Host "- API_URL: $BACKEND_URL" -ForegroundColor White
    Write-Host "- ENV: production" -ForegroundColor White
    
    Write-Host "`nWait 10 seconds for container to start, then test:" -ForegroundColor Yellow
    Write-Host "1. Visit http://localhost:3000" -ForegroundColor White
    Write-Host "2. Check browser console for correct environment variables" -ForegroundColor White
    Write-Host "3. Try Google OAuth login" -ForegroundColor White
    Write-Host "4. Navigate to manager-jobs page" -ForegroundColor White
    
    # Show container logs
    Write-Host "`nContainer logs:" -ForegroundColor Cyan
    Start-Sleep -Seconds 3
    docker logs holi-timecards-app-local --tail 20
    
} else {
    Write-Host "Failed to start container!" -ForegroundColor Red
    exit 1
}
