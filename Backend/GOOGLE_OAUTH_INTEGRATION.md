# Google OAuth Integration for EasyShifts

## Overview
This document describes the Google OAuth integration implemented in the EasyShifts backend. The integration allows users to sign in with their Google accounts, link existing accounts to Google, and create new accounts using Google authentication.

## Features Implemented

### 1. Database Schema Updates
- Added Google OAuth fields to the `User` model:
  - `google_id`: Unique Google OAuth identifier
  - `email`: User's email address
  - `google_picture`: URL to user's Google profile picture
  - `last_login`: Timestamp of user's last login
- Made `password` field nullable for Google OAuth users

### 2. Backend Components

#### Google Auth Handler (`handlers/google_auth.py`)
- **GoogleAuthHandler class**: Main handler for Google OAuth operations
- **Token verification**: Validates Google ID tokens using Google's verification library
- **User management**: Handles user creation, linking, and authentication

#### Database Controllers
- **UsersController**: Extended with Google OAuth methods
- **UsersRepository**: Added Google OAuth database operations

### 3. WebSocket Request Handlers
The following request IDs are now supported:

#### Request ID 66: Google Auth Login
**Purpose**: Authenticate user with Google OAuth token

**Request Data**:
```json
{
  "request_id": 66,
  "data": {
    "credential": "google_id_token_here",
    "clientId": "your_google_client_id"
  }
}
```

**Response (User Exists)**:
```json
{
  "request_id": 66,
  "success": true,
  "data": {
    "user_exists": true,
    "username": "user123",
    "is_manager": false,
    "email": "user@example.com",
    "google_linked": true
  }
}
```

**Response (New User)**:
```json
{
  "request_id": 66,
  "success": true,
  "data": {
    "user_exists": false,
    "google_user_info": {
      "google_id": "google_user_id",
      "email": "user@example.com",
      "name": "User Name",
      "picture": "https://photo.url",
      "email_verified": true
    }
  }
}
```

#### Request ID 67: Link Google Account
**Purpose**: Link Google account to existing EasyShifts account

**Request Data**:
```json
{
  "request_id": 67,
  "data": {
    "username": "existing_username",
    "password": "existing_password",
    "googleData": {
      "sub": "google_user_id",
      "email": "user@example.com",
      "name": "User Name",
      "picture": "https://photo.url"
    }
  }
}
```

**Response**:
```json
{
  "request_id": 67,
  "success": true,
  "data": {
    "username": "existing_username",
    "is_manager": false,
    "google_linked": true
  }
}
```

#### Request ID 68: Create Account with Google
**Purpose**: Create new EasyShifts account using Google authentication

**Request Data**:
```json
{
  "request_id": 68,
  "data": {
    "username": "new_username",
    "name": "User Name",
    "email": "user@example.com",
    "googleData": {
      "sub": "google_user_id",
      "picture": "https://photo.url"
    }
  }
}
```

**Response**:
```json
{
  "request_id": 68,
  "success": true,
  "data": {
    "username": "new_username",
    "is_manager": false,
    "google_linked": true
  }
}
```

#### Request ID 69: Google Signup Employee
**Purpose**: Create new employee account using Google authentication with role-specific data

**Request Data**:
```json
{
  "request_id": 69,
  "data": {
    "username": "new_employee",
    "name": "Employee Name",
    "email": "employee@example.com",
    "businessName": "Company Name",
    "googleData": {
      "sub": "google_user_id",
      "picture": "https://photo.url"
    },
    "certifications": {
      "canCrewChief": false,
      "canForklift": true,
      "canTruck": false
    }
  }
}
```

**Response**:
```json
{
  "request_id": 69,
  "success": true,
  "data": {
    "username": "new_employee",
    "is_manager": false,
    "google_linked": true
  }
}
```

#### Request ID 70: Google Signup Manager
**Purpose**: Create new manager account using Google authentication

**Request Data**:
```json
{
  "request_id": 70,
  "data": {
    "username": "new_manager",
    "name": "Manager Name",
    "email": "manager@example.com",
    "googleData": {
      "sub": "google_user_id",
      "picture": "https://photo.url"
    }
  }
}
```

**Response**:
```json
{
  "request_id": 70,
  "success": true,
  "data": {
    "username": "new_manager",
    "is_manager": true,
    "google_linked": true
  }
}
```

#### Request ID 71: Google Signup Client
**Purpose**: Create new client account using Google authentication

**Request Data**:
```json
{
  "request_id": 71,
  "data": {
    "username": "new_client",
    "name": "Client Name",
    "email": "client@example.com",
    "companyName": "Client Company",
    "googleData": {
      "sub": "google_user_id",
      "picture": "https://photo.url"
    }
  }
}
```

**Response**:
```json
{
  "request_id": 71,
  "success": true,
  "data": {
    "username": "new_client",
    "is_manager": false,
    "google_linked": true
  }
}
```

## Configuration

### Environment Variables
Create a `.env` file in the Backend directory with:
```
GOOGLE_CLIENT_ID=your_google_client_id_here
```

### Dependencies
The following packages are required (already added to requirements.txt):
- `google-auth`
- `google-auth-oauthlib`
- `google-auth-httplib2`
- `python-dotenv`

## Installation & Setup

1. **Install dependencies**:
   ```bash
   cd Backend
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   - Add your Google Client ID to `Backend/.env`
   - Ensure the same Client ID is in `app/.env` for frontend

3. **Database migration**:
   - The new fields will be automatically created when you start the server
   - Existing users can link their Google accounts using Request ID 67

4. **Start the server**:
   ```bash
   python Server.py
   ```

## Testing

Run the test script to verify the integration:
```bash
cd Backend
python test_google_auth.py
```

## Security Notes

1. **Token Verification**: All Google ID tokens are verified using Google's official verification library
2. **Unique Constraints**: Google IDs are unique across the system
3. **Email Verification**: Google provides email verification status
4. **Session Management**: User sessions are created upon successful authentication

## Error Handling

The system handles the following error cases:
- Invalid Google tokens
- Duplicate Google account linking
- Username conflicts
- Database errors
- Network issues during token verification

## Frontend Integration

The frontend should:
1. Use Google Sign-In JavaScript library
2. Send the received credential to the backend using the appropriate request ID
3. Handle the different response scenarios (existing user, new user, account linking)

## Next Steps

1. Test with actual Google OAuth tokens from the frontend
2. Implement additional Google OAuth scopes if needed
3. Add Google account unlinking functionality
4. Consider implementing Google OAuth refresh tokens for long-term sessions
