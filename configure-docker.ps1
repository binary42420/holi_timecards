# Configure Docker for Artifact Registry
param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

Write-Host "🔧 Configuring Docker for Artifact Registry" -ForegroundColor Green

# Configure Docker authentication for Artifact Registry
Write-Host "🔐 Configuring Docker authentication..." -ForegroundColor Yellow
gcloud auth configure-docker "$Region-docker.pkg.dev"

Write-Host "✅ Docker authentication configured for Artifact Registry" -ForegroundColor Green
Write-Host "You can now run: .\deploy.ps1" -ForegroundColor Blue
