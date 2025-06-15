# Force Consistent URL Pattern for EasyShifts Deployment
# This script ensures both frontend and backend use the same URL pattern

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Write-Info "🔧 Force Consistent URL Pattern for EasyShifts"
Write-Info "=============================================="

# Set project
gcloud config set project $ProjectId

Write-Info "📋 Current Cloud Run services:"
gcloud run services list --region=$Region

Write-Info ""
Write-Info "🔍 Step 1: Checking existing services"

# Get current service URLs
$backendExists = $false
$frontendExists = $false

try {
    $currentBackendUrl = gcloud run services describe easyshifts-backend --platform managed --region $Region --format 'value(status.url)' 2>$null
    if ($currentBackendUrl) {
        $backendExists = $true
        Write-Info "   Backend exists: $currentBackendUrl"
    }
} catch {
    Write-Info "   Backend service not found"
}

try {
    $currentFrontendUrl = gcloud run services describe easyshifts-frontend --platform managed --region $Region --format 'value(status.url)' 2>$null
    if ($currentFrontendUrl) {
        $frontendExists = $true
        Write-Info "   Frontend exists: $currentFrontendUrl"
    }
} catch {
    Write-Info "   Frontend service not found"
}

# Check URL patterns
$backendPattern = ""
$frontendPattern = ""

if ($currentBackendUrl) {
    if ($currentBackendUrl -match "https://easyshifts-backend-(.+)\.run\.app") {
        $backendPattern = $matches[1]
        Write-Info "   Backend URL pattern: $backendPattern"
    }
}

if ($currentFrontendUrl) {
    if ($currentFrontendUrl -match "https://easyshifts-frontend-(.+)\.run\.app") {
        $frontendPattern = $matches[1]
        Write-Info "   Frontend URL pattern: $frontendPattern"
    }
}

# Determine if we need to force consistency
$needsConsistency = $false
$targetPattern = "794306818447.us-central1"

if ($backendPattern -and $frontendPattern) {
    if ($backendPattern -ne $frontendPattern) {
        Write-Warning "   ⚠️ URL patterns are inconsistent!"
        Write-Warning "   Backend: $backendPattern"
        Write-Warning "   Frontend: $frontendPattern"
        $needsConsistency = $true
    } elseif ($backendPattern -ne $targetPattern) {
        Write-Warning "   ⚠️ URL pattern doesn't match target: $targetPattern"
        $needsConsistency = $true
    } else {
        Write-Success "   ✅ URL patterns are already consistent"
    }
} else {
    Write-Info "   One or both services don't exist, will create with consistent pattern"
    $needsConsistency = $true
}

if ($needsConsistency) {
    Write-Info ""
    Write-Info "🔄 Step 2: Forcing consistent URL pattern"
    
    # Delete existing services to force new URL pattern
    if ($frontendExists) {
        Write-Info "   Deleting existing frontend service..."
        gcloud run services delete easyshifts-frontend --region $Region --quiet
        Write-Success "   ✅ Frontend service deleted"
    }
    
    if ($backendExists -and $backendPattern -ne $targetPattern) {
        Write-Warning "   Backend has different pattern. Consider deleting and redeploying."
        Write-Info "   Current backend: $currentBackendUrl"
        Write-Info "   Target pattern: https://easyshifts-backend-$targetPattern.run.app"
        
        $response = Read-Host "   Delete backend service to force consistent URL? (y/N)"
        if ($response -eq "y" -or $response -eq "Y") {
            Write-Info "   Deleting existing backend service..."
            gcloud run services delete easyshifts-backend --region $Region --quiet
            Write-Success "   ✅ Backend service deleted"
            $backendExists = $false
        }
    }
}

Write-Info ""
Write-Info "🚀 Step 3: Deploying with consistent URLs"

# Check if DB_PASSWORD is set
if (-not $env:DB_PASSWORD) {
    Write-Warning "⚠️ DB_PASSWORD environment variable is not set!"
    Write-Info "Setting default password for deployment..."
    $env:DB_PASSWORD = "a61d15d9b4f2671739338d1082cc7b75c0084e21"
}

