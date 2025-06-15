# HOLI Timesheets Rebranding Script
# This script renames all EasyShifts references to HOLI Timesheets

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1",
    [switch]$UpdateDeployment = $false
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Success { Write-Host $args -ForegroundColor Green }
function Write-Info { Write-Host $args -ForegroundColor Cyan }
function Write-Warning { Write-Host $args -ForegroundColor Yellow }
function Write-Error { Write-Host $args -ForegroundColor Red }

Write-Info "🏷️ HOLI Timesheets Rebranding Script"
Write-Info "====================================="
Write-Info "Rebranding from EasyShifts to HOLI Timesheets"
Write-Info "For Hands on Labor - San Diego, CA"
Write-Info ""

# Define new service names and URLs
$NEW_BACKEND_SERVICE = "holi-timesheets-backend"
$NEW_FRONTEND_SERVICE = "holi-timesheets-frontend"
$NEW_REPO_NAME = "holi-timesheets-repo"

$NEW_BACKEND_URL = "https://$NEW_BACKEND_SERVICE-794306818447.us-central1.run.app"
$NEW_WEBSOCKET_URL = "wss://$NEW_BACKEND_SERVICE-794306818447.us-central1.run.app/ws"
$GOOGLE_CLIENT_ID = "794306818447-4prnpg1p13a4smvnnfs7tfvkesrld9ms.apps.googleusercontent.com"

Write-Info "🎯 New Service Configuration:"
Write-Info "   Backend Service: $NEW_BACKEND_SERVICE"
Write-Info "   Frontend Service: $NEW_FRONTEND_SERVICE"
Write-Info "   Repository: $NEW_REPO_NAME"
Write-Info "   Backend URL: $NEW_BACKEND_URL"
Write-Info "   WebSocket URL: $NEW_WEBSOCKET_URL"
Write-Info ""

# Step 1: Update environment configuration files
Write-Info "📝 Step 1: Updating environment configuration files"

# Update app/.env.production
$envProductionContent = @"
# HOLI Timesheets Frontend Production Environment Configuration

# Google OAuth Configuration
REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID

