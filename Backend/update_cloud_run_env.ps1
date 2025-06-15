# Update Cloud Run environment variables to fix Redis connection
Write-Host "🚀 Updating Holi Cloud Run Environment Variables" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1",
    [string]$ServiceName = "holi-timesheets-backend"
)

Write-Host "📋 Service: $ServiceName" -ForegroundColor Cyan
Write-Host "📍 Region: $Region" -ForegroundColor Cyan
Write-Host "🏗️ Project: $ProjectId" -ForegroundColor Cyan

# Load environment variables from .env.production
if (Test-Path ".env.production") {
    Write-Host "✅ Loading environment variables from .env.production" -ForegroundColor Green
    
    # Read the .env file and create environment variables
    Get-Content ".env.production" | ForEach-Object {
        if ($_ -match "^([^#][^=]+)=(.*)$") {
            $name = $matches[1]
            $value = $matches[2]
            Set-Variable -Name $name -Value $value
        }
    }
} else {
    Write-Host "❌ .env.production file not found" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔧 Updating Cloud Run service with environment variables..." -ForegroundColor Yellow

# Create the environment variables string
$envVars = @(
    "DB_HOST=$DB_HOST",
    "DB_PORT=$DB_PORT", 
    "DB_USER=$DB_USER",
    "DB_NAME=$DB_NAME",
    "DB_PASSWORD=$DB_PASSWORD",
    "REDIS_HOST=$REDIS_HOST",
    "REDIS_PORT=$REDIS_PORT",
    "REDIS_PASSWORD=$REDIS_PASSWORD",
    "REDIS_DB=$REDIS_DB",
    "REDIS_MAX_CONNECTIONS=$REDIS_MAX_CONNECTIONS",
    "REDIS_SOCKET_TIMEOUT=$REDIS_SOCKET_TIMEOUT",
    "REDIS_CONNECT_TIMEOUT=$REDIS_CONNECT_TIMEOUT",
    "SESSION_SECRET_KEY=$SESSION_SECRET_KEY",
    "CSRF_SECRET_KEY=$CSRF_SECRET_KEY",
    "SESSION_TIMEOUT_MINUTES=$SESSION_TIMEOUT_MINUTES",
    "VALIDATE_SESSION_IP=$VALIDATE_SESSION_IP",
    "PASSWORD_MIN_LENGTH=$PASSWORD_MIN_LENGTH",
    "REQUIRE_PASSWORD_COMPLEXITY=$REQUIRE_PASSWORD_COMPLEXITY",
    "HOST=$HOST",
    "PORT=8080",
    "ENVIRONMENT=$ENVIRONMENT",
    "GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID"
) -join ","

# Update the Cloud Run service
$gcloudArgs = @(
    "run", "services", "update", $ServiceName,
    "--region=$Region",
    "--project=$ProjectId", 
    "--set-env-vars=$envVars",
    "--quiet"
)

Write-Host "Executing: gcloud $($gcloudArgs -join ' ')" -ForegroundColor Gray

try {
    & gcloud $gcloudArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Cloud Run service updated successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "⏳ Waiting for deployment to propagate..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        Write-Host "🧪 Testing health endpoint..." -ForegroundColor Yellow
        $healthUrl = "https://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/health"
        
        try {
            $response = Invoke-WebRequest -Uri $healthUrl -TimeoutSec 20
            
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ Health check passed!" -ForegroundColor Green
                Write-Host ""
                Write-Host "🎉 DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
                Write-Host "The Redis connection issue should now be resolved." -ForegroundColor Green
                Write-Host ""
                Write-Host "🔌 WebSocket URL: wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "Next steps:" -ForegroundColor Yellow
                Write-Host "1. Test the frontend login" -ForegroundColor White
                Write-Host "2. Verify WebSocket connection" -ForegroundColor White
                Write-Host "3. Check session creation" -ForegroundColor White
            } else {
                Write-Host "❌ Health check failed (HTTP $($response.StatusCode))" -ForegroundColor Red
                Write-Host "Check the Cloud Run logs for more details." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "❌ Health check error: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Cloud Run service update failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error executing gcloud command: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