# Deploy backend if needed
if (-not $backendExists -or $needsConsistency) {
    Write-Info "   Building and deploying backend..."
    Push-Location "Backend"
    try {
        $backendImage = "$Region-docker.pkg.dev/$ProjectId/easyshifts-repo/easyshifts-backend:latest"
        
        # Build image
        gcloud builds submit --tag $backendImage .
        
        # Deploy with specific configuration to ensure consistent URL
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
            --set-env-vars "GOOGLE_CLIENT_ID=794306818447-4prnpg1p13a4smvnnfs7tfvkesrld9ms.apps.googleusercontent.com" `
            --set-env-vars "DB_HOST=miano.h.filess.io" `
            --set-env-vars "DB_PORT=3305" `
            --set-env-vars "DB_USER=easyshiftsdb_danceshall" `
            --set-env-vars "DB_NAME=easyshiftsdb_danceshall" `
            --set-env-vars "DB_PASSWORD=$env:DB_PASSWORD" `
            --set-env-vars "REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com" `
            --set-env-vars "REDIS_PORT=12649" `
            --set-env-vars "REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa" `
            --set-env-vars "ENVIRONMENT=production"
            
        Write-Success "   ✅ Backend deployed"
    } finally {
        Pop-Location
    }
}

# Get the actual backend URL
$actualBackendUrl = gcloud run services describe easyshifts-backend --platform managed --region $Region --format 'value(status.url)'
$websocketUrl = ($actualBackendUrl -replace "https:", "wss:") + "/ws"

Write-Info "   Backend URL: $actualBackendUrl"
Write-Info "   WebSocket URL: $websocketUrl"

# Deploy frontend
Write-Info "   Building and deploying frontend..."
Push-Location "app"
try {
    $frontendImage = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo/holi-timesheets-frontend:latest"
    
    # Build image
    gcloud builds submit --tag $frontendImage .
    
    # Deploy frontend with backend URL
    gcloud run deploy easyshifts-frontend `
        --image $frontendImage `
        --platform managed `
        --region $Region `
        --allow-unauthenticated `
        --memory 512Mi `
        --cpu 1 `
        --concurrency 100 `
        --timeout 300 `
        --set-env-vars "REACT_APP_GOOGLE_CLIENT_ID=794306818447-4prnpg1p13a4smvnnfs7tfvkesrld9ms.apps.googleusercontent.com" `
        --set-env-vars "REACT_APP_API_URL=$websocketUrl" `
        --set-env-vars "REACT_APP_ENV=production"
        
    Write-Success "   ✅ Frontend deployed"
} finally {
    Pop-Location
}

# Get final URLs
$finalBackendUrl = gcloud run services describe easyshifts-backend --platform managed --region $Region --format 'value(status.url)'
$finalFrontendUrl = gcloud run services describe easyshifts-frontend --platform managed --region $Region --format 'value(status.url)'

Write-Info ""
Write-Info "🔍 Step 4: Verifying URL consistency"

# Extract patterns
$finalBackendPattern = ""
$finalFrontendPattern = ""

if ($finalBackendUrl -match "https://easyshifts-backend-(.+)\.run\.app") {
    $finalBackendPattern = $matches[1]
}

if ($finalFrontendUrl -match "https://easyshifts-frontend-(.+)\.run\.app") {
    $finalFrontendPattern = $matches[1]
}

Write-Success "🎉 Deployment completed!"
Write-Success "📱 Frontend URL: $finalFrontendUrl"
Write-Success "🖥️ Backend URL: $finalBackendUrl"
Write-Success "🔌 WebSocket URL: $($finalBackendUrl -replace 'https:', 'wss:')/ws"

Write-Info ""
if ($finalBackendPattern -eq $finalFrontendPattern) {
    Write-Success "✅ URL patterns are now consistent!"
    Write-Success "   Pattern: $finalBackendPattern"
} else {
    Write-Warning "⚠️ URL patterns are still inconsistent:"
    Write-Warning "   Backend: $finalBackendPattern"
    Write-Warning "   Frontend: $finalFrontendPattern"
    Write-Warning "   This may be due to Google Cloud Run's automatic URL generation."
}

Write-Info ""
Write-Info "📋 Next steps:"
Write-Info "1. Update your environment files with the actual URLs above"
Write-Info "2. Test the connection using test-connection.html"
Write-Info "3. Update Google OAuth settings if the frontend URL changed"

# Update environment files with actual URLs
Write-Info ""
Write-Info "🔧 Updating environment files with actual URLs..."

$actualWebsocketUrl = ($finalBackendUrl -replace "https:", "wss:") + "/ws"

# Update app/.env.production
$envProductionContent = @"
# EasyShifts Frontend Production Environment Configuration

# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com

# API Configuration - Actual Production Backend URL
REACT_APP_API_URL=$actualWebsocketUrl

# Environment
REACT_APP_ENV=production

# Build Configuration
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
"@

$envProductionContent | Out-File -FilePath "app\.env.production" -Encoding UTF8

# Update runtime config files
$runtimeConfigContent = @"
// Runtime environment configuration for EasyShifts
// This file is loaded by index.html and provides environment variables at runtime
window._env_ = {
  REACT_APP_GOOGLE_CLIENT_ID: "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com",
  REACT_APP_API_URL: "$actualWebsocketUrl",
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

if (Test-Path "app\build\env-config.js") {
    $runtimeConfigContent | Out-File -FilePath "app\build\env-config.js" -Encoding UTF8
}

Write-Success "✅ Environment files updated with actual deployment URLs"

