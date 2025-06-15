# Test Session Persistence - Redeploy Backend to Test Session Survival

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$SERVICE_PREFIX = "holi-timesheets"

Write-Host "TESTING SESSION PERSISTENCE" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

Write-Host "`nThis script will redeploy the backend to test if sessions persist through deployments." -ForegroundColor Yellow

Write-Host "`nBEFORE RUNNING THIS TEST:" -ForegroundColor Red
Write-Host "1. Open the frontend: https://holi-timesheets-frontend-2ma525uu2a-uc.a.run.app" -ForegroundColor White
Write-Host "2. Sign in with Google OAuth" -ForegroundColor White
Write-Host "3. Navigate to manager-jobs and employee directory" -ForegroundColor White
Write-Host "4. Confirm you are logged in and can see data" -ForegroundColor White
Write-Host "5. Keep the browser tab open" -ForegroundColor White

Write-Host "`nPress any key to continue with the deployment test..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host "`nRedeploying backend to test session persistence..." -ForegroundColor Yellow

# Redeploy the same image to trigger a restart
gcloud run deploy $SERVICE_PREFIX-backend `
    --image us-central1-docker.pkg.dev/holitimecards/holi-timesheets-repo/holi-timesheets-backend:redis-persistence-20250614-225500 `
    --platform managed `
    --region $Region

if ($LASTEXITCODE -eq 0) {
    $backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)'
    
    Write-Host "`nBACKEND REDEPLOYED SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    
    Write-Host "`nBackend URL: $backendUrl" -ForegroundColor White
    
    Write-Host "`nNOW TEST SESSION PERSISTENCE:" -ForegroundColor Cyan
    Write-Host "1. Go back to your browser tab with the frontend" -ForegroundColor White
    Write-Host "2. Refresh the page (F5 or Ctrl+R)" -ForegroundColor White
    Write-Host "3. You should REMAIN LOGGED IN!" -ForegroundColor Green
    Write-Host "4. Navigate to manager-jobs page" -ForegroundColor White
    Write-Host "5. Navigate to employee directory" -ForegroundColor White
    Write-Host "6. All data should load without re-authentication" -ForegroundColor White
    
    Write-Host "`nEXPECTED RESULTS:" -ForegroundColor Cyan
    Write-Host "✅ You remain logged in after backend restart" -ForegroundColor Green
    Write-Host "✅ No 'User session not found' errors" -ForegroundColor Green
    Write-Host "✅ Client companies load successfully" -ForegroundColor Green
    Write-Host "✅ Jobs load successfully" -ForegroundColor Green
    Write-Host "✅ Employee directory loads successfully" -ForegroundColor Green
    Write-Host "✅ No need to re-authenticate with Google" -ForegroundColor Green
    
    Write-Host "`nIF SESSION PERSISTENCE WORKS:" -ForegroundColor Cyan
    Write-Host "🎉 Sessions will survive ALL future deployments!" -ForegroundColor Green
    Write-Host "🎉 Users won't need to re-login after updates!" -ForegroundColor Green
    Write-Host "🎉 Seamless user experience across deployments!" -ForegroundColor Green
    
    Write-Host "`nIF SESSION PERSISTENCE FAILS:" -ForegroundColor Cyan
    Write-Host "❌ You'll be logged out and need to sign in again" -ForegroundColor Red
    Write-Host "❌ Check Redis connection and configuration" -ForegroundColor Red
    Write-Host "❌ Review backend logs for Redis errors" -ForegroundColor Red
    
    Write-Host "`nMONITORING:" -ForegroundColor Cyan
    Write-Host "Check backend logs for Redis session messages:" -ForegroundColor White
    Write-Host "- 'Session stored in Redis for persistence'" -ForegroundColor White
    Write-Host "- 'Session restored from Redis persistence'" -ForegroundColor White
    Write-Host "- 'Redis connection established'" -ForegroundColor White
    
    Write-Host "`nTo check logs:" -ForegroundColor Cyan
    Write-Host "gcloud logging read 'resource.type=cloud_run_revision AND resource.labels.service_name=holi-timesheets-backend AND textPayload:Redis' --limit=10" -ForegroundColor White
    
} else {
    Write-Host "Backend deployment failed!" -ForegroundColor Red
    exit 1
}
