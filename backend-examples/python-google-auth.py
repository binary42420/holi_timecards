# Python Backend Implementation for Google OAuth
# Install: pip install google-auth google-auth-oauthlib google-auth-httplib2

import json
import os
from google.auth.transport import requests
from google.oauth2 import id_token
import logging

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')

class GoogleAuthHandler:
    def __init__(self):
        self.google_client_id = GOOGLE_CLIENT_ID
        
    def verify_google_token(self, token):
        """Verify Google ID token and extract user information"""
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.google_client_id
            )
            
            # Token is valid, extract user info
            return {
                'success': True,
                'user': {
                    'google_id': idinfo['sub'],
                    'email': idinfo['email'],
                    'name': idinfo['name'],
                    'picture': idinfo.get('picture'),
                    'email_verified': idinfo.get('email_verified', False)
                }
            }
            
        except ValueError as e:
            logging.error(f"Google token verification failed: {e}")
            return {
                'success': False,
                'error': 'Invalid Google token'
            }
    
    async def handle_google_auth_login(self, websocket, request_data):
        """Handle Google authentication login (Request ID 66)"""
        try:
            credential = request_data.get('credential')
            client_id = request_data.get('clientId')
            
            if not credential:
                await self.send_response(websocket, 66, False, None, 'Missing credential')
                return
            
            # Verify Google token
            verification = self.verify_google_token(credential)
            if not verification['success']:
                await self.send_response(websocket, 66, False, None, verification['error'])
                return
            
            google_user = verification['user']
            
            # Check if user exists in database
            existing_user = await self.find_user_by_google_id_or_email(
                google_user['google_id'], 
                google_user['email']
            )
            
            if existing_user:
                # User exists, log them in
                response_data = {
                    'user_exists': True,
                    'username': existing_user['username'],
                    'is_manager': existing_user['is_manager'],
                    'email': existing_user['email'],
                    'google_linked': True
                }
                
                # Update last login
                await self.update_user_last_login(existing_user['id'])
                
                await self.send_response(websocket, 66, True, response_data)
            else:
                # User doesn't exist, need account linking or creation
                response_data = {
                    'user_exists': False,
                    'google_user_info': google_user
                }
                
                await self.send_response(websocket, 66, True, response_data)
                
        except Exception as e:
            logging.error(f"Google auth login error: {e}")
            await self.send_response(websocket, 66, False, None, 'Authentication failed')
    
    async def handle_link_google_account(self, websocket, request_data):
        """Handle linking Google account to existing account (Request ID 67)"""
        try:
            username = request_data.get('username')
            password = request_data.get('password')
            google_data = request_data.get('googleData')
            
            # Verify existing user credentials
            user = await self.authenticate_user(username, password)
            if not user:
                await self.send_response(websocket, 67, False, None, 'Invalid username or password')
                return
            
            # Check if Google account is already linked to another user
            existing_google_user = await self.find_user_by_google_id(google_data['sub'])
            if existing_google_user and existing_google_user['id'] != user['id']:
                await self.send_response(websocket, 67, False, None, 'Google account already linked to another user')
                return
            
            # Link Google account to existing user
            await self.link_google_account_to_user(user['id'], google_data)
            
            response_data = {
                'username': user['username'],
                'is_manager': user['is_manager'],
                'google_linked': True
            }
            
            await self.send_response(websocket, 67, True, response_data)
            
        except Exception as e:
            logging.error(f"Link Google account error: {e}")
            await self.send_response(websocket, 67, False, None, 'Failed to link Google account')
    
    async def handle_create_account_with_google(self, websocket, request_data):
        """Handle creating new account with Google (Request ID 68)"""
        try:
            username = request_data.get('username')
            google_data = request_data.get('googleData')
            name = request_data.get('name')
            email = request_data.get('email')
            
            # Check if username already exists
            existing_user = await self.find_user_by_username(username)
            if existing_user:
                await self.send_response(websocket, 68, False, None, 'Username already exists')
                return
            
            # Check if Google account is already linked
            existing_google_user = await self.find_user_by_google_id(google_data['sub'])
            if existing_google_user:
                await self.send_response(websocket, 68, False, None, 'Google account already linked to another user')
                return
            
            # Create new user account
            new_user = await self.create_user_with_google({
                'username': username,
                'name': name,
                'email': email,
                'google_id': google_data['sub'],
                'google_data': google_data,
                'is_manager': False,  # New accounts are employees by default
                'approved': False  # Require approval unless auto-approved
            })
            
            response_data = {
                'username': new_user['username'],
                'is_manager': new_user['is_manager'],
                'google_linked': True
            }
            
            await self.send_response(websocket, 68, True, response_data)
            
        except Exception as e:
            logging.error(f"Create account with Google error: {e}")
            await self.send_response(websocket, 68, False, None, 'Failed to create account')
    
    async def send_response(self, websocket, request_id, success, data=None, error=None):
        """Send response back to client"""
        response = {
            'request_id': request_id,
            'success': success,
            'data': data,
            'error': error
        }
        
        await websocket.send(json.dumps(response))
    
    # Database helper methods (implement based on your database)
    async def find_user_by_google_id_or_email(self, google_id, email):
        """Find user by Google ID or email"""
        # Implementation depends on your database
        pass
    
    async def find_user_by_google_id(self, google_id):
        """Find user by Google ID"""
        # Implementation depends on your database
        pass
    
    async def find_user_by_username(self, username):
        """Find user by username"""
        # Implementation depends on your database
        pass
    
    async def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        # Implementation depends on your existing auth system
        pass
    
    async def link_google_account_to_user(self, user_id, google_data):
        """Link Google account to existing user"""
        # Implementation depends on your database
        pass
    
    async def create_user_with_google(self, user_data):
        """Create new user with Google information"""
        # Implementation depends on your database
        pass
    
    async def update_user_last_login(self, user_id):
        """Update user's last login time"""
        # Implementation depends on your database
        pass

# WebSocket message handler integration
async def handle_websocket_message(websocket, message):
    """Main WebSocket message handler"""
    try:
        request = json.loads(message)
        request_id = request.get('request_id')
        
        google_auth = GoogleAuthHandler()
        
        if request_id == 66:  # GOOGLE_AUTH_LOGIN
            await google_auth.handle_google_auth_login(websocket, request.get('data', {}))
        elif request_id == 67:  # LINK_GOOGLE_ACCOUNT
            await google_auth.handle_link_google_account(websocket, request.get('data', {}))
        elif request_id == 68:  # CREATE_ACCOUNT_WITH_GOOGLE
            await google_auth.handle_create_account_with_google(websocket, request.get('data', {}))
        else:
            # Handle other existing request IDs
            await handle_other_requests(websocket, request)
            
    except json.JSONDecodeError:
        logging.error("Invalid JSON received")
    except Exception as e:
        logging.error(f"WebSocket message handling error: {e}")

async def handle_other_requests(websocket, request):
    """Handle other existing request types"""
    # Your existing request handlers
    pass
