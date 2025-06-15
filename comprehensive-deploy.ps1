#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Comprehensive deployment script for HOLI Timesheets application
    
.DESCRIPTION
    This script:
    1. Fixes all Google OAuth client IDs and redirect URIs
    2. Rebuilds Docker containers locally using Docker Desktop
    3. Pushes to Google Artifact Registry
    4. Deploys to Cloud Run with consistent configuration
    
.PARAMETER ProjectId
    Google Cloud Project ID (default: holitimecards)
    
.PARAMETER Region
    Google Cloud Region (default: us-central1)
    
.PARAMETER SkipBuild
    Skip Docker build and use existing images
    
.PARAMETER BackendOnly
    Deploy only the backend service
    
.PARAMETER FrontendOnly
    Deploy only the frontend service
#>

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1",
    [switch]$SkipBuild,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

# Configuration
$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

# Database Configuration
$DB_CONFIG = @{
    HOST = "miano.h.filess.io"
    PORT = "3305"
    USER = "easyshiftsdb_danceshall"
    NAME = "easyshiftsdb_danceshall"
    PASSWORD = "a61d15d9b4f2671739338d1082cc7b75c0084e21"
}

# Redis Configuration
$REDIS_CONFIG = @{
    HOST = "redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com"
    PORT = "12649"
    PASSWORD = "AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa"
    DB = "0"
}

# Security Keys
$SECURITY_CONFIG = @{
    SESSION_SECRET = "K8mP9vN2xQ7wE5tR1yU6iO3pA8sD4fG9hJ2kL5nM7bV0cX1zQ6wE9rT3yU8iO5pA"
    CSRF_SECRET = "X9mN2bV5cQ8wE1rT4yU7iO0pA3sD6fG2hJ5kL8nM1bV4cX7zQ0wE3rT6yU9iO2pA"
}

# Helper Functions
function Write-Header($message) {
    Write-Host "`n🚀 $message" -ForegroundColor Cyan
    Write-Host ("=" * 60) -ForegroundColor Cyan
}

