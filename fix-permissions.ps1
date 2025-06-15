#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Fix file permissions for HOLI Timesheets on Windows 11
.DESCRIPTION
    This script fixes common permission issues that can occur when working with
    Docker containers and file systems on Windows 11.
#>

param(
    [switch]$Verbose = $false
)

# Set error handling
$ErrorActionPreference = "Continue"

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

Write-Header "🔧 HOLI Timesheets Permission Fix"

# Function to fix permissions on a directory
function Fix-DirectoryPermissions {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        Write-Info "🔄 Fixing permissions for $Description..."
        try {
            # Get current user
            $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
            
            # Set full control for current user
            icacls $Path /grant "${currentUser}:(OI)(CI)F" /T /Q 2>$null
            
            # Set read/execute for everyone
            icacls $Path /grant "Everyone:(OI)(CI)RX" /T /Q 2>$null
            
            Write-Success "✅ Fixed permissions for $Description"
        } catch {
            Write-Warning "⚠️ Could not fix permissions for $Description : $_"
        }
    } else {
        Write-Warning "⚠️ Path not found: $Path"
    }
}

# Function to fix file permissions
function Fix-FilePermissions {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        Write-Info "🔄 Fixing permissions for $Description..."
        try {
            # Get current user
            $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
            
            # Set full control for current user
            icacls $Path /grant "${currentUser}:F" /Q 2>$null
            
            # Set read for everyone
            icacls $Path /grant "Everyone:R" /Q 2>$null
            
            Write-Success "✅ Fixed permissions for $Description"
        } catch {
            Write-Warning "⚠️ Could not fix permissions for $Description : $_"
        }
    } else {
        Write-Warning "⚠️ File not found: $Path"
    }
}

# Fix Backend directory permissions
Write-Header "🏗️ Backend Permissions"
Fix-DirectoryPermissions "Backend" "Backend directory"
Fix-FilePermissions "Backend\Dockerfile" "Backend Dockerfile"
Fix-FilePermissions "Backend\requirements.txt" "Backend requirements"
Fix-FilePermissions "Backend\.env" "Backend environment file"

# Fix Frontend directory permissions
Write-Header "🎨 Frontend Permissions"
Fix-DirectoryPermissions "app" "Frontend directory"
Fix-FilePermissions "app\Dockerfile" "Frontend Dockerfile"
Fix-FilePermissions "app\package.json" "Frontend package.json"
Fix-FilePermissions "app\nginx.conf" "Frontend nginx config"

# Fix deployment scripts
Write-Header "🚀 Deployment Scripts"
Fix-FilePermissions "deploy-holi-comprehensive.ps1" "Comprehensive deployment script"
Fix-FilePermissions "test-docker-builds.ps1" "Docker build test script"
Fix-FilePermissions "docker-compose.yml" "Docker Compose file"

# Fix node_modules if it exists
if (Test-Path "app\node_modules") {
    Write-Info "🔄 Fixing node_modules permissions..."
    try {
        # Remove read-only attributes from node_modules
        attrib -R "app\node_modules\*.*" /S /D 2>$null
        Write-Success "✅ Fixed node_modules permissions"
    } catch {
        Write-Warning "⚠️ Could not fix node_modules permissions: $_"
    }
}

# Fix any build directories
if (Test-Path "app\build") {
    Fix-DirectoryPermissions "app\build" "Frontend build directory"
}

# Check Docker Desktop permissions
Write-Header "🐳 Docker Desktop Check"
Write-Info "🔍 Checking Docker Desktop access..."

try {
    $dockerVersion = docker version 2>$null
    if ($dockerVersion) {
        Write-Success "✅ Docker Desktop is accessible"
    } else {
        Write-Warning "⚠️ Docker Desktop may not be running or accessible"
        Write-Info "   Please ensure Docker Desktop is running and you have permissions"
    }
} catch {
    Write-Warning "⚠️ Docker Desktop check failed: $_"
}

# Check PowerShell execution policy
Write-Header "🔐 PowerShell Execution Policy"
$executionPolicy = Get-ExecutionPolicy
Write-Info "Current execution policy: $executionPolicy"

if ($executionPolicy -eq "Restricted") {
    Write-Warning "⚠️ PowerShell execution policy is Restricted"
    Write-Info "   You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser"
} else {
    Write-Success "✅ PowerShell execution policy allows script execution"
}

# Create .dockerignore files if they don't exist
Write-Header "📝 Docker Ignore Files"

$backendDockerIgnore = @"
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.vscode
.idea
*.swp
*.swo
*~
.DS_Store
Thumbs.db
"@

$frontendDockerIgnore = @"
node_modules
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.eslintcache
.vscode
.idea
*.swp
*.swo
*~
.DS_Store
Thumbs.db
build
.git
"@

if (-not (Test-Path "Backend\.dockerignore")) {
    $backendDockerIgnore | Out-File -FilePath "Backend\.dockerignore" -Encoding UTF8
    Write-Success "✅ Created Backend .dockerignore"
}

if (-not (Test-Path "app\.dockerignore")) {
    $frontendDockerIgnore | Out-File -FilePath "app\.dockerignore" -Encoding UTF8
    Write-Success "✅ Created Frontend .dockerignore"
}

Write-Header "🎉 Permission Fix Complete"
Write-Success "✅ All permission fixes applied!"
Write-Info "🚀 You can now run: .\test-docker-builds.ps1 to test builds"
Write-Info "🚀 Then run: .\deploy-holi-comprehensive.ps1 to deploy"