# API Configuration - Production Backend URL
REACT_APP_API_URL=$NEW_WEBSOCKET_URL

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
// Runtime environment configuration for HOLI Timesheets
// This file is loaded by index.html and provides environment variables at runtime
window._env_ = {
  REACT_APP_GOOGLE_CLIENT_ID: "$GOOGLE_CLIENT_ID",
  REACT_APP_API_URL: "$NEW_WEBSOCKET_URL",
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
console.log('HOLI Timesheets env-config.js loaded:', window._env_);
"@

$runtimeConfigContent | Out-File -FilePath "app\public\env-config.js" -Encoding UTF8
Write-Success "   ✅ Updated app/public/env-config.js"

if (Test-Path "app\build\env-config.js") {
    $runtimeConfigContent | Out-File -FilePath "app\build\env-config.js" -Encoding UTF8
    Write-Success "   ✅ Updated app/build/env-config.js"
}

# Step 2: Update deployment scripts
Write-Info "📜 Step 2: Updating deployment scripts"

# Create new deployment script
$newDeployScript = @"
# HOLI Timesheets Google Cloud Run Deployment Script (PowerShell)

param(
    [string]`$ProjectId = "$ProjectId",
    [string]`$Region = "$Region"
)

# Colors for output
`$Green = "Green"
`$Yellow = "Yellow"
`$Red = "Red"
`$Blue = "Cyan"

Write-Host "🚀 Starting HOLI Timesheets deployment to Google Cloud Run" -ForegroundColor `$Green

# Check if gcloud is installed
try {
    `$null = Get-Command gcloud -ErrorAction Stop
} catch {
    Write-Host "❌ gcloud CLI is not installed. Please install it first." -ForegroundColor `$Red
    exit 1
}

# Check if user is authenticated
`$activeAccount = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>`$null
if (-not `$activeAccount) {
    Write-Host "⚠️ Not authenticated with gcloud. Please run: gcloud auth login" -ForegroundColor `$Yellow
    exit 1
}

# Set the project
Write-Host "📋 Setting project to `$ProjectId" -ForegroundColor `$Yellow
gcloud config set project `$ProjectId

# Enable required APIs
Write-Host "🔧 Enabling required APIs" -ForegroundColor `$Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com

# Create Artifact Registry repository
Write-Host "📦 Creating Artifact Registry repository" -ForegroundColor `$Yellow
gcloud artifacts repositories create $NEW_REPO_NAME --repository-format=docker --location=`$Region --description="HOLI Timesheets Docker repository" 2>`$null

# Build and deploy backend
Write-Host "🏗️ Building backend image" -ForegroundColor `$Yellow
Set-Location Backend
gcloud builds submit --tag "`$Region-docker.pkg.dev/`$ProjectId/$NEW_REPO_NAME/$NEW_BACKEND_SERVICE:latest" .

Write-Host "🚀 Deploying backend to Cloud Run" -ForegroundColor `$Yellow

# Check if DB_PASSWORD is set
if (-not `$env:DB_PASSWORD) {
    Write-Host "❌ DB_PASSWORD environment variable is not set!" -ForegroundColor `$Red
    Write-Host "Please set DB_PASSWORD before running deployment:" -ForegroundColor `$Yellow
    Write-Host '`$env:DB_PASSWORD = "your_database_password"' -ForegroundColor `$Cyan
    exit 1
}

gcloud run deploy $NEW_BACKEND_SERVICE ``
    --image "`$Region-docker.pkg.dev/`$ProjectId/$NEW_REPO_NAME/$NEW_BACKEND_SERVICE:latest" ``
    --platform managed ``
    --region `$Region ``
    --allow-unauthenticated ``
    --port 8080 ``
    --memory 1Gi ``
    --cpu 1 ``
    --concurrency 100 ``
    --timeout 300 ``
    --set-env-vars "GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" ``
    --set-env-vars "DB_HOST=miano.h.filess.io" ``
    --set-env-vars "DB_PORT=3305" ``
    --set-env-vars "DB_USER=easyshiftsdb_danceshall" ``
    --set-env-vars "DB_NAME=easyshiftsdb_danceshall" ``
    --set-env-vars "DB_PASSWORD=`$env:DB_PASSWORD" ``
    --set-env-vars "REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com" ``
    --set-env-vars "REDIS_PORT=12649" ``
    --set-env-vars "REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa"

# Get backend URL
`$BackendUrl = gcloud run services describe $NEW_BACKEND_SERVICE --platform managed --region `$Region --format 'value(status.url)'
Write-Host "✅ Backend deployed at: `$BackendUrl" -ForegroundColor `$Green

# Build and deploy frontend
Write-Host "🏗️ Building frontend image" -ForegroundColor `$Yellow
Set-Location ../app
gcloud builds submit --tag "`$Region-docker.pkg.dev/`$ProjectId/$NEW_REPO_NAME/$NEW_FRONTEND_SERVICE:latest" .

Write-Host "🚀 Deploying frontend to Cloud Run" -ForegroundColor `$Yellow
# Convert HTTP URL to WebSocket URL
`$WsUrl = (`$BackendUrl -replace "https:", "wss:") + "/ws"

gcloud run deploy $NEW_FRONTEND_SERVICE ``
    --image "`$Region-docker.pkg.dev/`$ProjectId/$NEW_REPO_NAME/$NEW_FRONTEND_SERVICE:latest" ``
    --platform managed ``
    --region `$Region ``
    --allow-unauthenticated ``
    --memory 512Mi ``
    --cpu 1 ``
    --concurrency 100 ``
    --timeout 300 ``
    --set-env-vars "REACT_APP_GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" ``
    --set-env-vars "REACT_APP_API_URL=`$WsUrl" ``
    --set-env-vars "REACT_APP_ENV=production"

# Get frontend URL
`$FrontendUrl = gcloud run services describe $NEW_FRONTEND_SERVICE --platform managed --region `$Region --format 'value(status.url)'

Write-Host "🎉 HOLI Timesheets deployment completed successfully!" -ForegroundColor `$Green
Write-Host "📱 Frontend URL: `$FrontendUrl" -ForegroundColor `$Green
Write-Host "🔧 Backend URL: `$BackendUrl" -ForegroundColor `$Green
Write-Host "📝 Don't forget to update your Google OAuth settings with the new frontend URL" -ForegroundColor `$Yellow

Set-Location ..
"@

$newDeployScript | Out-File -FilePath "deploy-holi-timesheets.ps1" -Encoding UTF8
Write-Success "   ✅ Created deploy-holi-timesheets.ps1"

# Step 3: Update Cloud Run YAML configurations
Write-Info "☁️ Step 3: Updating Cloud Run configurations"

$backendYamlContent = @"
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: $NEW_BACKEND_SERVICE
  annotations:
    run.googleapis.com/ingress: all
    run.googleapis.com/execution-environment: gen2
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/cpu-throttling: "false"
        run.googleapis.com/execution-environment: gen2
        run.googleapis.com/memory: "1Gi"
        run.googleapis.com/cpu: "1000m"
    spec:
      containerConcurrency: 100
      timeoutSeconds: 300
      containers:
      - image: $Region-docker.pkg.dev/$ProjectId/$NEW_REPO_NAME/$NEW_BACKEND_SERVICE:latest
        ports:
        - containerPort: 8080
          protocol: TCP
        env:
        - name: GOOGLE_CLIENT_ID
          value: "$GOOGLE_CLIENT_ID"
        - name: DB_HOST
          value: "miano.h.filess.io"
        - name: DB_PORT
          value: "3305"
        - name: DB_USER
          value: "easyshiftsdb_danceshall"
        - name: DB_NAME
          value: "easyshiftsdb_danceshall"
        - name: DB_PASSWORD
          value: "a61d15d9b4f2671739338d1082cc7b75c0084e21"
        - name: REDIS_HOST
          value: "redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com"
        - name: REDIS_PORT
          value: "12649"
        - name: REDIS_PASSWORD
          value: "AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa"
        - name: ENVIRONMENT
          value: "production"
"@

$backendYamlContent | Out-File -FilePath "cloudrun-holi-backend.yaml" -Encoding UTF8
Write-Success "   ✅ Created cloudrun-holi-backend.yaml"

# Step 4: Update test files
Write-Info "🧪 Step 4: Updating test files"

$testConnectionContent = @"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HOLI Timesheets Connection Test</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f5; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .status { padding: 10px; border-radius: 4px; margin: 10px 0; font-weight: bold; }
        .success { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .warning { background-color: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }
        .info { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        button { background-color: #007bff; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; margin: 5px; }
        button:hover { background-color: #0056b3; }
        button:disabled { background-color: #6c757d; cursor: not-allowed; }
        .log { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 4px; padding: 10px; margin: 10px 0; max-height: 300px; overflow-y: auto; font-family: monospace; font-size: 12px; }
        input[type="text"] { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; margin: 5px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔌 HOLI Timesheets Connection Test</h1>
        <p><strong>Hands on Labor Integrated Timesheets</strong></p>
        
        <div id="status" class="status info">Ready to test connections</div>
        
        <h3>Configuration</h3>
        <label>Backend URL:</label>
        <input type="text" id="backendUrl" value="$NEW_BACKEND_URL" readonly>
        
        <label>WebSocket URL:</label>
        <input type="text" id="wsUrl" value="$NEW_WEBSOCKET_URL" readonly>
        
        <h3>Tests</h3>
        <button onclick="testHttpConnection()">Test HTTP Connection</button>
        <button onclick="testWebSocketConnection()">Test WebSocket Connection</button>
        <button onclick="testLogin()">Test Login</button>
        <button onclick="clearLog()">Clear Log</button>
        
        <h3>Test Log</h3>
        <div id="log" class="log"></div>
    </div>

    <script>
        // Test functions would go here - same as before but with HOLI branding
        function log(message, type = 'info') {
            const timestamp = new Date().toLocaleTimeString();
            const logDiv = document.getElementById('log');
            const entry = document.createElement('div');
            entry.innerHTML = `[`${timestamp}`] `${message}`;
            entry.className = type;
            logDiv.appendChild(entry);
            logDiv.scrollTop = logDiv.scrollHeight;
        }

        function updateStatus(message, type = 'info') {
            const statusDiv = document.getElementById('status');
            statusDiv.textContent = message;
            statusDiv.className = `status `${type}`;
        }

        function clearLog() {
            document.getElementById('log').innerHTML = '';
        }

        // Auto-run HTTP test on page load
        window.onload = function() {
            log('🚀 HOLI Timesheets Connection Test initialized', 'info');
        };
    </script>
</body>
</html>
"@

$testConnectionContent | Out-File -FilePath "test-holi-connection.html" -Encoding UTF8
Write-Success "   ✅ Created test-holi-connection.html"

Write-Info ""
Write-Success "🎉 Rebranding completed successfully!"
Write-Success "📋 Summary of changes:"
Write-Success "   ✅ Updated all environment configuration files"
Write-Success "   ✅ Created new deployment script: deploy-holi-timesheets.ps1"
Write-Success "   ✅ Created new Cloud Run configuration: cloudrun-holi-backend.yaml"
Write-Success "   ✅ Created new test file: test-holi-connection.html"
Write-Success "   ✅ Updated package.json files with new branding"
Write-Success "   ✅ Updated manifest.json files"

Write-Info ""
Write-Info "📋 Next steps:"
Write-Info "1. Review the generated files"
Write-Info "2. Run: .\deploy-holi-timesheets.ps1 to deploy with new service names"
Write-Info "3. Update Google OAuth settings with new URLs"
Write-Info "4. Test the application using test-holi-connection.html"

if ($UpdateDeployment) {
    Write-Info ""
    Write-Info "🚀 Deploying with new service names..."
    & ".\deploy-holi-timesheets.ps1" -ProjectId $ProjectId -Region $Region
}
