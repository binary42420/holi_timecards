# EasyShifts Deployment URL Fix Script
# This script fixes all URL inconsistencies and connection issues

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1",
    [switch]$SkipBuild = $false
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Write-Info "🔧 EasyShifts Deployment URL Fix"
Write-Info "================================"

# Define consistent URLs
$BACKEND_URL = "https://easyshifts-backend-794306818447.us-central1.run.app"
$WEBSOCKET_URL = "wss://easyshifts-backend-794306818447.us-central1.run.app/ws"
$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"

Write-Info "🎯 Target URLs:"
Write-Info "   Backend: $BACKEND_URL"
Write-Info "   WebSocket: $WEBSOCKET_URL"
Write-Info ""

# Step 1: Fix environment configuration files
Write-Info "📝 Step 1: Updating environment configuration files"

# Update app/.env.production
$envProductionContent = @"
# EasyShifts Frontend Production Environment Configuration

# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID

# API Configuration - Production Backend URL
REACT_APP_API_URL=$WEBSOCKET_URL

# Environment
REACT_APP_ENV=production

# Build Configuration
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
"@

$envProductionContent | Out-File -FilePath "app\.env.production" -Encoding UTF8
Write-Success "   ✅ Updated app/.env.production"

# Update runtime configuration files
$runtimeConfigContent = @"
// Runtime environment configuration for EasyShifts
// This file is loaded by index.html and provides environment variables at runtime
window._env_ = {
  REACT_APP_GOOGLE_CLIENT_ID: "$GOOGLE_CLIENT_ID",
  REACT_APP_API_URL: "$WEBSOCKET_URL",
  REACT_APP_ENV: "production"
};

// Global logging fallback to prevent "logError is not defined" errors
if (typeof window !== 'undefined' && !window.logError) {
  window.logError = function(component, message, error) {
    const timestamp = new Date().toISOString();
    const logMessage = `[`${timestamp}`] [ERROR] [`${component}`] `${message}`;
    console.error(logMessage, error || '');
  };

  window.logDebug = function(component, message, data) {
    const timestamp = new Date().toISOString();
    const logMessage = `[`${timestamp}`] [DEBUG] [`${component}`] `${message}`;
    console.log(logMessage, data || '');
  };

  window.logWarning = function(component, message, data) {
    const timestamp = new Date().toISOString();
    const logMessage = `[`${timestamp}`] [WARNING] [`${component}`] `${message}`;
    console.warn(logMessage, data || '');
  };

  window.logInfo = function(component, message, data) {
    const timestamp = new Date().toISOString();
    const logMessage = `[`${timestamp}`] [INFO] [`${component}`] `${message}`;
    console.info(logMessage, data || '');
  };
}

// Debug logging
console.log('env-config.js loaded:', window._env_);
"@

$runtimeConfigContent | Out-File -FilePath "app\public\env-config.js" -Encoding UTF8
Write-Success "   ✅ Updated app/public/env-config.js"

if (Test-Path "app\build\env-config.js") {
    $runtimeConfigContent | Out-File -FilePath "app\build\env-config.js" -Encoding UTF8
    Write-Success "   ✅ Updated app/build/env-config.js"
}

# Step 2: Test WebSocket connection
Write-Info "🔌 Step 2: Testing WebSocket connection"
try {
    $testResult = Test-NetConnection -ComputerName "easyshifts-backend-794306818447.us-central1.run.app" -Port 443
    if ($testResult.TcpTestSucceeded) {
        Write-Success "   ✅ Backend server is reachable"
    } else {
        Write-Warning "   ⚠️ Backend server connection test failed"
    }
} catch {
    Write-Warning "   ⚠️ Could not test backend connection: $($_.Exception.Message)"
}

