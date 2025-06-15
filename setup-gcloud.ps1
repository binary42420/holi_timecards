# HOLI Timesheets Google Cloud Setup Script (PowerShell)
# This script sets up your Google Cloud environment for HOLI Timesheets deployment

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1",
    [string]$DbPassword,
    [string]$GoogleClientId = "444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com"
)

# Colors for output
$Green = "Green"
$Yellow = "Yellow"
$Red = "Red"
$Blue = "Cyan"

Write-Host "🚀 Holi Timesheets Google Cloud Setup" -ForegroundColor $Green
Write-Host "This script will help you set up Google Cloud for EasyShifts deployment" -ForegroundColor $Blue

# Check if gcloud is installed
try {
    $null = Get-Command gcloud -ErrorAction Stop
} catch {
    Write-Host "❌ gcloud CLI is not installed." -ForegroundColor $Red
    Write-Host "Please install it from: https://cloud.google.com/sdk/docs/install" -ForegroundColor $Yellow
    exit 1
}

# Get project ID if not provided
if (-not $ProjectId) {
    $ProjectId = Read-Host "📋 Please enter your Google Cloud Project ID"
    if (-not $ProjectId) {
        Write-Host "❌ Project ID cannot be empty" -ForegroundColor $Red
        exit 1
    }
}

# Get region if not provided
if (-not $Region) {
    $RegionInput = Read-Host "🌍 Please enter your preferred region (default: us-central1)"
    if ($RegionInput) {
        $Region = $RegionInput
    }
}

# Get database password if not provided
if (-not $DbPassword) {
    $SecurePassword = Read-Host "🔐 Please enter your database password" -AsSecureString
    $DbPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($SecurePassword))
    if (-not $DbPassword) {
        Write-Host "❌ Database password cannot be empty" -ForegroundColor $Red
        exit 1
    }
}

Write-Host "✅ Configuration collected" -ForegroundColor $Green
Write-Host "Project ID: $ProjectId" -ForegroundColor $Blue
Write-Host "Region: $Region" -ForegroundColor $Blue
Write-Host "Google Client ID: $GoogleClientId" -ForegroundColor $Blue

# Authenticate with gcloud
Write-Host "🔐 Authenticating with Google Cloud..." -ForegroundColor $Yellow
gcloud auth login

# Set the project
Write-Host "📋 Setting project to $ProjectId" -ForegroundColor $Yellow
gcloud config set project $ProjectId

# Enable required APIs
Write-Host "🔧 Enabling required APIs..." -ForegroundColor $Yellow
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create database password secret
Write-Host "🔐 Creating database password secret..." -ForegroundColor $Yellow
$DbPassword | gcloud secrets create db-password --data-file=-

# Create Google OAuth client ID secret
Write-Host "🔐 Creating Google OAuth client ID secret..." -ForegroundColor $Yellow
$GoogleClientId | gcloud secrets create google-client-id --data-file=-

# Create service account
Write-Host "👤 Creating service account..." -ForegroundColor $Yellow
gcloud iam service-accounts create holi-sa --display-name="Holi Service Account" --description="Service account for Holi application"

# Grant necessary permissions
$ServiceAccount = "holi-sa@$ProjectId.iam.gserviceaccount.com"

Write-Host "🔑 Granting permissions..." -ForegroundColor $Yellow
gcloud projects add-iam-policy-binding $ProjectId --member="serviceAccount:$ServiceAccount" --role="roles/secretmanager.secretAccessor"
gcloud projects add-iam-policy-binding $ProjectId --member="serviceAccount:$ServiceAccount" --role="roles/cloudsql.client"

# Update deployment script with project details
Write-Host "📝 Updating deployment script..." -ForegroundColor $Yellow
$deployContent = Get-Content deploy.sh -Raw
$deployContent = $deployContent -replace 'PROJECT_ID="your-project-id"', "PROJECT_ID=`"$ProjectId`""
$deployContent = $deployContent -replace 'REGION="us-central1"', "REGION=`"$Region`""
$deployContent | Set-Content deploy.sh

# Update Cloud Run YAML files
Write-Host "📝 Updating Cloud Run configurations..." -ForegroundColor $Yellow
$backendYaml = Get-Content cloudrun-backend.yaml -Raw
$backendYaml = $backendYaml -replace 'PROJECT_ID', $ProjectId
$backendYaml | Set-Content cloudrun-backend.yaml

$frontendYaml = Get-Content cloudrun-frontend.yaml -Raw
$frontendYaml = $frontendYaml -replace 'PROJECT_ID', $ProjectId
$frontendYaml | Set-Content cloudrun-frontend.yaml

Write-Host "🎉 Setup completed successfully!" -ForegroundColor $Green
Write-Host "✅ APIs enabled" -ForegroundColor $Green
Write-Host "✅ Service account created" -ForegroundColor $Green
Write-Host "✅ Database password stored in Secret Manager" -ForegroundColor $Green
Write-Host "✅ Google OAuth client ID stored in Secret Manager" -ForegroundColor $Green
Write-Host "✅ Deployment scripts updated" -ForegroundColor $Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor $Yellow
Write-Host "1. Make sure your Google OAuth settings include your Cloud Run URLs" -ForegroundColor $Blue
Write-Host "2. Run: .\deploy.ps1" -ForegroundColor $Blue
Write-Host ""
Write-Host "🔗 Important URLs to add to Google OAuth:" -ForegroundColor $Yellow
Write-Host "   - https://holi-timesheets-frontend-2ma525uu2a-uc.a.run.app" -ForegroundColor $Blue
Write-Host "   - https://holi-timesheets-backend-2ma525uu2a-uc.a.run.app" -ForegroundColor $Blue


