from sqlalchemy.exc import NoResultFound
from main import get_db_session
from db.controllers.users_controller import UsersController
from security.secure_session import password_security, secure_session_manager
import logging

logger = logging.getLogger(__name__)

class BackendAuthenticationUser:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.error_message = ""

    def __is_user_exists(self):
        """
        Checks if the user exists in the database.

        Returns: True if the user exists, else False.
        """
        try:
            with get_db_session() as session:
                users_controller = UsersController(session)
                user = users_controller.get_user_by_username(self.username)
                return user is not None
        except Exception as e:
            logger.error(f"Database error checking user existence: {e}")
            self.error_message = "Database error occurred"
            return False

    def __is_username_and_password_match(self):
        """
        Checks if the username and password match using secure password verification.

        Returns: True if the username and password match, else False.
        """
        try:
            with get_db_session() as session:
                users_controller = UsersController(session)
                user = users_controller.get_user_by_username(self.username)

                if not user:
                    self.error_message = f"User with username {self.username} does not exist"
                    return False

                # Handle legacy plain text passwords and new hashed passwords
                if user.password:
                    # Check if password is already hashed (starts with $2b$ for bcrypt)
                    if user.password.startswith('$2b$'):
                        # Use secure password verification
                        if password_security.verify_password(self.password, user.password):
                            return True
                    else:
                        # Legacy plain text password - verify and upgrade
                        if user.password == self.password:
                            # Upgrade to hashed password
                            hashed_password = password_security.hash_password(self.password)
                            users_controller.update_user_password(user.id, hashed_password)
                            logger.info(f"Upgraded password security for user {self.username}")
                            return True

                self.error_message = "Username and password do not match"
                return False

        except NoResultFound:
            self.error_message = f"User with username {self.username} does not exist"
            return False
        except Exception as e:
            logger.error(f"Database error during password verification: {e}")
            self.error_message = "Authentication error occurred"
            return False

    def validate_login(self):
        """
        Validates the user login.

        Returns: True if the user is logged in, else False.
        """
        if self.__is_user_exists() and self.__is_username_and_password_match():
            return True
        else:
            return False

    def validate_registration(self):
        """
        Validates the user registration.

        Returns: True if the user is registered, else False.
        """
        if self.__is_user_exists():
            self.error_message = f"User with username {self.username} already exists"  # Overwrite the error message
            return False
        else:
            self.users_controller.create_entity({"username": self.username, "password": self.password})
            return True

    def get_error_message(self):
        """
        Returns: The error message that occurred during the login process.
        """
        return self.error_message
