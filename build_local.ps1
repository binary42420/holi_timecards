# build_local.ps1
# Comprehensive PowerShell script to build, run, and deploy both frontend and backend Docker images locally and to Google Cloud Run
# Usage: ./build_local.ps1 [-Run] [-Deploy] [-Region "us-central1"] [-Project "holitimecards"]
# - Now with Artifact Registry repo existence checks and Cloud Run URL output

param(
    [switch]$Run,
    [switch]$Deploy,
    [string]$Region = "us-central1",
    [string]$Project = "holitimecards"
)

$ErrorActionPreference = 'Stop'

$frontendDir = "app"
$backendDir = "Backend"
$frontendImage = "holi-timecards-app:local"
$backendImage = "holi-timecards-backend:local"
$frontendDockerfile = Join-Path $frontendDir "Dockerfile"
$backendDockerfile = Join-Path $backendDir "Dockerfile"

Write-Host "\n==== Checking Dockerfiles ===="
if (!(Test-Path $frontendDockerfile)) {
    Write-Error "No Dockerfile found in $frontendDir. Aborting."
    exit 1
}
if (!(Test-Path $backendDockerfile)) {
    Write-Error "No Dockerfile found in $backendDir. Aborting."
    exit 1
}

Write-Host "\n==== Building Frontend Docker Image ($frontendImage) ====" -ForegroundColor Cyan
try {
    docker build -t $frontendImage $frontendDir
    Write-Host "Frontend image built successfully." -ForegroundColor Green
} catch {
    Write-Error "Failed to build frontend image. $_"
    exit 1
}

Write-Host "\n==== Building Backend Docker Image ($backendImage) ====" -ForegroundColor Cyan
try {
    docker build -t $backendImage $backendDir
    Write-Host "Backend image built successfully." -ForegroundColor Green
} catch {
    Write-Error "Failed to build backend image. $_"
    exit 1
}

Write-Host "\n==== Built Docker Images ====" -ForegroundColor Yellow
docker images | Where-Object { $_.Repository -like 'holi-timecards-*' } | Format-Table Repository,Tag,ID,Size

# Deploy to Google Cloud Run if requested
if ($Deploy) {
    Write-Host "\n==== Ensuring Artifact Registry Repositories Exist ====" -ForegroundColor Cyan
    $reposToCheck = @('app', 'backend')
    foreach ($repo in $reposToCheck) {
        $repoExists = $false
        try {
            $check = gcloud artifacts repositories describe $repo --location=$Region --project=$Project 2>$null
            if ($LASTEXITCODE -eq 0) { $repoExists = $true }
        } catch {}
        if (-not $repoExists) {
            Write-Host "Creating Artifact Registry repo '$repo'..." -ForegroundColor Yellow
            gcloud artifacts repositories create $repo --repository-format=docker --location=$Region --project=$Project --description="$repo Docker repository"
            if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create repo $repo"; exit 1 }
        } else {
            Write-Host "Repo '$repo' exists." -ForegroundColor Green
        }
    }

    Write-Host "\n==== Tagging and Pushing Images to Artifact Registry ====" -ForegroundColor Cyan
    $frontendRemoteImage = "$Region-docker.pkg.dev/$Project/app/app:latest"
    $backendRemoteImage = "$Region-docker.pkg.dev/$Project/backend/backend:latest"

    try {
        Write-Host "Tagging frontend image..."
        docker tag $frontendImage $frontendRemoteImage
        Write-Host "Pushing frontend image to Artifact Registry..."
        docker push $frontendRemoteImage
        if ($LASTEXITCODE -ne 0) { throw "Failed to push frontend image." }
    } catch {
        Write-Error "Failed to tag or push frontend image. $_"
        exit 1
    }
    try {
        Write-Host "Tagging backend image..."
        docker tag $backendImage $backendRemoteImage
        Write-Host "Pushing backend image to Artifact Registry..."
        docker push $backendRemoteImage
        if ($LASTEXITCODE -ne 0) { throw "Failed to push backend image." }
    } catch {
        Write-Error "Failed to tag or push backend image. $_"
        exit 1
    }
    Write-Host "\n==== Deploying to Cloud Run ====" -ForegroundColor Cyan
    $frontendUrl = $null
    $backendUrl = $null
    try {
        Write-Host "Deploying frontend to Cloud Run..."
        $frontendDeploy = gcloud run deploy holi-timecards-app --image $frontendRemoteImage --platform managed --region $Region --project $Project --allow-unauthenticated --format="value(status.url)"
        $frontendUrl = $frontendDeploy.Trim()
        Write-Host "Deploying backend to Cloud Run..."
        $backendDeploy = gcloud run deploy holi-timecards-backend --image $backendRemoteImage --platform managed --region $Region --project $Project --allow-unauthenticated --format="value(status.url)"
        $backendUrl = $backendDeploy.Trim()
        Write-Host "\n==== Cloud Run Deployment Complete ====" -ForegroundColor Green
        if ($frontendUrl) { Write-Host "Frontend deployed at: $frontendUrl" -ForegroundColor Yellow }
        if ($backendUrl) { Write-Host "Backend deployed at:  $backendUrl" -ForegroundColor Yellow }
    } catch {
        Write-Error "Cloud Run deployment failed. $_"
        exit 1
    }
}

if ($Run) {
    Write-Host "\n==== Running Containers ====" -ForegroundColor Cyan
    # Stop any existing containers
    $frontendContainer = docker ps -q -f "name=holi-timecards-app-local"
    $backendContainer = docker ps -q -f "name=holi-timecards-backend-local"
    if ($frontendContainer) { docker stop $frontendContainer | Out-Null }
    if ($backendContainer) { docker stop $backendContainer | Out-Null }

    # Run frontend
    Write-Host "Starting frontend container on port 3000..." -ForegroundColor Green
    docker run --rm -d -p 3000:3000 --name holi-timecards-app-local $frontendImage
    # Run backend
    Write-Host "Starting backend container on port 8000..." -ForegroundColor Green
    docker run --rm -d -p 8000:8000 --name holi-timecards-backend-local $backendImage

    Write-Host "\n==== Containers running ====" -ForegroundColor Yellow
    docker ps | Where-Object { $_.Names -like 'holi-timecards-*' } | Format-Table Names,Status,Ports,Image
    Write-Host "Frontend: http://localhost:3000/"
    Write-Host "Backend:  http://localhost:8000/"
} else {
    Write-Host "\nTo run the containers locally, use:\n" -ForegroundColor Cyan
    Write-Host "docker run --rm -p 3000:3000 --name holi-timecards-app-local $frontendImage"
    Write-Host "docker run --rm -p 8000:8000 --name holi-timecards-backend-local $backendImage"
}

Write-Host "\n==== Done. ====" -ForegroundColor Green
