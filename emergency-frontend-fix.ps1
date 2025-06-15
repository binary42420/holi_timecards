# Emergency Frontend Fix - Rebuild with Correct WebSocket URL
# This script rebuilds and redeploys the frontend with the correct backend URL

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

# Configuration
$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"
$CORRECT_BACKEND_URL = "wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws"

Write-Host "🚨 EMERGENCY FRONTEND FIX" -ForegroundColor Red
Write-Host "The frontend is still using placeholder URL instead of actual backend URL" -ForegroundColor Yellow
Write-Host "Correct Backend URL: $CORRECT_BACKEND_URL" -ForegroundColor Green

# Step 1: Update all environment files with correct URL
Write-Host "`n📝 Step 1: Updating Environment Files" -ForegroundColor Cyan

# Update app/.env.production
$envProductionContent = @"
# HOLI Timesheets Frontend Production Environment Configuration

# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID

# API Configuration - Production Backend URL
REACT_APP_API_URL=$CORRECT_BACKEND_URL

# Environment
REACT_APP_ENV=production

# Build Configuration
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
"@

$envProductionContent | Out-File -FilePath "app\.env.production" -Encoding UTF8
Write-Host "✅ Updated app/.env.production" -ForegroundColor Green

# Update app/public/env-config.js
$envConfigContent = @"
// Runtime environment configuration for HOLI Timesheets
// This file is loaded by index.html and provides environment variables at runtime

// Detect if we're running locally
const isLocalDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// Force local development mode if needed (set to false for Cloud Run deployment)
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

$envConfigContent | Out-File -FilePath "app\public\env-config.js" -Encoding UTF8
Write-Host "✅ Updated app/public/env-config.js" -ForegroundColor Green

# Step 2: Clear any cached build files
Write-Host "`n🧹 Step 2: Clearing Build Cache" -ForegroundColor Cyan

if (Test-Path "app\build") {
    Remove-Item -Recurse -Force "app\build"
    Write-Host "✅ Cleared app/build directory" -ForegroundColor Green
}

if (Test-Path "app\node_modules\.cache") {
    Remove-Item -Recurse -Force "app\node_modules\.cache"
    Write-Host "✅ Cleared node_modules cache" -ForegroundColor Green
}

# Step 3: Build new frontend image
Write-Host "`n🏗️ Step 3: Building Frontend with Correct URL" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

Write-Host "Building frontend image: $frontendImage" -ForegroundColor Yellow

Set-Location "app"
try {
    # Set environment variables for build
    $env:REACT_APP_GOOGLE_CLIENT_ID = $GOOGLE_CLIENT_ID
    $env:REACT_APP_API_URL = $CORRECT_BACKEND_URL
    $env:REACT_APP_ENV = "production"
    
    Write-Host "Environment variables set for build:" -ForegroundColor Gray
    Write-Host "  REACT_APP_GOOGLE_CLIENT_ID: $env:REACT_APP_GOOGLE_CLIENT_ID" -ForegroundColor Gray
    Write-Host "  REACT_APP_API_URL: $env:REACT_APP_API_URL" -ForegroundColor Gray
    Write-Host "  REACT_APP_ENV: $env:REACT_APP_ENV" -ForegroundColor Gray
    
    # Build Docker image
    $buildCmd = "docker build -t `"$frontendImage`" ."
    Write-Host "Running: $buildCmd" -ForegroundColor Gray
    
    Invoke-Expression $buildCmd
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Frontend build failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Frontend image built successfully!" -ForegroundColor Green
    
} finally {
    Set-Location ".."
}

# Step 4: Push to registry
Write-Host "`n📤 Step 4: Pushing to Artifact Registry" -ForegroundColor Cyan

$pushCmd = "docker push `"$frontendImage`""
Write-Host "Running: $pushCmd" -ForegroundColor Gray

Invoke-Expression $pushCmd
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend push failed!" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Frontend image pushed successfully!" -ForegroundColor Green

# Step 5: Deploy to Cloud Run
Write-Host "`n🚀 Step 5: Deploying to Cloud Run" -ForegroundColor Cyan

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
    "--set-env-vars `"REACT_APP_API_URL=$CORRECT_BACKEND_URL`" " +
    "--set-env-vars `"REACT_APP_ENV=production`""

Write-Host "Running frontend deployment..." -ForegroundColor Gray
Invoke-Expression $deployCmd

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Frontend deployed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Frontend deployment failed!" -ForegroundColor Red
    exit 1
}

# Step 6: Verify deployment
Write-Host "`n🔍 Step 6: Verifying Deployment" -ForegroundColor Cyan

$frontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)' 2>$null

if ($frontendUrl) {
    Write-Host "✅ Frontend URL: $frontendUrl" -ForegroundColor Green
    Write-Host "✅ Backend WebSocket: $CORRECT_BACKEND_URL" -ForegroundColor Green
    
    Write-Host "`n🎉 EMERGENCY FIX COMPLETE!" -ForegroundColor Green
    Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
    Write-Host "1. Clear your browser cache (Ctrl+Shift+R)" -ForegroundColor White
    Write-Host "2. Visit: $frontendUrl" -ForegroundColor White
    Write-Host "3. Try Google OAuth login" -ForegroundColor White
    Write-Host "4. Navigate to manager-jobs page" -ForegroundColor White
    Write-Host "5. Verify WebSocket connects to correct backend" -ForegroundColor White
    
} else {
    Write-Host "❌ Could not retrieve frontend URL" -ForegroundColor Red
    exit 1
}

Write-Host "`n🔧 Issues Fixed:" -ForegroundColor Cyan
Write-Host "✅ Removed placeholder WebSocket URL" -ForegroundColor Green
Write-Host "✅ Updated all environment files with correct backend URL" -ForegroundColor Green
Write-Host "✅ Rebuilt frontend with correct configuration" -ForegroundColor Green
Write-Host "✅ Deployed fresh frontend image to Cloud Run" -ForegroundColor Green
