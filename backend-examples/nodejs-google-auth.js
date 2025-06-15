// Node.js Backend Implementation for Google OAuth
// Install: npm install google-auth-library

const { OAuth2Client } = require('google-auth-library');

// Initialize Google OAuth client
const GOOGLE_CLIENT_ID = process.env.GOOGLE_CLIENT_ID;
const client = new OAuth2Client(GOOGLE_CLIENT_ID);

// Google token verification function
async function verifyGoogleToken(token) {
  try {
    const ticket = await client.verifyIdToken({
      idToken: token,
      audience: GOOGLE_CLIENT_ID,
    });
    
    const payload = ticket.getPayload();
    return {
      success: true,
      user: {
        googleId: payload.sub,
        email: payload.email,
        name: payload.name,
        picture: payload.picture,
        emailVerified: payload.email_verified
      }
    };
  } catch (error) {
    console.error('Google token verification failed:', error);
    return { 
      success: false, 
      error: 'Invalid Google token' 
    };
  }
}

// WebSocket message handler additions
async function handleWebSocketMessage(ws, message) {
  const request = JSON.parse(message);
  
  switch (request.request_id) {
    case 66: // GOOGLE_AUTH_LOGIN
      await handleGoogleAuthLogin(ws, request);
      break;
      
    case 67: // LINK_GOOGLE_ACCOUNT
      await handleLinkGoogleAccount(ws, request);
      break;
      
    case 68: // CREATE_ACCOUNT_WITH_GOOGLE
      await handleCreateAccountWithGoogle(ws, request);
      break;
      
    // ... other existing cases
  }
}

// Handler for Google authentication login
async function handleGoogleAuthLogin(ws, request) {
  try {
    const { credential, clientId } = request.data;
    
    // Verify Google token
    const verification = await verifyGoogleToken(credential);
    if (!verification.success) {
      return sendResponse(ws, 66, false, null, verification.error);
    }
    
    const googleUser = verification.user;
    
    // Check if user exists in database by Google ID or email
    const existingUser = await findUserByGoogleIdOrEmail(googleUser.googleId, googleUser.email);
    
    if (existingUser) {
      // User exists, log them in
      const response = {
        user_exists: true,
        username: existingUser.username,
        is_manager: existingUser.isManager,
        email: existingUser.email,
        google_linked: true
      };
      
      // Update last login time
      await updateUserLastLogin(existingUser.id);
      
      sendResponse(ws, 66, true, response);
    } else {
      // User doesn't exist, need account linking or creation
      const response = {
        user_exists: false,
        google_user_info: googleUser
      };
      
      sendResponse(ws, 66, true, response);
    }
    
  } catch (error) {
    console.error('Google auth login error:', error);
    sendResponse(ws, 66, false, null, 'Authentication failed');
  }
}

// Handler for linking Google account to existing account
async function handleLinkGoogleAccount(ws, request) {
  try {
    const { username, password, googleData } = request.data;
    
    // Verify existing user credentials
    const user = await authenticateUser(username, password);
    if (!user) {
      return sendResponse(ws, 67, false, null, 'Invalid username or password');
    }
    
    // Check if Google account is already linked to another user
    const existingGoogleUser = await findUserByGoogleId(googleData.sub);
    if (existingGoogleUser && existingGoogleUser.id !== user.id) {
      return sendResponse(ws, 67, false, null, 'Google account already linked to another user');
    }
    
    // Link Google account to existing user
    await linkGoogleAccountToUser(user.id, googleData);
    
    const response = {
      username: user.username,
      is_manager: user.isManager,
      google_linked: true
    };
    
    sendResponse(ws, 67, true, response);
    
  } catch (error) {
    console.error('Link Google account error:', error);
    sendResponse(ws, 67, false, null, 'Failed to link Google account');
  }
}

// Handler for creating new account with Google
async function handleCreateAccountWithGoogle(ws, request) {
  try {
    const { username, googleData, name, email } = request.data;
    
    // Check if username already exists
    const existingUser = await findUserByUsername(username);
    if (existingUser) {
      return sendResponse(ws, 68, false, null, 'Username already exists');
    }
    
    // Check if Google account is already linked
    const existingGoogleUser = await findUserByGoogleId(googleData.sub);
    if (existingGoogleUser) {
      return sendResponse(ws, 68, false, null, 'Google account already linked to another user');
    }
    
    // Create new user account
    const newUser = await createUserWithGoogle({
      username: username,
      name: name,
      email: email,
      googleId: googleData.sub,
      googleData: googleData,
      isManager: false, // New accounts are employees by default
      approved: false // Require approval unless auto-approved
    });
    
    const response = {
      username: newUser.username,
      is_manager: newUser.isManager,
      google_linked: true
    };
    
    sendResponse(ws, 68, true, response);
    
  } catch (error) {
    console.error('Create account with Google error:', error);
    sendResponse(ws, 68, false, null, 'Failed to create account');
  }
}

// Database helper functions (implement based on your database)
async function findUserByGoogleIdOrEmail(googleId, email) {
  // Implementation depends on your database
  // Return user object if found, null otherwise
}

async function findUserByGoogleId(googleId) {
  // Implementation depends on your database
}

async function findUserByUsername(username) {
  // Implementation depends on your database
}

async function authenticateUser(username, password) {
  // Implementation depends on your existing auth system
}

async function linkGoogleAccountToUser(userId, googleData) {
  // Implementation depends on your database
  // Update user record with Google ID and data
}

async function createUserWithGoogle(userData) {
  // Implementation depends on your database
  // Create new user with Google information
}

async function updateUserLastLogin(userId) {
  // Implementation depends on your database
}

// Response helper function
function sendResponse(ws, requestId, success, data = null, error = null) {
  const response = {
    request_id: requestId,
    success: success,
    data: data,
    error: error
  };
  
  ws.send(JSON.stringify(response));
}
