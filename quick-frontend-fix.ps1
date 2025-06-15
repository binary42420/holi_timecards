# Quick Frontend Fix - Rebuild with Correct WebSocket URL

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"
$CORRECT_BACKEND_URL = "wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws"

Write-Host "EMERGENCY FRONTEND FIX" -ForegroundColor Red
Write-Host "Fixing placeholder URL issue" -ForegroundColor Yellow

# Update env-config.js with correct URL
Write-Host "Updating env-config.js..." -ForegroundColor Yellow

$envConfig = @"
// Runtime environment configuration for HOLI Timesheets
const isLocalDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
const forceLocalMode = false;

window._env_ = {
  REACT_APP_GOOGLE_CLIENT_ID: "$GOOGLE_CLIENT_ID",
  REACT_APP_API_URL: (isLocalDevelopment || forceLocalMode)
    ? "ws://localhost:8080/ws"
    : "$CORRECT_BACKEND_URL",
  REACT_APP_ENV: (isLocalDevelopment || forceLocalMode) ? "development" : "production"
};

console.log('env-config.js loaded:', window._env_);
"@

$envConfig | Out-File -FilePath "app/public/env-config.js" -Encoding UTF8
Write-Host "Updated env-config.js" -ForegroundColor Green

# Update .env.production
Write-Host "Updating .env.production..." -ForegroundColor Yellow

$envProd = @"
REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID
REACT_APP_API_URL=$CORRECT_BACKEND_URL
REACT_APP_ENV=production
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
"@

$envProd | Out-File -FilePath "app/.env.production" -Encoding UTF8
Write-Host "Updated .env.production" -ForegroundColor Green

# Build and deploy
Write-Host "Building frontend..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

Set-Location "app"
try {
    # Set environment variables
    $env:REACT_APP_GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID
    $env:REACT_APP_API_URL = $CORRECT_BACKEND_URL
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

$deployCmd = @"
gcloud run deploy $SERVICE_PREFIX-frontend --image "$frontendImage" --platform managed --region $Region --allow-unauthenticated --port 8080 --memory 512Mi --cpu 1 --concurrency 1000 --timeout 300 --max-instances 10 --set-env-vars "REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" --set-env-vars "REACT_APP_API_URL=$CORRECT_BACKEND_URL" --set-env-vars "REACT_APP_ENV=production"
"@

Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
    
    $frontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)'
    
    Write-Host "Frontend URL: $frontendUrl" -ForegroundColor Green
    Write-Host "Backend WebSocket: $CORRECT_BACKEND_URL" -ForegroundColor Green
    
    Write-Host "EMERGENCY FIX COMPLETE!" -ForegroundColor Green
    Write-Host "Clear browser cache and try again!" -ForegroundColor Yellow
    
} else {
    Write-Host "Deployment failed!" -ForegroundColor Red
    exit 1
}