function Write-Step($message) {
    Write-Host "`n📋 $message" -ForegroundColor Yellow
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

function Write-Warning($message) {
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

function Test-Command($command) {
    try {
        & $command --version 2>$null | Out-Null
        return $true
    } catch {
        return $false
    }
}

function Invoke-SafeCommand($command, $description, $workingDir = $null) {
    Write-Host "   Running: $description" -ForegroundColor Gray
    
    $originalLocation = Get-Location
    try {
        if ($workingDir) {
            Set-Location $workingDir
        }
        
        $result = Invoke-Expression $command
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Command failed: $command"
            return $false
        }
        return $true
    } catch {
        Write-Error "Exception running command: $($_.Exception.Message)"
        return $false
    } finally {
        Set-Location $originalLocation
    }
}

# Main Script
Write-Header "HOLI Timesheets Comprehensive Deployment"

# Step 1: Prerequisites Check
Write-Step "Checking Prerequisites"

$prerequisites = @(
    @{ Command = "docker"; Name = "Docker Desktop" },
    @{ Command = "gcloud"; Name = "Google Cloud CLI" },
    @{ Command = "node"; Name = "Node.js" },
    @{ Command = "npm"; Name = "NPM" }
)

$missingPrereqs = @()
foreach ($prereq in $prerequisites) {
    if (Test-Command $prereq.Command) {
        Write-Success "$($prereq.Name) is available"
    } else {
        Write-Error "$($prereq.Name) is not available"
        $missingPrereqs += $prereq.Name
    }
}

if ($missingPrereqs.Count -gt 0) {
    Write-Error "Missing prerequisites: $($missingPrereqs -join ', ')"
    exit 1
}

# Check Docker Desktop is running
try {
    docker info 2>$null | Out-Null
    Write-Success "Docker Desktop is running"
} catch {
    Write-Error "Docker Desktop is not running. Please start Docker Desktop."
    exit 1
}

# Step 2: Fix Environment Files
Write-Step "Fixing Environment Configuration Files"

# Fix Backend .env
$backendEnvContent = @"
# HOLI Timesheets Backend Environment Configuration

# Database Configuration
DB_HOST=$($DB_CONFIG.HOST)
DB_PORT=$($DB_CONFIG.PORT)
DB_NAME=$($DB_CONFIG.NAME)
DB_USER=$($DB_CONFIG.USER)
DB_PASSWORD=$($DB_CONFIG.PASSWORD)

# Redis Configuration
REDIS_HOST=$($REDIS_CONFIG.HOST)
REDIS_PORT=$($REDIS_CONFIG.PORT)
REDIS_PASSWORD=$($REDIS_CONFIG.PASSWORD)
REDIS_DB=$($REDIS_CONFIG.DB)

# Security Keys
SESSION_SECRET_KEY=$($SECURITY_CONFIG.SESSION_SECRET)
CSRF_SECRET_KEY=$($SECURITY_CONFIG.CSRF_SECRET)

# Google OAuth Configuration
GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID

# Server Configuration
HOST=0.0.0.0
PORT=8080
ENVIRONMENT=production
"@

$backendEnvContent | Out-File -FilePath "Backend\.env" -Encoding UTF8
Write-Success "Updated Backend/.env"

# Fix Frontend .env.production (fix the malformed WebSocket URL)
$frontendEnvContent = @"
# HOLI Timesheets Frontend Production Environment Configuration

# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID

# API Configuration - Production Backend URL (will be updated after deployment)
REACT_APP_API_URL=wss://$SERVICE_PREFIX-backend-placeholder.run.app/ws

# Environment
REACT_APP_ENV=production

# Build Configuration
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
"@

$frontendEnvContent | Out-File -FilePath "app\.env.production" -Encoding UTF8
Write-Success "Fixed app/.env.production (removed malformed wss://https:// URL)"

# Fix app/public/env-config.js
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
    : "wss://$SERVICE_PREFIX-backend-placeholder.run.app/ws",
  REACT_APP_ENV: (isLocalDevelopment || forceLocalMode) ? "development" : "production"
};

console.log('env-config.js loaded:', window._env_);
"@

$envConfigContent | Out-File -FilePath "app\public\env-config.js" -Encoding UTF8
Write-Success "Updated app/public/env-config.js"

# Step 3: Configure Google Cloud
Write-Step "Configuring Google Cloud"

# Set project
if (!(Invoke-SafeCommand "gcloud config set project $ProjectId" "Setting project")) {
    exit 1
}

# Configure Docker for Artifact Registry
if (!(Invoke-SafeCommand "gcloud auth configure-docker $Region-docker.pkg.dev" "Configuring Docker auth")) {
    exit 1
}

# Create repository if it doesn't exist
Write-Host "   Ensuring Artifact Registry repository exists..."
$repoExists = gcloud artifacts repositories describe holi-timesheets-repo --location=$Region 2>$null
if (!$repoExists) {
    if (!(Invoke-SafeCommand "gcloud artifacts repositories create holi-timesheets-repo --repository-format=docker --location=$Region" "Creating repository")) {
        exit 1
    }
}

Write-Success "Google Cloud configured"

