#!/usr/bin/env node

/**
 * Simple WebSocket Test Server for Local Development
 * This server simulates the backend WebSocket API for testing purposes
 *
 * To install dependencies: npm install ws
 * To run: node test-websocket-server.js
 */

const WebSocket = require('ws');
const http = require('http');

const PORT = 8765;

// Create HTTP server for health checks
const server = http.createServer((req, res) => {
  if (req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok', timestamp: new Date().toISOString() }));
  } else {
    res.writeHead(404);
    res.end('Not Found');
  }
});

// Create WebSocket server
const wss = new WebSocket.Server({ server });

console.log(`🚀 Starting WebSocket Test Server on port ${PORT}`);
console.log(`📡 WebSocket URL: ws://localhost:${PORT}`);
console.log(`🏥 Health check: http://localhost:${PORT}/health`);

wss.on('connection', (ws, req) => {
  const clientId = Math.random().toString(36).substring(7);
  console.log(`✅ Client connected: ${clientId} from ${req.socket.remoteAddress}`);

  // Send welcome message
  ws.send(JSON.stringify({
    type: 'welcome',
    message: 'Connected to WebSocket Test Server',
    clientId: clientId,
    timestamp: new Date().toISOString()
  }));

  ws.on('message', (data) => {
    try {
      const message = JSON.parse(data.toString());
      console.log(`📨 Received from ${clientId}:`, message);

      // Handle different request types
      handleRequest(ws, message, clientId);
    } catch (error) {
      console.error(`❌ Error parsing message from ${clientId}:`, error);
      ws.send(JSON.stringify({
        error: 'Invalid JSON format',
        timestamp: new Date().toISOString()
      }));
    }
  });

  ws.on('close', (code, reason) => {
    console.log(`🔌 Client disconnected: ${clientId} (${code}: ${reason})`);
  });

  ws.on('error', (error) => {
    console.error(`❌ WebSocket error for ${clientId}:`, error);
  });
});

function handleRequest(ws, message, clientId) {
  const { request_id, data } = message;

  console.log(`🔄 Processing request ${request_id} from ${clientId}`);

  switch (request_id) {
    case 66: // GOOGLE_AUTH_LOGIN
      handleGoogleAuth(ws, data, request_id);
      break;
    
    case 10: // LOGIN_REQUEST
      handleLogin(ws, data, request_id);
      break;
    
    case 1: // Test login request
      handleTestLogin(ws, data, request_id);
      break;
    
    default:
      // Echo back unknown requests
      ws.send(JSON.stringify({
        request_id: request_id,
        success: false,
        error: `Unknown request_id: ${request_id}`,
        timestamp: new Date().toISOString()
      }));
  }
}

function handleGoogleAuth(ws, data, request_id) {
  console.log(`🔐 Google Auth request:`, data);
  
  // Simulate Google authentication
  setTimeout(() => {
    ws.send(JSON.stringify({
      request_id: request_id,
      success: true,
      data: {
        user_exists: true,
        username: 'test_user',
        is_manager: true,
        email: 'test@example.com',
        session_id: 'test_session_' + Date.now(),
        csrf_token: 'test_csrf_' + Date.now()
      }
    }));
  }, 1000); // Simulate network delay
}

function handleLogin(ws, data, request_id) {
  console.log(`👤 Login request:`, data);
  
  // Simulate login
  setTimeout(() => {
    if (data.username && data.password) {
      ws.send(JSON.stringify({
        request_id: request_id,
        success: true,
        data: {
          username: data.username,
          is_manager: data.username === 'manager',
          session_id: 'session_' + Date.now(),
          csrf_token: 'csrf_' + Date.now()
        }
      }));
    } else {
      ws.send(JSON.stringify({
        request_id: request_id,
        success: false,
        error: 'Username and password required'
      }));
    }
  }, 500);
}

function handleTestLogin(ws, data, request_id) {
  console.log(`🧪 Test login request:`, data);
  
  // Simulate test login response
  setTimeout(() => {
    ws.send(JSON.stringify({
      request_id: request_id,
      success: true,
      message: 'Test login successful',
      data: {
        username: data.username || 'test_user',
        timestamp: new Date().toISOString()
      }
    }));
  }, 300);
}

// Handle server shutdown gracefully
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down WebSocket Test Server...');
  wss.close(() => {
    server.close(() => {
      console.log('✅ Server closed');
      process.exit(0);
    });
  });
});

// Start the server
server.listen(PORT, () => {
  console.log(`✅ WebSocket Test Server running on port ${PORT}`);
  console.log('📝 Logs will appear here as clients connect and send messages');
  console.log('🔄 Press Ctrl+C to stop the server');
});
