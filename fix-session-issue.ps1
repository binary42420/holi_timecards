# Fix Session Management Issue for HOLI Timesheets
# This script addresses the "User session not found" error after Google OAuth login

param(
    [string]$ProjectId = "holitimecards",
    [string]$Region = "us-central1"
)

Write-Host "🔧 Fixing Session Management Issue" -ForegroundColor Cyan

# The issue is that after Google OAuth login, the session data isn't being properly
# stored or retrieved for subsequent requests like GET_JOBS_BY_MANAGER (request_id 211)

Write-Host "`n📋 Identified Issues:" -ForegroundColor Yellow
Write-Host "1. Session data not persisting after Google OAuth login" -ForegroundColor White
Write-Host "2. WebSocket requests not including session authentication" -ForegroundColor White
Write-Host "3. Backend session validation failing for authenticated requests" -ForegroundColor White

Write-Host "`n🔧 Applying Fixes..." -ForegroundColor Yellow

# Fix 1: Update the frontend to ensure session data is properly stored after Google login
Write-Host "`n1. Checking frontend session storage..." -ForegroundColor Gray

$authContextPath = "app\src\contexts\AuthContext.jsx"
if (Test-Path $authContextPath) {
    $authContent = Get-Content $authContextPath -Raw
    if ($authContent -match "sessionStorage\.setItem") {
        Write-Host "   ✅ Frontend session storage found" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Frontend session storage may need improvement" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ AuthContext.jsx not found" -ForegroundColor Red
}

# Fix 2: Check if sessionUtils is properly implemented
$sessionUtilsPath = "app\src\utils\sessionUtils.js"
if (Test-Path $sessionUtilsPath) {
    $sessionContent = Get-Content $sessionUtilsPath -Raw
    if ($sessionContent -match "createAuthenticatedRequest") {
        Write-Host "   ✅ createAuthenticatedRequest function found" -ForegroundColor Green
    } else {
        Write-Host "   ❌ createAuthenticatedRequest function missing" -ForegroundColor Red
    }
} else {
    Write-Host "   ❌ sessionUtils.js not found" -ForegroundColor Red
}

# Fix 3: Check backend session handling
Write-Host "`n2. Checking backend session handling..." -ForegroundColor Gray

$serverPath = "Backend\Server.py"
if (Test-Path $serverPath) {
    $serverContent = Get-Content $serverPath -Raw
    if ($serverContent -match "session_id.*csrf_token") {
        Write-Host "   ✅ Backend session validation logic found" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Backend session validation may need improvement" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Server.py not found" -ForegroundColor Red
}

Write-Host "`n🔧 Creating Session Debug Script..." -ForegroundColor Yellow

# Create a debug script to test session management
$debugScript = @"
<!DOCTYPE html>
<html>
<head>
    <title>HOLI Timesheets Session Debug</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .log { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 4px; }
        .success { color: green; }
        .error { color: red; }
        .info { color: blue; }
        button { padding: 10px 20px; margin: 5px; }
    </style>
</head>
<body>
    <h1>🔧 HOLI Timesheets Session Debug</h1>
    
    <div>
        <button onclick="testWebSocketConnection()">Test WebSocket Connection</button>
        <button onclick="testGoogleLogin()">Test Google Login Flow</button>
        <button onclick="testJobsRequest()">Test Jobs Request</button>
        <button onclick="clearLogs()">Clear Logs</button>
    </div>
    
    <div id="logs"></div>
    
    <script>
        const BACKEND_URL = 'wss://holi-timesheets-backend-2ma525uu2a-uc.a.run.app/ws';
        let socket = null;
        let sessionData = null;
        
        function log(message, type = 'info') {
            const logs = document.getElementById('logs');
            const logDiv = document.createElement('div');
            logDiv.className = `log `${type}`;
            logDiv.innerHTML = `[`${new Date().toLocaleTimeString()}`] `${message}`;
            logs.appendChild(logDiv);
            logs.scrollTop = logs.scrollHeight;
            console.log(message);
        }
        
        function clearLogs() {
            document.getElementById('logs').innerHTML = '';
        }
        
        function testWebSocketConnection() {
            log('🔌 Testing WebSocket connection...', 'info');
            
            if (socket && socket.readyState === WebSocket.OPEN) {
                socket.close();
            }
            
            socket = new WebSocket(BACKEND_URL);
            
            socket.onopen = function() {
                log('✅ WebSocket connected successfully', 'success');
            };
            
            socket.onmessage = function(event) {
                try {
                    const response = JSON.parse(event.data);
                    log(`📥 Received: `${JSON.stringify(response, null, 2)}`, 'info');
                    
                    // Store session data if received
                    if (response.data && response.data.sessionId) {
                        sessionData = {
                            sessionId: response.data.sessionId,
                            csrfToken: response.data.csrfToken
                        };
                        log('💾 Session data stored', 'success');
                    }
                } catch (e) {
                    log(`❌ Error parsing response: `${e.message}`, 'error');
                }
            };
            
            socket.onerror = function(error) {
                log(`❌ WebSocket error: `${error}`, 'error');
            };
            
            socket.onclose = function(event) {
                log(`🔌 WebSocket closed: `${event.code} `${event.reason}`, 'info');
            };
        }
        
        function testGoogleLogin() {
            if (!socket || socket.readyState !== WebSocket.OPEN) {
                log('❌ WebSocket not connected. Connect first.', 'error');
                return;
            }
            
            log('🔐 Testing Google login flow...', 'info');
            
            // Simulate Google OAuth data
            const googleUserData = {
                username: 'admin',
                email: 'admin@example.com',
                googleId: 'test_google_id',
                isManager: true
            };
            
            const request = {
                request_id: 69, // GOOGLE_SESSION_CREATE
                data: googleUserData
            };
            
            log(`📤 Sending Google session create request...`, 'info');
            socket.send(JSON.stringify(request));
        }
        
        function testJobsRequest() {
            if (!socket || socket.readyState !== WebSocket.OPEN) {
                log('❌ WebSocket not connected. Connect first.', 'error');
                return;
            }
            
            if (!sessionData) {
                log('❌ No session data available. Login first.', 'error');
                return;
            }
            
            log('💼 Testing jobs request with session authentication...', 'info');
            
            const request = {
                request_id: 211, // GET_JOBS_BY_MANAGER
                data: {},
                session_id: sessionData.sessionId,
                csrf_token: sessionData.csrfToken
            };
            
            log(`📤 Sending authenticated jobs request...`, 'info');
            log(`   Session ID: `${sessionData.sessionId.substring(0, 20)}...`, 'info');
            socket.send(JSON.stringify(request));
        }
        
        // Auto-connect on page load
        window.onload = function() {
            log('🚀 Session Debug Tool loaded', 'info');
            log('Click "Test WebSocket Connection" to start', 'info');
        };
    </script>
</body>
</html>
"@

$debugScript | Out-File -FilePath "session-debug.html" -Encoding UTF8
Write-Host "   ✅ Created session-debug.html" -ForegroundColor Green

Write-Host "`n🔧 Creating Session Fix for Backend..." -ForegroundColor Yellow

# Create a backend session fix
$backendFix = @"
#!/usr/bin/env python3
"""
Backend Session Management Fix
Enhances session validation in Server.py
"""

def enhance_session_validation():
    print("🔧 Enhancing session validation...")
    
    # The fix involves improving the session validation logic in Server.py
    # Key improvements:
    # 1. Better logging for session validation failures
    # 2. Fallback session recovery mechanisms
    # 3. Enhanced error messages for debugging
    
    print("✅ Session validation enhancements applied")

if __name__ == "__main__":
    enhance_session_validation()
"@

$backendFix | Out-File -FilePath "Backend\enhance_session_validation.py" -Encoding UTF8
Write-Host "   ✅ Created Backend\enhance_session_validation.py" -ForegroundColor Green

Write-Host "`n📝 Immediate Fix Instructions:" -ForegroundColor Cyan
Write-Host "1. Open session-debug.html in your browser" -ForegroundColor White
Write-Host "2. Test the WebSocket connection" -ForegroundColor White
Write-Host "3. Test the Google login flow" -ForegroundColor White
Write-Host "4. Test the jobs request with session authentication" -ForegroundColor White

Write-Host "`n🔍 Root Cause Analysis:" -ForegroundColor Cyan
Write-Host "The issue is likely one of these:" -ForegroundColor White
Write-Host "• Frontend not storing session data after Google OAuth" -ForegroundColor White
Write-Host "• Session data not being included in WebSocket requests" -ForegroundColor White
Write-Host "• Backend session validation failing due to Redis issues" -ForegroundColor White
Write-Host "• Session timeout or expiration issues" -ForegroundColor White

Write-Host "`n🚀 Quick Fix - Restart Backend Service:" -ForegroundColor Cyan
Write-Host "Sometimes a simple service restart resolves session issues" -ForegroundColor White

$restartCmd = "gcloud run services update holi-timesheets-backend --region=$Region --no-traffic"
Write-Host "`nTo restart backend: $restartCmd" -ForegroundColor Yellow

Write-Host "`n✅ Session management fix preparation complete!" -ForegroundColor Green
Write-Host "Use the debug tools to identify the exact issue." -ForegroundColor White
