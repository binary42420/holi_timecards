from __future__ import annotations
from sqlalchemy.orm import Session
from db.controllers.base_controller import BaseController
from db.repositories.users_repository import UsersRepository
from db.services.users_service import UsersService
from typing import Tuple


class UsersController(BaseController):
    """
    UserController Class

    Controller class for managing user entities.
    """

    def __init__(self, db: Session):
        """
        Initializes the UserController with a database session.

        Parameters:
            db (Session): SQLAlchemy Session for database interactions.
        """
        self.repository = UsersRepository(db)
        self.service = UsersService(self.repository)
        super().__init__(self.repository, self.service)

    def check_user_existence_and_manager_status(self, username: str, password: str) -> Tuple[bool, bool]:
        """
        Check if a user with the given username and password exists and if they are a manager.

        Parameters:
            username (str): The username to check.
            password (str): The password to check.

        Returns:
            Tuple[bool, bool]: A tuple of booleans. The first boolean indicates whether the user exists,
                               and the second boolean indicates whether the user is a manager.
        """
        # Delegate the functionality to the service layer
        return self.service.check_user_existence_and_manager_status(username, password)

    def get_user_id_by_username_and_password(self, username: str, password: str):
        """
        Retrieves the user ID by username and password.

        Parameters:
            username (str): The username of the user to retrieve.
            password (str): The password of the user to retrieve.

        Returns:
            Optional[int]: The user ID if the user exists, None otherwise.
        """
        return self.service.get_user_id_by_username_and_password(username, password)

    def get_user_id_by_username(self, username: str):
        """
        Retrieves the user ID by username.

        Parameters:
            username (str): The username of the user to retrieve.

        Returns:
            Optional[int]: The user ID if the user exists, None otherwise.
        """
        return self.service.get_user_id_by_username(username)

    def get_user_id_by_name(self, name: str):
        """
        Retrieves the user ID by username.

        Parameters:
            name (str): The name of the user to retrieve.

        Returns:
            Optional[int]: The user ID if the user exists, None otherwise.
        """
        return self.service.get_user_id_by_name(name)

    def get_username_by_id(self, user_id: str):
        """
        Retrieves the username by user ID.

        Parameters:
            user_id (str): The user ID of the user to retrieve.

        Returns:
            Optional[str]: The username if the user exists, None otherwise.
        """
        return self.service.get_username_by_id(user_id)

    def get_name_by_id(self, user_id: str):
        """
        Retrieves the name by user ID.

        Parameters:
            user_id (int): The user ID of the user to retrieve.

        Returns:
            str: The name if the user exists, None otherwise.
        """
        return self.service.get_name_by_id(user_id)

    def approve_user(self, user_name: str):
        """
        Approve a user by setting isApproval to True.

        Parameters:
            user_name (str): The user_name of the user to approve.
        """
        # Call the repository method to approve the user
        self.repository.approve_user(user_name)

    def check_username_existence(self, username: str) -> bool:
        """
        Check if a username already exists in the database.

        Parameters:
            username (str): The username to check.

        Returns:
            bool: True if the username exists, False otherwise.
        """
        return self.repository.get_user_by_username(username) is not None

    # Google OAuth methods
    def find_user_by_google_id(self, google_id: str):
        """
        Find user by Google ID.

        Parameters:
            google_id (str): The Google OAuth ID to search for.

        Returns:
            User: The user object if found, None otherwise.
        """
        return self.repository.get_user_by_google_id(google_id)

    def find_user_by_google_id_or_email(self, google_id: str, email: str):
        """
        Find user by Google ID or email address.

        Parameters:
            google_id (str): The Google OAuth ID to search for.
            email (str): The email address to search for.

        Returns:
            User: The user object if found, None otherwise.
        """
        # First try to find by Google ID
        user = self.repository.get_user_by_google_id(google_id)
        if user:
            return user

        # If not found, try to find by email
        return self.repository.get_user_by_email(email)

    def link_google_account_to_user(self, user_id: int, google_data: dict):
        """
        Link Google account to existing user.

        Parameters:
            user_id (int): The user ID to link Google account to.
            google_data (dict): Google user information.
        """
        return self.repository.link_google_account(user_id, google_data)

    def create_user_with_google(self, user_data: dict):
        """
        Create new user with Google information.

        Parameters:
            user_data (dict): User data including Google information.

        Returns:
            User: The created user object.
        """
        return self.repository.create_user_with_google(user_data)

    def update_user_last_login(self, user_id: int):
        """
        Update user's last login time.

        Parameters:
            user_id (int): The user ID to update.
        """
        return self.repository.update_last_login(user_id)

    def get_user_by_username(self, username: str):
        """
        Get user by username.

        Parameters:
            username (str): The username to search for.

        Returns:
            User: The user object if found, None otherwise.
        """
        return self.repository.get_user_by_username(username)

    def find_user_by_email(self, email: str):
        """
        Find user by email address.

        Parameters:
            email (str): The email address to search for.

        Returns:
            User: The user object if found, None otherwise.
        """
        return self.repository.get_user_by_email(email)

    def get_user_by_username(self, username: str):
        """
        Get user by username.

        Parameters:
            username (str): The username to search for.

        Returns:
            User: The user object if found, None otherwise.
        """
        return self.repository.get_user_by_username(username)

    def find_user_by_email(self, email: str):
        """
        Find user by email address.

        Parameters:
            email (str): The email address to search for.

        Returns:
            User: The user object if found, None otherwise.
        """
        return self.repository.get_user_by_email(email)

    def get_all_approved_workers(self):
        """
        Get all approved workers (non-manager users).

        Returns:
            List[User]: List of approved worker users.
        """
        try:
            from sqlalchemy import and_
            from ..models import User

            query = self.repository.db.query(User).filter(
                and_(
                    User.isApproval == True,
                    User.isManager == False,
                    User.isActive == True
                )
            )

            return query.all()

        except Exception as e:
            print(f"Error getting all approved workers: {e}")
            return []

    def get_users_by_client_company_id(self, client_company_id: int):
        """
        Retrieves all users belonging to a specific client company.

        Parameters:
            client_company_id (int): The client company ID.

        Returns:
            List[User]: List of users belonging to the client company.
        """
        return self.repository.get_users_by_client_company_id(client_company_id)

    def get_all_client_users(self):
        """
        Retrieves all users that are client users (have client_company_id set).

        Returns:
            List[User]: List of all client users.
        """
        return self.repository.get_all_client_users()