# Step 4: Build Docker Images Locally
if (!$SkipBuild) {
    Write-Step "Building Docker Images Locally with Docker Desktop"

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"

    # Build Backend
    if (!$FrontendOnly) {
        Write-Host "   Building backend image..."
        $backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:$timestamp"

        if (!(Invoke-SafeCommand "docker build -t `"$backendImage`" ." "Building backend" "Backend")) {
            Write-Error "Backend build failed"
            exit 1
        }

        Write-Host "   Pushing backend image to Artifact Registry..."
        if (!(Invoke-SafeCommand "docker push `"$backendImage`"" "Pushing backend")) {
            Write-Error "Backend push failed"
            exit 1
        }

        Write-Success "Backend image built and pushed: $backendImage"
    }

    # Build Frontend
    if (!$BackendOnly) {
        Write-Host "   Building frontend image..."
        $frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"

        if (!(Invoke-SafeCommand "docker build -t `"$frontendImage`" ." "Building frontend" "app")) {
            Write-Error "Frontend build failed"
            exit 1
        }

        Write-Host "   Pushing frontend image to Artifact Registry..."
        if (!(Invoke-SafeCommand "docker push `"$frontendImage`"" "Pushing frontend")) {
            Write-Error "Frontend push failed"
            exit 1
        }

        Write-Success "Frontend image built and pushed: $frontendImage"
    }
} else {
    Write-Warning "Skipping build - using existing images"
    $timestamp = "latest"
    $backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:$timestamp"
    $frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:$timestamp"
}

# Step 5: Deploy to Cloud Run
Write-Step "Deploying to Cloud Run"

# Deploy Backend
if (!$FrontendOnly) {
    Write-Host "   Deploying backend service..."

    $backendEnvVars = @(
        "GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID",
        "DB_HOST=$($DB_CONFIG.HOST)",
        "DB_PORT=$($DB_CONFIG.PORT)",
        "DB_USER=$($DB_CONFIG.USER)",
        "DB_NAME=$($DB_CONFIG.NAME)",
        "DB_PASSWORD=$($DB_CONFIG.PASSWORD)",
        "REDIS_HOST=$($REDIS_CONFIG.HOST)",
        "REDIS_PORT=$($REDIS_CONFIG.PORT)",
        "REDIS_PASSWORD=$($REDIS_CONFIG.PASSWORD)",
        "REDIS_DB=$($REDIS_CONFIG.DB)",
        "SESSION_SECRET_KEY=$($SECURITY_CONFIG.SESSION_SECRET)",
        "CSRF_SECRET_KEY=$($SECURITY_CONFIG.CSRF_SECRET)",
        "ENVIRONMENT=production"
    )

    $envVarString = ($backendEnvVars | ForEach-Object { "--set-env-vars `"$_`"" }) -join " "

    $deployCommand = @"
gcloud run deploy $SERVICE_PREFIX-backend ``
    --image `"$backendImage`" ``
    --platform managed ``
    --region $Region ``
    --allow-unauthenticated ``
    --port 8080 ``
    --memory 1Gi ``
    --cpu 1 ``
    --concurrency 100 ``
    --timeout 300 ``
    --max-instances 10 ``
    $envVarString
"@

    if (!(Invoke-SafeCommand $deployCommand "Deploying backend")) {
        Write-Error "Backend deployment failed"
        exit 1
    }

    Write-Success "Backend deployed successfully"
}

# Get backend URL for frontend configuration
$backendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)' 2>$null
if ($backendUrl) {
    $websocketUrl = ($backendUrl -replace "https:", "wss:") + "/ws"
    Write-Success "Backend URL: $backendUrl"
    Write-Success "WebSocket URL: $websocketUrl"
} else {
    Write-Warning "Could not retrieve backend URL"
    $websocketUrl = "wss://$SERVICE_PREFIX-backend-placeholder.run.app/ws"
}

# Deploy Frontend
if (!$BackendOnly) {
    Write-Host "   Deploying frontend service..."

    $frontendEnvVars = @(
        "REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID",
        "REACT_APP_API_URL=$websocketUrl",
        "REACT_APP_ENV=production"
    )

    $frontendEnvVarString = ($frontendEnvVars | ForEach-Object { "--set-env-vars `"$_`"" }) -join " "

    $frontendDeployCommand = @"
gcloud run deploy $SERVICE_PREFIX-frontend ``
    --image `"$frontendImage`" ``
    --platform managed ``
    --region $Region ``
    --allow-unauthenticated ``
    --port 8080 ``
    --memory 512Mi ``
    --cpu 1 ``
    --concurrency 1000 ``
    --timeout 300 ``
    --max-instances 10 ``
    $frontendEnvVarString
"@

    if (!(Invoke-SafeCommand $frontendDeployCommand "Deploying frontend")) {
        Write-Error "Frontend deployment failed"
        exit 1
    }

    Write-Success "Frontend deployed successfully"
}

# Step 6: Update Environment Files with Actual URLs
Write-Step "Updating Environment Files with Deployed URLs"

$finalBackendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)' 2>$null
$finalFrontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)' 2>$null
$finalWebsocketUrl = ($finalBackendUrl -replace "https:", "wss:") + "/ws"

if ($finalBackendUrl -and $finalFrontendUrl) {
    # Update app/.env.production with actual URLs
    $updatedFrontendEnv = @"
# HOLI Timesheets Frontend Production Environment Configuration

# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID

# API Configuration - Production Backend URL
REACT_APP_API_URL=$finalWebsocketUrl

# Environment
REACT_APP_ENV=production

# Build Configuration
GENERATE_SOURCEMAP=false
INLINE_RUNTIME_CHUNK=false
"@

    $updatedFrontendEnv | Out-File -FilePath "app\.env.production" -Encoding UTF8
    Write-Success "Updated app/.env.production with actual WebSocket URL"

    # Update app/public/env-config.js with actual URLs
    $updatedEnvConfig = @"
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
    : "$finalWebsocketUrl",
  REACT_APP_ENV: (isLocalDevelopment || forceLocalMode) ? "development" : "production"
};

console.log('env-config.js loaded:', window._env_);
"@

    $updatedEnvConfig | Out-File -FilePath "app\public\env-config.js" -Encoding UTF8
    Write-Success "Updated app/public/env-config.js with actual WebSocket URL"
}

# Step 7: Final Summary
Write-Header "Deployment Complete!"

Write-Host "`n📋 Deployment Summary:" -ForegroundColor Cyan
Write-Host "   Project ID: $ProjectId" -ForegroundColor White
Write-Host "   Region: $Region" -ForegroundColor White
Write-Host "   Google Client ID: $GOOGLE_CLIENT_ID" -ForegroundColor White

if ($finalFrontendUrl) {
    Write-Host "`n🌐 Application URLs:" -ForegroundColor Cyan
    Write-Host "   Frontend: $finalFrontendUrl" -ForegroundColor Green
}

if ($finalBackendUrl) {
    Write-Host "   Backend: $finalBackendUrl" -ForegroundColor Green
    Write-Host "   WebSocket: $finalWebsocketUrl" -ForegroundColor Green
    Write-Host "   Health Check: $finalBackendUrl/health" -ForegroundColor Green
}

Write-Host "`n🔧 Configuration Fixed:" -ForegroundColor Cyan
Write-Host "   ✅ Fixed malformed WebSocket URL in app/.env.production" -ForegroundColor Green
Write-Host "   ✅ Standardized service names to '$SERVICE_PREFIX-*'" -ForegroundColor Green
Write-Host "   ✅ Updated all environment files with consistent Google Client ID" -ForegroundColor Green
Write-Host "   ✅ Rebuilt containers locally with Docker Desktop" -ForegroundColor Green
Write-Host "   ✅ Deployed to Cloud Run with consistent configuration" -ForegroundColor Green

Write-Host "`n📝 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Test the application at: $finalFrontendUrl" -ForegroundColor White
Write-Host "   2. Verify Google OAuth login works correctly" -ForegroundColor White
Write-Host "   3. Check that WebSocket connection is established" -ForegroundColor White
Write-Host "   4. Monitor logs: gcloud logs tail --follow --service=$SERVICE_PREFIX-backend" -ForegroundColor White

Write-Success "`n🎉 HOLI Timesheets deployment completed successfully!"
