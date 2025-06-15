# Deploy Persistent Session Management System (Simple Version)

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

Write-Host "DEPLOYING PERSISTENT SESSION MANAGEMENT SYSTEM" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

Write-Host "`nPersistent Session Features:" -ForegroundColor Yellow
Write-Host "- Database-backed session storage" -ForegroundColor Green
Write-Host "- Sessions survive deployments and restarts" -ForegroundColor Green
Write-Host "- Automatic session cleanup (every 30 minutes)" -ForegroundColor Green
Write-Host "- Multi-layer session management (Database -> Redis -> Memory)" -ForegroundColor Green
Write-Host "- Session restoration on server startup" -ForegroundColor Green
Write-Host "- Enhanced Google OAuth session persistence" -ForegroundColor Green

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:$timestamp"

Write-Host "`nBuilding backend with persistent sessions..." -ForegroundColor Yellow

Set-Location "Backend"
try {
    docker build -t $backendImage .
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Backend build failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Backend build successful!" -ForegroundColor Green
    
    Write-Host "Pushing backend..." -ForegroundColor Yellow
    docker push $backendImage
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Backend push failed!" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "Backend push successful!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

Write-Host "`nDeploying backend to Cloud Run..." -ForegroundColor Yellow

# Deploy backend with basic environment variables (no secrets for now)
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
    --max-instances 10 `
    --set-env-vars "SESSION_TIMEOUT=604800" `
    --set-env-vars "ENABLE_PERSISTENT_SESSIONS=true" `
    --set-env-vars "SESSION_CLEANUP_INTERVAL=1800"

if ($LASTEXITCODE -eq 0) {
    $backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)'
    
    Write-Host "`nPERSISTENT SESSION SYSTEM DEPLOYED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "=================================================" -ForegroundColor Green
    
    Write-Host "`nBackend URL: $backendUrl" -ForegroundColor White
    
    Write-Host "`nPersistent Session Features Deployed:" -ForegroundColor Cyan
    Write-Host "- Database Session Storage:" -ForegroundColor Green
    Write-Host "  * user_sessions table for persistent storage" -ForegroundColor White
    Write-Host "  * Sessions survive all deployments and restarts" -ForegroundColor White
    Write-Host "  * 7-day session expiration (configurable)" -ForegroundColor White
    
    Write-Host "- Multi-Layer Session Management:" -ForegroundColor Green
    Write-Host "  * Primary: Database (persistent)" -ForegroundColor White
    Write-Host "  * Secondary: Redis (cache)" -ForegroundColor White
    Write-Host "  * Tertiary: Memory (fallback)" -ForegroundColor White
    
    Write-Host "- Automatic Session Cleanup:" -ForegroundColor Green
    Write-Host "  * Background task runs every 30 minutes" -ForegroundColor White
    Write-Host "  * Removes expired sessions from database" -ForegroundColor White
    Write-Host "  * Provides session statistics" -ForegroundColor White
    
    Write-Host "- Enhanced Google OAuth:" -ForegroundColor Green
    Write-Host "  * Google sessions persist through deployments" -ForegroundColor White
    Write-Host "  * Automatic session restoration" -ForegroundColor White
    Write-Host "  * Improved user experience" -ForegroundColor White
    
    Write-Host "- Session Restoration:" -ForegroundColor Green
    Write-Host "  * Server loads active sessions on startup" -ForegroundColor White
    Write-Host "  * WebSocket connections restore sessions automatically" -ForegroundColor White
    Write-Host "  * No user re-authentication required" -ForegroundColor White
    
    Write-Host "`nDatabase Migration:" -ForegroundColor Cyan
    Write-Host "The user_sessions table will be created automatically when:" -ForegroundColor White
    Write-Host "1. The first user logs in after deployment" -ForegroundColor White
    Write-Host "2. The persistent session manager initializes" -ForegroundColor White
    Write-Host "3. If table doesn't exist, it will be created on-demand" -ForegroundColor White
    
    Write-Host "`nTesting Instructions:" -ForegroundColor Cyan
    Write-Host "1. Visit the frontend and log in with Google OAuth" -ForegroundColor White
    Write-Host "2. Navigate around the application (manager-jobs, employee directory)" -ForegroundColor White
    Write-Host "3. Trigger a backend deployment (this script)" -ForegroundColor White
    Write-Host "4. Refresh the frontend - you should remain logged in!" -ForegroundColor White
    Write-Host "5. Check browser console for session restoration logs" -ForegroundColor White
    
    Write-Host "`nExpected Results:" -ForegroundColor Cyan
    Write-Host "- Users stay logged in through deployments" -ForegroundColor White
    Write-Host "- No 'User session not found' errors after deployment" -ForegroundColor White
    Write-Host "- Seamless user experience across updates" -ForegroundColor White
    Write-Host "- Session data persists in database" -ForegroundColor White
    Write-Host "- Automatic cleanup of expired sessions" -ForegroundColor White
    
    Write-Host "`nMonitoring:" -ForegroundColor Cyan
    Write-Host "- Check Cloud Run logs for session statistics" -ForegroundColor White
    Write-Host "- Look for 'Cleaned up X expired sessions' messages" -ForegroundColor White
    Write-Host "- Monitor 'Session stats' for database health" -ForegroundColor White
    
    Write-Host "`nNext Steps:" -ForegroundColor Cyan
    Write-Host "1. Test the persistent session functionality" -ForegroundColor White
    Write-Host "2. Monitor session statistics in logs" -ForegroundColor White
    Write-Host "3. Verify users stay logged in through deployments" -ForegroundColor White
    Write-Host "4. Check database for user_sessions table creation" -ForegroundColor White
    
} else {
    Write-Host "Backend deployment failed!" -ForegroundColor Red
    exit 1
}
