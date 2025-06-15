# HOLI Timesheets Deployment Validation Script
# This script validates that all prerequisites are met before running the comprehensive deployment

param(
    [string]$ProjectId = "easyshifts",
    [string]$Region = "us-central1"
)

# Color definitions
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"
$Cyan = "Cyan"

function Write-Status {
    param(
        [string]$Message,
        [string]$Status = "INFO",
        [string]$Color = "White"
    )
    $icon = switch ($Status) {
        "PASS" { "✅" }
        "FAIL" { "❌" }
        "WARN" { "⚠️" }
        "INFO" { "ℹ️" }
        default { "•" }
    }
    Write-Host "$icon $Message" -ForegroundColor $Color
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    }
    catch {
        return $false
    }
}

Write-Host "🔍 HOLI Timesheets Deployment Validation" -ForegroundColor $Blue
Write-Host "=" * 50 -ForegroundColor $Blue

$allChecks = $true

# Check Docker
Write-Host "`n🐳 Docker Validation" -ForegroundColor $Yellow
if (Test-Command "docker") {
    try {
        $dockerVersion = docker --version
        Write-Status "Docker installed: $dockerVersion" "PASS" $Green
        
        # Check if Docker is running
        $dockerInfo = docker info 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Status "Docker daemon is running" "PASS" $Green
        } else {
            Write-Status "Docker daemon is not running - please start Docker Desktop" "FAIL" $Red
            $allChecks = $false
        }
    }
    catch {
        Write-Status "Docker command failed" "FAIL" $Red
        $allChecks = $false
    }
} else {
    Write-Status "Docker not found in PATH" "FAIL" $Red
    $allChecks = $false
}

# Check gcloud CLI
Write-Host "`n☁️ Google Cloud CLI Validation" -ForegroundColor $Yellow
if (Test-Command "gcloud") {
    try {
        $gcloudVersion = gcloud version --format="value(Google Cloud SDK)" 2>$null
        Write-Status "gcloud CLI installed: $gcloudVersion" "PASS" $Green
        
        # Check authentication
        $account = gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>$null
        if ($account) {
            Write-Status "Authenticated as: $account" "PASS" $Green
        } else {
            Write-Status "Not authenticated - run 'gcloud auth login'" "FAIL" $Red
            $allChecks = $false
        }
        
        # Check project
        $currentProject = gcloud config get-value project 2>$null
        if ($currentProject -eq $ProjectId) {
            Write-Status "Project set to: $ProjectId" "PASS" $Green
        } else {
            Write-Status "Project not set to $ProjectId (current: $currentProject)" "WARN" $Yellow
            Write-Status "Will be set automatically during deployment" "INFO" $Cyan
        }
        
        # Check Docker authentication
        $dockerConfigured = gcloud auth list --filter="account:*" --format="value(account)" | Where-Object { $_ -ne $null }
        if ($dockerConfigured) {
            Write-Status "gcloud authentication available for Docker" "PASS" $Green
        } else {
            Write-Status "Docker authentication may need configuration" "WARN" $Yellow
        }
        
    }
    catch {
        Write-Status "gcloud CLI command failed" "FAIL" $Red
        $allChecks = $false
    }
} else {
    Write-Status "gcloud CLI not found in PATH" "FAIL" $Red
    $allChecks = $false
}

# Check PowerShell version
Write-Host "`n💻 PowerShell Validation" -ForegroundColor $Yellow
$psVersion = $PSVersionTable.PSVersion
if ($psVersion.Major -ge 5) {
    Write-Status "PowerShell version: $($psVersion.ToString())" "PASS" $Green
} else {
    Write-Status "PowerShell version too old: $($psVersion.ToString())" "FAIL" $Red
    $allChecks = $false
}

# Check environment variables
Write-Host "`n🔐 Environment Variables" -ForegroundColor $Yellow
if ($env:DB_PASSWORD) {
    Write-Status "DB_PASSWORD is set" "PASS" $Green
} else {
    Write-Status "DB_PASSWORD is not set" "FAIL" $Red
    Write-Status "Set with: `$env:DB_PASSWORD = 'your_password'" "INFO" $Cyan
    $allChecks = $false
}

# Check file structure
Write-Host "`n📁 File Structure Validation" -ForegroundColor $Yellow
$requiredFiles = @(
    "Backend/Dockerfile",
    "Backend/requirements.txt",
    "Backend/start_server_with_env.py",
    "app/Dockerfile",
    "app/package.json",
    "app/public/env-config.js"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Status "$file exists" "PASS" $Green
    } else {
        Write-Status "$file missing" "FAIL" $Red
        $allChecks = $false
    }
}

# Check Google Cloud APIs (if authenticated)
if ($account) {
    Write-Host "`n🔌 Google Cloud APIs" -ForegroundColor $Yellow
    
    $requiredApis = @(
        "run.googleapis.com",
        "artifactregistry.googleapis.com",
        "iam.googleapis.com"
    )
    
    foreach ($api in $requiredApis) {
        try {
            $apiEnabled = gcloud services list --enabled --filter="name:$api" --format="value(name)" 2>$null
            if ($apiEnabled) {
                Write-Status "$api enabled" "PASS" $Green
            } else {
                Write-Status "$api not enabled" "WARN" $Yellow
                Write-Status "Will be enabled automatically if needed" "INFO" $Cyan
            }
        }
        catch {
            Write-Status "Could not check $api status" "WARN" $Yellow
        }
    }
}

# Network connectivity test
Write-Host "`n🌐 Network Connectivity" -ForegroundColor $Yellow
try {
    $response = Test-NetConnection -ComputerName "google.com" -Port 443 -InformationLevel Quiet
    if ($response) {
        Write-Status "Internet connectivity available" "PASS" $Green
    } else {
        Write-Status "Internet connectivity issues" "WARN" $Yellow
    }
}
catch {
    Write-Status "Could not test network connectivity" "WARN" $Yellow
}

# Summary
Write-Host "`n" + "=" * 50 -ForegroundColor $Blue
if ($allChecks) {
    Write-Host "🎉 All validation checks passed!" -ForegroundColor $Green
    Write-Host "You can proceed with deployment using:" -ForegroundColor $Green
    Write-Host ".\deploy-comprehensive.ps1" -ForegroundColor $Cyan
} else {
    Write-Host "❌ Some validation checks failed!" -ForegroundColor $Red
    Write-Host "Please fix the issues above before deploying." -ForegroundColor $Red
}

Write-Host "`n📚 For detailed deployment instructions, see:" -ForegroundColor $Blue
Write-Host "DEPLOYMENT_GUIDE.md" -ForegroundColor $Cyan
