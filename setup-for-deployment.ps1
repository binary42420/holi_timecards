# HOLI Timecards - Pre-Deployment Setup Script
# This script helps you prepare your environment for Google Cloud Run deployment

Write-Host "🚀 HOLI Timecards - Pre-Deployment Setup" -ForegroundColor Green
Write-Host "=======================================" -ForegroundColor Green

# Check if running as Administrator (recommended for Docker)
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")
if (-not $isAdmin) {
    Write-Host "⚠️  Warning: Not running as Administrator. Some Docker operations may fail." -ForegroundColor Yellow
    Write-Host "   Consider running PowerShell as Administrator for best results." -ForegroundColor Yellow
}

Write-Host "`n1. Checking Prerequisites..." -ForegroundColor Yellow

# Check Docker
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
    
    # Check if Docker is running
    $dockerInfo = docker info 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Docker is running" -ForegroundColor Green
    } else {
        Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    Write-Host "   Download from: https://www.docker.com/products/docker-desktop" -ForegroundColor Cyan
    exit 1
}

# Check gcloud CLI
try {
    $gcloudVersion = gcloud version --format="value(Google Cloud SDK)" 2>$null
    if (-not $gcloudVersion) {
        $gcloudVersion = (gcloud version 2>$null | Select-String "Google Cloud SDK").ToString().Split()[-1]
    }
    Write-Host "✅ gcloud CLI found: $gcloudVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ gcloud CLI not found. Please install Google Cloud CLI." -ForegroundColor Red
    Write-Host "   Download from: https://cloud.google.com/sdk/docs/install" -ForegroundColor Cyan
    exit 1
}

Write-Host "`n2. Google Cloud Authentication..." -ForegroundColor Yellow

# Check authentication
try {
    $account = gcloud auth list --filter=status:ACTIVE --format="value(account)"
    if ($account) {
        Write-Host "✅ Authenticated as: $account" -ForegroundColor Green
    } else {
        Write-Host "❌ Not authenticated with Google Cloud." -ForegroundColor Red
        Write-Host "   Please run: gcloud auth login" -ForegroundColor Cyan
        exit 1
    }
} catch {
    Write-Host "❌ Authentication check failed." -ForegroundColor Red
    Write-Host "   Please run: gcloud auth login" -ForegroundColor Cyan
    exit 1
}

# Set project
Write-Host "`n3. Setting up Google Cloud Project..." -ForegroundColor Yellow
try {
    $currentProject = gcloud config get-value project
    if ($currentProject -ne "holitimecards") {
        Write-Host "Setting project to holitimecards..." -ForegroundColor Yellow
        gcloud config set project holitimecards
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to set project. Please ensure you have access to 'holitimecards' project." -ForegroundColor Red
            exit 1
        }
    }
    Write-Host "✅ Project set to: holitimecards" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to configure project." -ForegroundColor Red
    exit 1
}

# Enable required APIs
Write-Host "`n4. Enabling required Google Cloud APIs..." -ForegroundColor Yellow
$requiredApis = @(
    "run.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com"
)

foreach ($api in $requiredApis) {
    try {
        Write-Host "   Enabling $api..." -ForegroundColor Cyan
        gcloud services enable $api --quiet
        Write-Host "   ✅ $api enabled" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️ Failed to enable $api (may already be enabled)" -ForegroundColor Yellow
    }
}

# Configure Docker authentication
Write-Host "`n5. Configuring Docker authentication..." -ForegroundColor Yellow
try {
    gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
    Write-Host "✅ Docker authentication configured for Artifact Registry" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to configure Docker authentication" -ForegroundColor Red
    exit 1
}

# Check database password
Write-Host "`n6. Checking environment variables..." -ForegroundColor Yellow
if ($env:DB_PASSWORD) {
    Write-Host "✅ DB_PASSWORD is set" -ForegroundColor Green
} else {
    Write-Host "❌ DB_PASSWORD environment variable is not set." -ForegroundColor Red
    Write-Host "   Please set your database password:" -ForegroundColor Cyan
    Write-Host "   `$env:DB_PASSWORD = 'your_database_password_here'" -ForegroundColor Cyan
    Write-Host "`n   You can also add it to your PowerShell profile for persistence:" -ForegroundColor Yellow
    Write-Host "   Add this line to your PowerShell profile:" -ForegroundColor Yellow
    Write-Host "   `$env:DB_PASSWORD = 'your_database_password_here'" -ForegroundColor Cyan
    
    $setNow = Read-Host "`nWould you like to set DB_PASSWORD now? (y/n)"
    if ($setNow -eq 'y' -or $setNow -eq 'Y') {
        $dbPassword = Read-Host "Enter your database password" -AsSecureString
        $env:DB_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword))
        Write-Host "✅ DB_PASSWORD set for this session" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Please set DB_PASSWORD before running deployment" -ForegroundColor Yellow
    }
}

Write-Host "`n🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green

Write-Host "`n📋 Summary:" -ForegroundColor Blue
Write-Host "   ✅ Docker is ready" -ForegroundColor Green
Write-Host "   ✅ Google Cloud CLI is configured" -ForegroundColor Green
Write-Host "   ✅ Project set to 'holitimecards'" -ForegroundColor Green
Write-Host "   ✅ Required APIs are enabled" -ForegroundColor Green
Write-Host "   ✅ Docker authentication configured" -ForegroundColor Green

if ($env:DB_PASSWORD) {
    Write-Host "   ✅ Database password is set" -ForegroundColor Green
} else {
    Write-Host "   ⚠️ Database password needs to be set" -ForegroundColor Yellow
}

Write-Host "`n🚀 Ready for deployment!" -ForegroundColor Green
Write-Host "Run the deployment script:" -ForegroundColor Cyan
Write-Host "   .\deploy-holi-timecards.ps1" -ForegroundColor White
Write-Host "`nOr for backend only:" -ForegroundColor Cyan
Write-Host "   .\deploy-holi-timecards.ps1 -BackendOnly" -ForegroundColor White
Write-Host "`nOr for frontend only:" -ForegroundColor Cyan
Write-Host "   .\deploy-holi-timecards.ps1 -FrontendOnly" -ForegroundColor White

Write-Host "`n📚 Additional Resources:" -ForegroundColor Blue
Write-Host "   - Deployment Guide: .\DEPLOYMENT_GUIDE.md" -ForegroundColor Cyan
Write-Host "   - Google Cloud Console: https://console.cloud.google.com/run?project=holitimecards" -ForegroundColor Cyan
