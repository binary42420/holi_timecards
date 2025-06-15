#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Retry deployment with fixed environment variables
    
.DESCRIPTION
    This script retries the Cloud Run deployment with the corrected environment variables
    (removing reserved variables like PORT and HOST)
#>

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1",
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

# Configuration
$GOOGLE_CLIENT_ID = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
$SERVICE_PREFIX = "holi-timesheets"
$REGISTRY = "$Region-docker.pkg.dev/$ProjectId/holi-timesheets-repo"

# Get the latest image tags
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backendImage = "$REGISTRY/$SERVICE_PREFIX-backend:20250614-200324"  # Use the existing built image
$frontendImage = "$REGISTRY/$SERVICE_PREFIX-frontend:20250614-200324"  # Use the existing built image

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

function Invoke-SafeCommand($command, $description) {
    Write-Host "   Running: $description" -ForegroundColor Gray
    
    try {
        $result = Invoke-Expression $command
        if ($LASTEXITCODE -ne 0) {
            Write-Error "Command failed: $command"
            return $false
        }
        return $true
    } catch {
        Write-Error "Exception running command: $($_.Exception.Message)"
        return $false
    }
}

Write-Header "Retrying HOLI Timesheets Deployment (Fixed)"

# Deploy Backend
if (!$FrontendOnly) {
    Write-Step "Deploying Backend Service (Fixed Environment Variables)"
    
    # FIXED: Removed PORT and HOST environment variables (reserved by Cloud Run)
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
    
    $deployCommand = "gcloud run deploy $SERVICE_PREFIX-backend --image `"$backendImage`" --platform managed --region $Region --allow-unauthenticated --port 8080 --memory 1Gi --cpu 1 --concurrency 100 --timeout 300 --max-instances 10 $envVarString"
    
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
    Write-Step "Deploying Frontend Service (Fixed Environment Variables)"
    
    # FIXED: Removed PORT environment variable (reserved by Cloud Run)
    $frontendEnvVars = @(
        "REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID",
        "REACT_APP_API_URL=$websocketUrl",
        "REACT_APP_ENV=production"
    )
    
    $frontendEnvVarString = ($frontendEnvVars | ForEach-Object { "--set-env-vars `"$_`"" }) -join " "
    
    $frontendDeployCommand = "gcloud run deploy $SERVICE_PREFIX-frontend --image `"$frontendImage`" --platform managed --region $Region --allow-unauthenticated --port 8080 --memory 512Mi --cpu 1 --concurrency 1000 --timeout 300 --max-instances 10 $frontendEnvVarString"
    
    if (!(Invoke-SafeCommand $frontendDeployCommand "Deploying frontend")) {
        Write-Error "Frontend deployment failed"
        exit 1
    }
    
    Write-Success "Frontend deployed successfully"
}

# Final Summary
Write-Header "Deployment Complete!"

$finalBackendUrl = gcloud run services describe "$SERVICE_PREFIX-backend" --platform managed --region $Region --format 'value(status.url)' 2>$null
$finalFrontendUrl = gcloud run services describe "$SERVICE_PREFIX-frontend" --platform managed --region $Region --format 'value(status.url)' 2>$null
$finalWebsocketUrl = ($finalBackendUrl -replace "https:", "wss:") + "/ws"

Write-Host "`n📋 Deployment Summary:" -ForegroundColor Cyan
Write-Host "   Project ID: $ProjectId" -ForegroundColor White
Write-Host "   Region: $Region" -ForegroundColor White

if ($finalFrontendUrl) {
    Write-Host "`n🌐 Application URLs:" -ForegroundColor Cyan
    Write-Host "   Frontend: $finalFrontendUrl" -ForegroundColor Green
}

if ($finalBackendUrl) {
    Write-Host "   Backend: $finalBackendUrl" -ForegroundColor Green
    Write-Host "   WebSocket: $finalWebsocketUrl" -ForegroundColor Green
    Write-Host "   Health Check: $finalBackendUrl/health" -ForegroundColor Green
}

Write-Host "`n🔧 Issues Fixed:" -ForegroundColor Cyan
Write-Host "   ✅ Removed reserved PORT environment variable" -ForegroundColor Green
Write-Host "   ✅ Removed reserved HOST environment variable" -ForegroundColor Green
Write-Host "   ✅ Fixed Dockerfile casing (FROM ... AS)" -ForegroundColor Green

Write-Success "`n🎉 HOLI Timesheets deployment completed successfully!"
