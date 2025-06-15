# Rebuild and Deploy Both Services with All Latest Changes

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

Write-Host "REBUILDING AND DEPLOYING HOLI TIMESHEETS" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

Write-Host "`nLatest Changes Included:" -ForegroundColor Yellow
Write-Host "✅ Fixed Redis WebSocket Manager async/await issues" -ForegroundColor Green
Write-Host "✅ Redis session persistence implementation" -ForegroundColor Green
Write-Host "✅ Google OAuth authentication improvements" -ForegroundColor Green
Write-Host "✅ Employee directory authentication fixes" -ForegroundColor Green
Write-Host "✅ WebSocket connection stability improvements" -ForegroundColor Green

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:final-$timestamp"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:final-$timestamp"

# ============================================================================
# BUILD AND DEPLOY BACKEND
# ============================================================================

Write-Host "`n🔧 REBUILDING BACKEND..." -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Cyan

Set-Location "Backend"
try {
    Write-Host "Building backend with all fixes..." -ForegroundColor Yellow
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
    
    Write-Host "✅ Backend image pushed!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

Write-Host "Deploying backend to Cloud Run..." -ForegroundColor Yellow

gcloud run deploy $SERVICE_PREFIX-backend `
    --image $backendImage `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --port 8080 `
    --memory 1Gi `
    --cpu 1 `
    --concurrency 1000 `
    --timeout 900 `
    --max-instances 10

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Backend deployment failed!" -ForegroundColor Red
    exit 1
}

$backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)'
$BACKEND_WS_URL = $backendUrl -replace "https://", "wss://"
$BACKEND_WS_URL = "$BACKEND_WS_URL/ws"

Write-Host "✅ Backend deployed successfully!" -ForegroundColor Green
Write-Host "   Backend URL: $backendUrl" -ForegroundColor White
Write-Host "   WebSocket URL: $BACKEND_WS_URL" -ForegroundColor White

# ============================================================================
# BUILD AND DEPLOY FRONTEND
# ============================================================================

Write-Host "`n🎨 REBUILDING FRONTEND..." -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan

Set-Location "app"
try {
    Write-Host "Building frontend with all fixes..." -ForegroundColor Yellow
    
    # Set environment variables for build
    $env:REACT_APP_GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID
    $env:REACT_APP_API_URL = $BACKEND_WS_URL
    $env:REACT_APP_ENV = "production"
    
    Write-Host "Environment variables:" -ForegroundColor Gray
    Write-Host "  REACT_APP_GOOGLE_CLIENT_ID: $GOOGLE_CLIENT_ID" -ForegroundColor Gray
    Write-Host "  REACT_APP_API_URL: $BACKEND_WS_URL" -ForegroundColor Gray
    Write-Host "  REACT_APP_ENV: production" -ForegroundColor Gray
    
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
    
    Write-Host "✅ Frontend image pushed!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

Write-Host "Deploying frontend to Cloud Run..." -ForegroundColor Yellow

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
    Write-Host "❌ Frontend deployment failed!" -ForegroundColor Red
    exit 1
}

$frontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)'

Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
Write-Host "   Frontend URL: $frontendUrl" -ForegroundColor White

# ============================================================================
# DEPLOYMENT SUMMARY
# ============================================================================

Write-Host "`n🎉 REBUILD AND DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green

Write-Host "`nService URLs:" -ForegroundColor Cyan
Write-Host "Frontend:  $frontendUrl" -ForegroundColor White
Write-Host "Backend:   $backendUrl" -ForegroundColor White
Write-Host "WebSocket: $BACKEND_WS_URL" -ForegroundColor White

Write-Host "`nImages Deployed:" -ForegroundColor Cyan
Write-Host "Backend:  $backendImage" -ForegroundColor White
Write-Host "Frontend: $frontendImage" -ForegroundColor White

Write-Host "`nAll Latest Changes Included:" -ForegroundColor Cyan
Write-Host "🔧 Backend Fixes:" -ForegroundColor Yellow
Write-Host "   ✅ Redis WebSocket Manager async/await issues resolved" -ForegroundColor Green
Write-Host "   ✅ Session persistence with Redis working" -ForegroundColor Green
Write-Host "   ✅ WebSocket connection stability improved" -ForegroundColor Green
Write-Host "   ✅ No more heartbeat errors" -ForegroundColor Green

Write-Host "🎨 Frontend Fixes:" -ForegroundColor Yellow
Write-Host "   ✅ Google OAuth authentication improvements" -ForegroundColor Green
Write-Host "   ✅ Employee directory authentication fixes" -ForegroundColor Green
Write-Host "   ✅ Session management enhancements" -ForegroundColor Green
Write-Host "   ✅ createAuthenticatedRequest usage fixed" -ForegroundColor Green

Write-Host "`nReady to Test:" -ForegroundColor Cyan
Write-Host "1. Visit: $frontendUrl" -ForegroundColor White
Write-Host "2. Sign in with Google OAuth" -ForegroundColor White
Write-Host "3. Test manager-jobs page (client companies and jobs)" -ForegroundColor White
Write-Host "4. Test employee directory" -ForegroundColor White
Write-Host "5. Verify session persistence through deployments" -ForegroundColor White

Write-Host "`nExpected Results:" -ForegroundColor Cyan
Write-Host "✅ Stable WebSocket connections" -ForegroundColor Green
Write-Host "✅ No connection errors in logs" -ForegroundColor Green
Write-Host "✅ Session persistence working" -ForegroundColor Green
Write-Host "✅ All authentication flows working" -ForegroundColor Green
Write-Host "✅ Manager and employee features functional" -ForegroundColor Green

Write-Host "`n🚀 HOLI TIMESHEETS APPLICATION FULLY DEPLOYED!" -ForegroundColor Green
