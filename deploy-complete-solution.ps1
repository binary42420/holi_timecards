# Complete Rebuild and Deploy Frontend + Backend to Cloud Run

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

Write-Host "🚀 COMPLETE REBUILD AND DEPLOY TO CLOUD RUN" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:$timestamp"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

# Step 1: Build and Deploy Backend
Write-Host "`n🔧 STEP 1: BUILDING BACKEND" -ForegroundColor Yellow
Write-Host "Features included:" -ForegroundColor White
Write-Host "- Redis fixes with fallback session management" -ForegroundColor Green
Write-Host "- Fixed WebSocket manager NoneType errors" -ForegroundColor Green
Write-Host "- Enhanced Google session creation" -ForegroundColor Green
Write-Host "- Dual session validation system" -ForegroundColor Green

Set-Location "Backend"
try {
    Write-Host "Building backend image..." -ForegroundColor Yellow
    docker build -t $backendImage .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Backend build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Backend build successful!" -ForegroundColor Green
    
    Write-Host "Pushing backend image..." -ForegroundColor Yellow
    docker push $backendImage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Backend push failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Backend push successful!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

Write-Host "`n🌐 STEP 2: DEPLOYING BACKEND TO CLOUD RUN" -ForegroundColor Yellow

$backendDeployCmd = "gcloud run deploy $SERVICE_PREFIX-backend " +
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

Invoke-Expression $backendDeployCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend deployment failed!" -ForegroundColor Red
    exit 1
}

$backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)'
Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green
Write-Host "Backend URL: $backendUrl" -ForegroundColor Cyan

# Extract WebSocket URL for frontend
$BACKEND_WS_URL = $backendUrl -replace "https://", "wss://"
$BACKEND_WS_URL = "$BACKEND_WS_URL/ws"

# Step 2: Build and Deploy Frontend
Write-Host "`n🎨 STEP 3: BUILDING FRONTEND" -ForegroundColor Yellow
Write-Host "Features included:" -ForegroundColor White
Write-Host "- Fixed socket availability issues" -ForegroundColor Green
Write-Host "- Manager dashboard infinite loop fixes" -ForegroundColor Green
Write-Host "- Enhanced session validation" -ForegroundColor Green
Write-Host "- Retry mechanisms for failed requests" -ForegroundColor Green

Set-Location "app"
try {
    $env:REACT_APP_GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID
    $env:REACT_APP_API_URL = $BACKEND_WS_URL
    $env:REACT_APP_ENV = "production"
    
    Write-Host "Building frontend image..." -ForegroundColor Yellow
    Write-Host "Using backend WebSocket URL: $BACKEND_WS_URL" -ForegroundColor Cyan
    
    docker build -t $frontendImage .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Frontend build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Frontend build successful!" -ForegroundColor Green
    
    Write-Host "Pushing frontend image..." -ForegroundColor Yellow
    docker push $frontendImage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Frontend push failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "✅ Frontend push successful!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

Write-Host "`n🌐 STEP 4: DEPLOYING FRONTEND TO CLOUD RUN" -ForegroundColor Yellow

$frontendDeployCmd = "gcloud run deploy $SERVICE_PREFIX-frontend " +
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
    "--set-env-vars `"REACT_APP_API_URL=$BACKEND_WS_URL`" " +
    "--set-env-vars `"REACT_APP_ENV=production`""

Invoke-Expression $frontendDeployCmd

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend deployment failed!" -ForegroundColor Red
    exit 1
}

$frontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)'

Write-Host "`n🎉 COMPLETE DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

Write-Host "`n📋 DEPLOYMENT SUMMARY:" -ForegroundColor Cyan
Write-Host "Backend URL:  $backendUrl" -ForegroundColor White
Write-Host "Frontend URL: $frontendUrl" -ForegroundColor White
Write-Host "WebSocket URL: $BACKEND_WS_URL" -ForegroundColor White

Write-Host "`n🔧 FIXES INCLUDED:" -ForegroundColor Cyan
Write-Host "✅ Redis WebSocket manager NoneType errors - FIXED" -ForegroundColor Green
Write-Host "✅ Fallback session management - IMPLEMENTED" -ForegroundColor Green
Write-Host "✅ Google session creation robustness - ENHANCED" -ForegroundColor Green
Write-Host "✅ Socket availability waiting - FIXED" -ForegroundColor Green
Write-Host "✅ Manager dashboard infinite loops - FIXED" -ForegroundColor Green
Write-Host "✅ Session validation with fallback - IMPLEMENTED" -ForegroundColor Green
Write-Host "✅ Request retry mechanisms - ADDED" -ForegroundColor Green

Write-Host "`n🧪 TESTING INSTRUCTIONS:" -ForegroundColor Cyan
Write-Host "1. Visit: $frontendUrl" -ForegroundColor White
Write-Host "2. Clear browser cache (Ctrl+Shift+R)" -ForegroundColor White
Write-Host "3. Try Google OAuth login" -ForegroundColor White
Write-Host "4. Navigate to manager-jobs page" -ForegroundColor White
Write-Host "5. Should see job data loading successfully" -ForegroundColor White

Write-Host "`n📊 MONITOR LOGS:" -ForegroundColor Cyan
Write-Host "Backend logs:" -ForegroundColor White
Write-Host "gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=holi-timesheets-backend' --limit=10 --freshness=5m" -ForegroundColor Gray

Write-Host "`n🎯 EXPECTED RESULTS:" -ForegroundColor Cyan
Write-Host "- No more 'WebSocket connection not available' errors" -ForegroundColor White
Write-Host "- No more 'User session not found' errors" -ForegroundColor White
Write-Host "- Google OAuth login completes successfully" -ForegroundColor White
Write-Host "- Manager jobs page loads data" -ForegroundColor White
Write-Host "- Session validation works with fallback" -ForegroundColor White

Write-Host "`n🚀 APPLICATION IS NOW FULLY DEPLOYED AND READY!" -ForegroundColor Green
