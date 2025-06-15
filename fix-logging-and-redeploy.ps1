# Fix logging functions and redeploy HOLI Timesheets

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

Write-Host "🔧 Fixing logging functions and redeploying HOLI Timesheets" -ForegroundColor Green

# Set the project
gcloud config set project $ProjectId

# Update the backend URL in env-config.js to match the actual deployed URL
$actualBackendUrl = "wss://holi-timesheets-backend-s5b2sxgpsa-uc.a.run.app/ws"

Write-Host "📝 Updating environment configuration with correct backend URL" -ForegroundColor Yellow

# Update app/public/env-config.js with correct URL
$envConfigContent = @"
// Runtime environment configuration for HOLI Timesheets
// This file is loaded by index.html and provides environment variables at runtime
window._env_ = {
  REACT_APP_GOOGLE_CLIENT_ID: "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com",
  REACT_APP_API_URL: "$actualBackendUrl",
  REACT_APP_ENV: "production"
};

// Global logging fallback to prevent "logError is not defined" errors
if (typeof window !== 'undefined' && !window.logError) {
  window.logError = function(component, message, error) {
    const timestamp = new Date().toISOString();
    const logMessage = '[' + timestamp + '] [ERROR] [' + component + '] ' + message;
    console.error(logMessage, error || '');
  };

  window.logDebug = function(component, message, data) {
    const timestamp = new Date().toISOString();
    const logMessage = '[' + timestamp + '] [DEBUG] [' + component + '] ' + message;
    console.log(logMessage, data || '');
  };

  window.logWarning = function(component, message, data) {
    const timestamp = new Date().toISOString();
    const logMessage = '[' + timestamp + '] [WARNING] [' + component + '] ' + message;
    console.warn(logMessage, data || '');
  };

  window.logInfo = function(component, message, data) {
    const timestamp = new Date().toISOString();
    const logMessage = '[' + timestamp + '] [INFO] [' + component + '] ' + message;
    console.info(logMessage, data || '');
  };
}

// Debug logging
console.log('HOLI Timesheets env-config.js loaded:', window._env_);
"@

$envConfigContent | Out-File -FilePath "app\public\env-config.js" -Encoding UTF8
Write-Host "   ✅ Updated app/public/env-config.js" -ForegroundColor Green

# Also update build version
$envConfigContent | Out-File -FilePath "app\build\env-config.js" -Encoding UTF8
Write-Host "   ✅ Updated app/build/env-config.js" -ForegroundColor Green

# Build new frontend image
Write-Host "🏗️ Building new frontend image with fixed logging" -ForegroundColor Yellow
Set-Location app

try {
    # Build the frontend
    Write-Host "   Building React app..." -ForegroundColor Cyan
    $env:REACT_APP_GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
    $env:REACT_APP_API_URL = $actualBackendUrl
    $env:REACT_APP_ENV = "production"
    
    npm run build
    Write-Host "   ✅ Frontend build completed" -ForegroundColor Green
    
    # Build Docker image
    Write-Host "   Building Docker image..." -ForegroundColor Cyan
    gcloud builds submit --tag "$Region-docker.pkg.dev/$ProjectId/easyshifts-repo/holi-timesheets-frontend-fixed:latest" .
    Write-Host "   ✅ Docker image built" -ForegroundColor Green
    
} catch {
    Write-Host "   ❌ Build failed: $($_.Exception.Message)" -ForegroundColor Red
    throw
} finally {
    Set-Location ..
}

# Deploy the fixed frontend
Write-Host "🚀 Deploying fixed frontend" -ForegroundColor Yellow

gcloud run deploy holi-timesheets-frontend `
    --image "$Region-docker.pkg.dev/$ProjectId/easyshifts-repo/holi-timesheets-frontend-fixed:latest" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 512Mi `
    --cpu 1 `
    --concurrency 100 `
    --timeout 300 `
    --set-env-vars "REACT_APP_GOOGLE_CLIENT_ID=794306818447-4prnpg1p13a4smvnnfs7tfvkesrld9ms.apps.googleusercontent.com" `
    --set-env-vars "REACT_APP_API_URL=$actualBackendUrl" `
    --set-env-vars "REACT_APP_ENV=production"

# Get the final URL
$frontendUrl = gcloud run services describe holi-timesheets-frontend --platform managed --region $Region --format 'value(status.url)'

Write-Host "🎉 HOLI Timesheets logging fix deployed!" -ForegroundColor Green
Write-Host "📱 Frontend URL: $frontendUrl" -ForegroundColor Green
Write-Host "🔧 Backend URL: https://holi-timesheets-backend-s5b2sxgpsa-uc.a.run.app" -ForegroundColor Green
Write-Host "🔌 WebSocket URL: $actualBackendUrl" -ForegroundColor Green

Write-Host ""
Write-Host "🧪 Test the fix:" -ForegroundColor Cyan
Write-Host "1. Open: $frontendUrl" -ForegroundColor Cyan
Write-Host "2. Open browser console (F12)" -ForegroundColor Cyan
Write-Host "3. Look for 'HOLI Timesheets env-config.js loaded' message" -ForegroundColor Cyan
Write-Host "4. Try logging in - logError should now be defined" -ForegroundColor Cyan

Write-Host ""
Write-Host "🔍 If you still see 'logError is not defined':" -ForegroundColor Yellow
Write-Host "1. Hard refresh the page (Ctrl+F5)" -ForegroundColor Yellow
Write-Host "2. Clear browser cache" -ForegroundColor Yellow
Write-Host "3. Check if env-config.js is loading in Network tab" -ForegroundColor Yellow
