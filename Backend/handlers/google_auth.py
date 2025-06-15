# Google OAuth Authentication Handler for EasyShifts
import json
import os
import logging
from google.auth.transport import requests
from google.oauth2 import id_token
from dotenv import load_dotenv

from db.controllers.users_controller import UsersController
from user_session import UserSession
from main import get_db_session

# Load environment variables
load_dotenv()

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
logging.info(f"Google OAuth: Loaded GOOGLE_CLIENT_ID: {GOOGLE_CLIENT_ID}")

class GoogleAuthHandler:
    def __init__(self):
        self.google_client_id = GOOGLE_CLIENT_ID
        
    def verify_google_token(self, token):
        """Verify Google ID token and extract user information"""
        if not self.google_client_id:
            logging.error("GOOGLE_CLIENT_ID is not set. Cannot verify Google token.")
            return {
                'success': False,
                'error': 'Google OAuth is not properly configured on the server.'
            }
        try:
            # Verify the token with clock skew tolerance
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                self.google_client_id,
                clock_skew_in_seconds=300  # Allow 5 minutes of clock skew
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
    
    def handle_google_auth_login(self, data):
        """Handle Google authentication login (Request ID 66)"""
        try:
            credential = data.get('credential')
            client_id = data.get('clientId')

            if not credential:
                return {
                    'success': False,
                    'error': 'Missing credential'
                }

            # Verify Google token
            verification = self.verify_google_token(credential)
            if not verification['success']:
                return {
                    'success': False,
                    'error': verification['error']
                }

            google_user = verification['user']

            # Defensive: handle both google_id and googleId
            google_id = google_user.get('google_id') or google_user.get('googleId')
            email = google_user.get('email')

            # Use database session context manager
            with get_db_session() as session:
                users_controller = UsersController(session)

                # Check if user exists in database
                existing_user = users_controller.find_user_by_google_id_or_email(
                    google_id,
                    email
                )

                if existing_user:
                    # User exists, log them in
                    # Update last login
                    users_controller.update_user_last_login(existing_user.id)

                    # Create user session
                    user_session = UserSession(user_id=existing_user.id, is_manager=existing_user.isManager)

                    response_data = {
                        'user_exists': True,
                        'username': existing_user.username,
                        'is_manager': existing_user.isManager,
                        'email': existing_user.email,
                        'google_linked': True,
                        'user_session': user_session,
                        'google_id': google_id
                    }

                    return {
                        'success': True,
                        'data': response_data
                    }
                else:
                    # User doesn't exist, need account linking or creation
                    response_data = {
                        'user_exists': False,
                        'google_user_info': google_user
                    }

                    return {
                        'success': True,
                        'data': response_data
                    }

        except Exception as e:
            logging.error(f"Google auth login error: {e}")
            return {
                'success': False,
                'error': 'Authentication failed'
            }
    
    def handle_link_google_account(self, data):
        """Handle linking Google account to existing account (Request ID 67)"""
        try:
            username = data.get('username')
            password = data.get('password')
            google_data = data.get('googleData')

            # Use database session context manager
            with get_db_session() as session:
                users_controller = UsersController(session)

                # Verify existing user credentials
                user_exists, is_manager = users_controller.check_user_existence_and_manager_status(username, password)
                if not user_exists:
                    return {
                        'success': False,
                        'error': 'Invalid username or password'
                    }

                # Get the actual user object
                user_id = users_controller.get_user_id_by_username_and_password(username, password)
                user = users_controller.get_entity(user_id)

                # Check if Google account is already linked to another user
                existing_google_user = users_controller.find_user_by_google_id(google_data['sub'])
                if existing_google_user and existing_google_user.id != user.id:
                    return {
                        'success': False,
                        'error': 'Google account already linked to another user'
                    }

                # Link Google account to existing user
                users_controller.link_google_account_to_user(user.id, google_data)

                # Create user session
                user_session = UserSession(user_id=user.id, is_manager=user.isManager)

                response_data = {
                    'username': user.username,
                    'is_manager': is_manager,
                    'google_linked': True,
                    'user_session': user_session
                }

                return {
                    'success': True,
                    'data': response_data
                }
            
        except Exception as e:
            logging.error(f"Link Google account error: {e}")
            return {
                'success': False,
                'error': 'Failed to link Google account'
            }
    
    def handle_create_account_with_google(self, data):
        """Handle creating new account with Google (Request ID 68)"""
        try:
            username = data.get('username')
            google_data = data.get('googleData')
            name = data.get('name')
            email = data.get('email')

            # Use database session context manager
            with get_db_session() as session:
                users_controller = UsersController(session)

                # Check if username already exists
                if users_controller.check_username_existence(username):
                    return {
                        'success': False,
                        'error': 'Username already exists'
                    }

                # Check if Google account is already linked
                existing_google_user = users_controller.find_user_by_google_id(google_data['sub'])
                if existing_google_user:
                    return {
                        'success': False,
                        'error': 'Google account already linked to another user'
                    }

                # Create new user account
                new_user = users_controller.create_user_with_google({
                    'username': username,
                    'name': name,
                    'email': email,
                    'google_id': google_data['sub'],
                    'google_picture': google_data.get('picture'),
                    'is_manager': False,  # New accounts are employees by default
                    'approved': False  # Require approval unless auto-approved
                })

                # Create user session
                user_session = UserSession(user_id=new_user.id, is_manager=new_user.isManager)

                response_data = {
                    'username': new_user.username,
                    'is_manager': new_user.isManager,
                    'google_linked': True,
                    'user_session': user_session
                }

                return {
                    'success': True,
                    'data': response_data
                }
            
        except Exception as e:
            logging.error(f"Create account with Google error: {e}")
            return {
                'success': False,
                'error': 'Failed to create account'
            }

    def handle_google_signup_employee(self, data):
        """Handle Google signup for employee (Request ID 69)"""
        try:
            username = data.get('username')
            google_data = data.get('googleData')
            name = data.get('name')
            email = data.get('email')
            business_name = data.get('businessName')  # TODO: Handle business_name
            certifications = data.get('certifications', {})  # TODO: Handle certifications

            # Use database session context manager
            with get_db_session() as session:
                users_controller = UsersController(session)

                # Check if username already exists
                if users_controller.check_username_existence(username):
                    return {
                        'success': False,
                        'error': 'Username already exists'
                    }

                # Check if Google account is already linked
                existing_google_user = users_controller.find_user_by_google_id(google_data['sub'])
                if existing_google_user:
                    return {
                        'success': False,
                        'error': 'Google account already linked to another user'
                    }

                # Create new employee account
                new_user = users_controller.create_user_with_google({
                    'username': username,
                    'name': name,
                    'email': email,
                    'google_id': google_data['sub'],
                    'google_picture': google_data.get('picture'),
                    'is_manager': False,
                    'approved': False  # Require approval for employees
                })

                # TODO: Handle business_name and certifications
                # This would require additional database operations

                # Create user session
                user_session = UserSession(user_id=new_user.id, is_manager=new_user.isManager)

                response_data = {
                    'username': new_user.username,
                    'is_manager': new_user.isManager,
                    'google_linked': True,
                    'user_session': user_session
                }

                return {
                    'success': True,
                    'data': response_data
                }

        except Exception as e:
            logging.error(f"Google signup employee error: {e}")
            return {
                'success': False,
                'error': 'Failed to create employee account'
            }

    def handle_google_signup_manager(self, data):
        """Handle Google signup for manager (Request ID 70)"""
        try:
            logging.info(f"Google signup manager data received: {data}")

            username = data.get('username')
            google_data = data.get('googleData')
            name = data.get('name')
            email = data.get('email')

            logging.info(f"Extracted data - username: {username}, name: {name}, email: {email}")
            logging.info(f"Google data: {google_data}")

            # Use database session context manager
            with get_db_session() as session:
                users_controller = UsersController(session)

                # Check if username already exists
                if users_controller.check_username_existence(username):
                    return {
                        'success': False,
                        'error': 'Username already exists'
                    }

                # Check if Google account is already linked
                existing_google_user = users_controller.find_user_by_google_id(google_data['sub'])
                if existing_google_user:
                    return {
                        'success': False,
                        'error': 'Google account already linked to another user'
                    }

                # Create new manager account
                new_user = users_controller.create_user_with_google({
                    'username': username,
                    'name': name,
                    'email': email,
                    'google_id': google_data['sub'],
                    'google_picture': google_data.get('picture'),
                    'is_manager': True,
                    'approved': True  # Auto-approve managers
                })

                # Create user session
                user_session = UserSession(user_id=new_user.id, is_manager=new_user.isManager)

                response_data = {
                    'username': new_user.username,
                    'is_manager': new_user.isManager,
                    'google_linked': True,
                    'user_session': user_session
                }

                return {
                    'success': True,
                    'data': response_data
                }

        except Exception as e:
            logging.error(f"Google signup manager error: {e}")
            return {
                'success': False,
                'error': 'Failed to create manager account'
            }

    def handle_google_signup_client(self, data):
        """Handle Google signup for client (Request ID 71)"""
        try:
            username = data.get('username')
            google_data = data.get('googleData')
            name = data.get('name')
            email = data.get('email')
            company_name = data.get('companyName')  # TODO: Handle company_name

            # Use database session context manager
            with get_db_session() as session:
                users_controller = UsersController(session)

                # Check if username already exists
                if users_controller.check_username_existence(username):
                    return {
                        'success': False,
                        'error': 'Username already exists'
                    }

                # Check if Google account is already linked
                existing_google_user = users_controller.find_user_by_google_id(google_data['sub'])
                if existing_google_user:
                    return {
                        'success': False,
                        'error': 'Google account already linked to another user'
                    }

                # TODO: Handle client company creation
                # This would require additional database operations for client companies

                # Create new client account
                new_user = users_controller.create_user_with_google({
                    'username': username,
                    'name': name,
                    'email': email,
                    'google_id': google_data['sub'],
                    'google_picture': google_data.get('picture'),
                    'is_manager': False,  # Clients are not managers
                    'approved': True  # Auto-approve clients
                })

                # Create user session
                user_session = UserSession(user_id=new_user.id, is_manager=new_user.isManager)

                response_data = {
                    'username': new_user.username,
                    'is_manager': new_user.isManager,
                    'google_linked': True,
                    'user_session': user_session
                }

                return {
                    'success': True,
                    'data': response_data
                }

        except Exception as e:
            logging.error(f"Google signup client error: {e}")
            return {
                'success': False,
                'error': 'Failed to create client account'
            }

# Global instance for use in Server.py
google_auth_instance = GoogleAuthHandler()

def google_auth_handler(data, user_session):
    """Main Google auth handler function called by Server.py"""
    try:
        # Determine which Google auth operation to perform based on data
        operation = data.get('operation', 'login')

        if operation == 'login':
            return google_auth_instance.handle_google_auth_login(data)
        elif operation == 'link':
            return google_auth_instance.handle_link_google_account(data)
        elif operation == 'create':
            return google_auth_instance.handle_create_account_with_google(data)
        elif operation == 'signup_employee':
            return google_auth_instance.handle_google_signup_employee(data)
        elif operation == 'signup_manager':
            return google_auth_instance.handle_google_signup_manager(data)
        elif operation == 'signup_client':
            return google_auth_instance.handle_google_signup_client(data)
        else:
            return {
                'success': False,
                'error': f'Unknown Google auth operation: {operation}'
            }
    except Exception as e:
        logging.error(f"Google auth handler error: {e}")
        return {
            'success': False,
            'error': 'Google authentication failed'
        }

