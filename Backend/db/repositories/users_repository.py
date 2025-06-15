from sqlalchemy.orm import Session
from db.models import User
from db.repositories.base_repository import BaseRepository
from db.repositories.userRequests_repository import UserRequestsRepository
from datetime import datetime


class UsersRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def delete_entity(self, entity_id: str):
        """
        """
        # If the user have a request, delete it
        userRequestsRepository = UserRequestsRepository(self.db)
        try:
            user_request = userRequestsRepository.get_entity(entity_id)
            if user_request:
                userRequestsRepository.delete_entity(entity_id)
        except:
            pass

        # Delete the user
        super().delete_entity(entity_id)

    def check_user_credentials(self, username: str, password: str) -> bool:
        """
        Check if a user with the given username and password exists.

        Parameters:
            username (str): The username to check.
            password (str): The password to check.

        Returns:
            bool: True if a user with the provided credentials exists, False otherwise.
        """
        # Query the database to find a user with the given username and password
        user = self.db.query(User).filter(User.username == username, User.password == password).first()
        # If user is not None, it means a user with the provided credentials exists
        return user is not None

    def is_manager_by_username_and_password(self, username: str, password: str) -> bool:
        """
        Check if a user with the given username and password is a manager.

        Parameters:
            username (str): The username to check.
            password (str): The password to check.

        Returns:
            bool: True if the user with the provided credentials is a manager, False otherwise.
        """
        # Query the database to find a user with the given username and password
        user = self.db.query(User).filter(User.username == username, User.password == password).first()

        # Check if the user exists and is a manager
        return user is not None and user.isManager

    def get_user_by_username_and_password(self, username: str, password: str):
        """
        Retrieves a user by username and password.

        Parameters:
            username (str): The username of the user to retrieve.
            password (str): The password of the user to retrieve.

        Returns:
            User: The user object if found, None otherwise.
        """
        # Query the database to find a user with the given username and password
        return self.db.query(User).filter(User.username == username, User.password == password).first()

    def get_user_by_username(self, username: str):
        """
        Retrieves a user by username.

        Parameters:
            username (str): The username of the user to retrieve.

        Returns:
            User: The user object if found, None otherwise.
        """
        # Query the database to find a user with the given username and password
        return self.db.query(User).filter(User.username == username).first()

    def custom_operation_for_test_only(self):
        return 30

    def approve_user(self, user_name: str):
        """
        Approve a user by setting isApproval to True.

        Parameters:
            user_name (str): The user_name of the user to approve.
        """
        # Retrieve the user by ID
        user = self.get_user_by_username(user_name)
        # If user is found, update isApproval attribute and commit changes
        if user:
            user.isApproval = True
            self.db.commit()

    def get_user_by_name(self, name: str):
        """
        Retrieves a user by name.

        Parameters:
            name (str): The name of the user to retrieve.

        Returns:
            User: The user object if found, None otherwise.
        """
        return self.db.query(User).filter(User.name == name).first()

    # Google OAuth methods
    def get_user_by_google_id(self, google_id: str):
        """
        Retrieves a user by Google ID.

        Parameters:
            google_id (str): The Google ID of the user to retrieve.

        Returns:
            User: The user object if found, None otherwise.
        """
        return self.db.query(User).filter(User.google_id == google_id).first()

    def get_user_by_email(self, email: str):
        """
        Retrieves a user by email address.

        Parameters:
            email (str): The email address of the user to retrieve.

        Returns:
            User: The user object if found, None otherwise.
        """
        return self.db.query(User).filter(User.email == email).first()

    def link_google_account(self, user_id: int, google_data: dict):
        """
        Link Google account to existing user.

        Parameters:
            user_id (int): The user ID to link Google account to.
            google_data (dict): Google user information.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.google_id = google_data.get('sub')
                user.email = google_data.get('email')
                user.google_picture = google_data.get('picture')
                user.last_login = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e

    def create_user_with_google(self, user_data: dict):
        """
        Create new user with Google information.

        Parameters:
            user_data (dict): User data including Google information.

        Returns:
            User: The created user object.
        """
        try:
            new_user = User(
                username=user_data['username'],
                name=user_data['name'],
                email=user_data['email'],
                google_id=user_data['google_id'],
                google_picture=user_data.get('google_picture'),
                isManager=user_data.get('is_manager', False),
                isApproval=user_data.get('approved', False),
                isActive=True,
                last_login=datetime.now(),
                password=None  # No password for Google OAuth users
            )

            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
        except Exception as e:
            self.db.rollback()
            raise e

    def get_users_by_client_company_id(self, client_company_id: int):
        """
        Retrieves all users belonging to a specific client company.

        Parameters:
            client_company_id (int): The client company ID.

        Returns:
            List[User]: List of users belonging to the client company.
        """
        return self.db.query(User).filter(User.client_company_id == client_company_id).all()

    def get_all_client_users(self):
        """
        Retrieves all users that are client users (have client_company_id set).

        Returns:
            List[User]: List of all client users.
        """
        return self.db.query(User).filter(User.client_company_id.isnot(None)).all()

    def update_last_login(self, user_id: int):
        """
        Update user's last login time.

        Parameters:
            user_id (int): The user ID to update.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.now()
                self.db.commit()
                return True
            return False
        except Exception as e:
            self.db.rollback()
            raise e
