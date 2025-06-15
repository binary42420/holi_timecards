
// Frontend Google Session Debug Fix
// Add this to your browser console to debug Google session creation

function debugGoogleSessionCreation() {
    console.log("🔧 Google Session Debug Fix");
    
    // Check if WebSocket is connected
    if (!window.socket || window.socket.readyState !== WebSocket.OPEN) {
        console.error("❌ WebSocket not connected");
        return;
    }
    
    // Test Google session creation with proper data
    const testGoogleData = {
        username: "admin",
        email: "admin@example.com", 
        googleId: "test_google_id_123",
        isManager: true
    };
    
    console.log("📤 Sending Google session create request with data:", testGoogleData);
    
    const request = {
        request_id: 69, // GOOGLE_SESSION_CREATE
        data: testGoogleData
    };
    
    window.socket.send(JSON.stringify(request));
    
    // Listen for response
    const originalOnMessage = window.socket.onmessage;
    window.socket.onmessage = function(event) {
        const response = JSON.parse(event.data);
        if (response.request_id === 69) {
            console.log("📥 Google session response:", response);
            if (response.data && response.data.success) {
                console.log("✅ Google session created successfully!");
                console.log("Session ID:", response.data.sessionId);
                console.log("CSRF Token:", response.data.csrfToken);
            } else {
                console.error("❌ Google session creation failed:", response.data);
            }
        }
        if (originalOnMessage) originalOnMessage(event);
    };
}

// Run the debug function
debugGoogleSessionCreation();
