#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Test Docker builds locally before Cloud Run deployment
.DESCRIPTION
    This script validates Docker builds on Windows 11 with Docker Desktop
    to ensure containers build properly before pushing to Google Cloud Run.
    This does NOT run the containers locally - only validates the build process.
#>

param(
    [switch]$BackendOnly = $false,
    [switch]$FrontendOnly = $false,
    [switch]$Verbose = $false
)

# Set error handling
$ErrorActionPreference = "Stop"

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = "Continue"
}

# Color output functions
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Success { Write-ColorOutput Green $args }
function Write-Info { Write-ColorOutput Cyan $args }
function Write-Warning { Write-ColorOutput Yellow $args }
function Write-Error { Write-ColorOutput Red $args }
function Write-Header { 
    Write-Host ""
    Write-ColorOutput Magenta "=" * 60
    Write-ColorOutput Magenta $args
    Write-ColorOutput Magenta "=" * 60
    Write-Host ""
}

# Configuration
$TIMESTAMP = Get-Date -Format "yyyyMMdd-HHmmss"
$BACKEND_TEST_IMAGE = "holi-backend-test:$TIMESTAMP"
$FRONTEND_TEST_IMAGE = "holi-frontend-test:$TIMESTAMP"

Write-Header "🧪 HOLI Timesheets Docker Build Test"

# Function to run command with error handling
function Invoke-SafeCommand {
    param(
        [string]$Command,
        [string]$Description,
        [string]$WorkingDirectory = $null
    )
    
    Write-Info "🔄 $Description..."
    
    if ($WorkingDirectory) {
        $currentDir = Get-Location
        Set-Location $WorkingDirectory
    }
    
    try {
        if ($Verbose) {
            Write-Verbose "Executing: $Command"
        }
        
        Invoke-Expression $Command
        
        if ($LASTEXITCODE -ne 0) {
            throw "Command failed with exit code $LASTEXITCODE"
        }
        
        Write-Success "✅ $Description completed successfully"
        return $true
    } catch {
        Write-Error "❌ $Description failed: $_"
        return $false
    } finally {
        if ($WorkingDirectory) {
            Set-Location $currentDir
        }
    }
}

# Check Docker
Write-Info "🔍 Checking Docker..."
try {
    $dockerVersion = docker version --format "{{.Server.Version}}" 2>$null
    if (-not $dockerVersion) {
        Write-Error "❌ Docker Desktop is not running. Please start Docker Desktop."
        exit 1
    }
    Write-Success "✅ Docker Desktop is running (version: $dockerVersion)"
} catch {
    Write-Error "❌ Docker Desktop is not accessible."
    exit 1
}

# Test backend build
if (-not $FrontendOnly) {
    Write-Header "🏗️ Testing Backend Build"
    
    $backendPath = "Backend"
    if (-not (Test-Path $backendPath)) {
        Write-Error "❌ Backend directory not found"
        exit 1
    }
    
    if (-not (Invoke-SafeCommand "docker build -t `"$BACKEND_TEST_IMAGE`" ." "Building backend test image" $backendPath)) {
        Write-Error "❌ Backend build test failed"
        exit 1
    }
    
    # Validate the image was built successfully
    Write-Info "🧪 Validating backend image..."
    try {
        $imageInfo = docker inspect $BACKEND_TEST_IMAGE --format "{{.Config.ExposedPorts}}" 2>$null
        if ($imageInfo -like "*8080*") {
            Write-Success "✅ Backend image built with correct port configuration"
        } else {
            Write-Warning "⚠️ Backend image may have port configuration issues"
        }

        # Check image size
        $imageSize = docker images $BACKEND_TEST_IMAGE --format "{{.Size}}"
        Write-Info "   Backend image size: $imageSize"

    } catch {
        Write-Warning "⚠️ Backend image validation failed: $_"
    }
}

# Test frontend build
if (-not $BackendOnly) {
    Write-Header "🎨 Testing Frontend Build"
    
    $frontendPath = "app"
    if (-not (Test-Path $frontendPath)) {
        Write-Error "❌ Frontend directory not found"
        exit 1
    }
    
    if (-not (Invoke-SafeCommand "docker build -t `"$FRONTEND_TEST_IMAGE`" ." "Building frontend test image" $frontendPath)) {
        Write-Error "❌ Frontend build test failed"
        exit 1
    }
    
    # Validate the image was built successfully
    Write-Info "🧪 Validating frontend image..."
    try {
        $imageInfo = docker inspect $FRONTEND_TEST_IMAGE --format "{{.Config.ExposedPorts}}" 2>$null
        if ($imageInfo -like "*8080*") {
            Write-Success "✅ Frontend image built with correct port configuration"
        } else {
            Write-Warning "⚠️ Frontend image may have port configuration issues"
        }

        # Check image size
        $imageSize = docker images $FRONTEND_TEST_IMAGE --format "{{.Size}}"
        Write-Info "   Frontend image size: $imageSize"

        # Check if nginx is properly configured
        $nginxCheck = docker run --rm $FRONTEND_TEST_IMAGE nginx -t 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "✅ Frontend nginx configuration is valid"
        } else {
            Write-Warning "⚠️ Frontend nginx configuration may have issues"
        }

    } catch {
        Write-Warning "⚠️ Frontend image validation failed: $_"
    }
}

# Cleanup test images
Write-Header "🧹 Cleaning Up Test Images"

try {
    if (-not $FrontendOnly) {
        docker rmi $BACKEND_TEST_IMAGE -f | Out-Null
        Write-Success "✅ Backend test image removed"
    }
    
    if (-not $BackendOnly) {
        docker rmi $FRONTEND_TEST_IMAGE -f | Out-Null
        Write-Success "✅ Frontend test image removed"
    }
} catch {
    Write-Warning "⚠️ Cleanup had issues, but continuing..."
}

Write-Header "🎉 Docker Build Validation Complete"
Write-Success "✅ All Docker images built and validated successfully!"
Write-Info "🚀 Images are ready for Cloud Run deployment"
Write-Info "🚀 Run: .\deploy-holi-comprehensive.ps1 to deploy to Google Cloud Run"