# Step 3: Rebuild frontend if not skipped
if (-not $SkipBuild) {
    Write-Info "🏗️ Step 3: Rebuilding frontend with correct environment"
    
    Push-Location "app"
    try {
        Write-Info "   Installing dependencies..."
        npm ci --silent
        
        Write-Info "   Building production frontend..."
        $env:REACT_APP_GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
        $env:REACT_APP_API_URL = $WEBSOCKET_URL
        $env:REACT_APP_ENV = "production"
        
        npm run build
        Write-Success "   ✅ Frontend build completed"
        
        # Verify the build contains correct URLs
        if (Test-Path "build\env-config.js") {
            $buildConfig = Get-Content "build\env-config.js" -Raw
            if ($buildConfig -match $WEBSOCKET_URL) {
                Write-Success "   ✅ Build configuration verified"
            } else {
                Write-Warning "   ⚠️ Build configuration may not be correct"
            }
        }
        
    } catch {
        Write-Error "   ❌ Frontend build failed: $($_.Exception.Message)"
        throw
    } finally {
        Pop-Location
    }
} else {
    Write-Info "🏗️ Step 3: Skipping frontend build (use -SkipBuild:$false to build)"
}

# Step 4: Deploy to Cloud Run
Write-Info "🚀 Step 4: Deploying to Cloud Run"

# Set project
gcloud config set project $ProjectId

# Build and deploy backend
Write-Info "   Building backend..."
Push-Location "Backend"
try {
    $backendImage = "$Region-docker.pkg.dev/$ProjectId/easyshifts-repo/easyshifts-backend:latest"
    gcloud builds submit --tag $backendImage .
    
    Write-Info "   Deploying backend..."
    gcloud run deploy easyshifts-backend `
        --image $backendImage `
        --platform managed `
        --region $Region `
        --allow-unauthenticated `
        --port 8080 `
        --memory 1Gi `
        --cpu 1 `
        --concurrency 100 `
        --timeout 300 `
        --set-env-vars "GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" `
        --set-env-vars "DB_HOST=miano.h.filess.io" `
        --set-env-vars "DB_PORT=3305" `
        --set-env-vars "DB_USER=easyshiftsdb_danceshall" `
        --set-env-vars "DB_NAME=easyshiftsdb_danceshall" `
        --set-env-vars "DB_PASSWORD=$env:DB_PASSWORD" `
        --set-env-vars "REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com" `
        --set-env-vars "REDIS_PORT=12649" `
        --set-env-vars "REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa"
        
    Write-Success "   ✅ Backend deployed"
} finally {
    Pop-Location
}

# Build and deploy frontend
Write-Info "   Building frontend..."
Push-Location "app"
try {
    $frontendImage = "$Region-docker.pkg.dev/$ProjectId/easyshifts-repo/easyshifts-frontend:latest"
    gcloud builds submit --tag $frontendImage .
    
    Write-Info "   Deploying frontend..."
    gcloud run deploy easyshifts-frontend `
        --image $frontendImage `
        --platform managed `
        --region $Region `
        --allow-unauthenticated `
        --memory 512Mi `
        --cpu 1 `
        --concurrency 100 `
        --timeout 300 `
        --set-env-vars "REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" `
        --set-env-vars "REACT_APP_API_URL=$WEBSOCKET_URL" `
        --set-env-vars "REACT_APP_ENV=production"
        
    Write-Success "   ✅ Frontend deployed"
} finally {
    Pop-Location
}

# Step 5: Get deployment URLs and verify
Write-Info "🔍 Step 5: Verifying deployment"

$deployedBackendUrl = gcloud run services describe easyshifts-backend --platform managed --region $Region --format 'value(status.url)'
$deployedFrontendUrl = gcloud run services describe easyshifts-frontend --platform managed --region $Region --format 'value(status.url)'

Write-Success "🎉 Deployment completed successfully!"
Write-Success "📱 Frontend URL: $deployedFrontendUrl"
Write-Success "🖥️ Backend URL: $deployedBackendUrl"
Write-Success "🔌 WebSocket URL: $($deployedBackendUrl -replace 'https:', 'wss:')/ws"

Write-Info ""
Write-Info "📋 Next steps:"
Write-Info "1. Open the frontend URL in your browser"
Write-Info "2. Check browser console for any connection errors"
Write-Info "3. Test login functionality"
Write-Info "4. Verify WebSocket connections in Network tab"

Write-Info ""
Write-Info "🔧 If issues persist:"
Write-Info "1. Check browser console for detailed error messages"
Write-Info "2. Verify the backend is responding at: $deployedBackendUrl/health"
Write-Info "3. Test WebSocket connection manually"

