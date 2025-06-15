class UserSession:
    """
    Represents an active user session in the site.

    Attributes:
        _user_id (str): The user's ID.
        _is_manager (bool): True if the user is a manager, False if a worker.
    """

    def __init__(self, user_id: str, is_manager: bool, username: str = None, email: str = None, is_admin: bool = False):
        """
        Initializes a UserSession object for Hands on Labor (single company system).

        Parameters:
            user_id (int): The user's ID.
            is_manager (bool): True if the user is a manager, False if a worker.
            username (str): The user's username.
            email (str): The user's email.
            is_admin (bool): True if the user is an admin, False otherwise.
        """
        self._user_id = user_id
        self._is_manager = is_manager
        self._username = username
        self._email = email
        self._is_admin = is_admin

    @property
    def get_id(self) -> str:
        """
        Retrieves the user's ID.

        Returns:
            str: The user's ID.
        """
        return self._user_id

    def can_access_manager_page(self) -> bool:
        """
        Checks if the user can access manager-specific pages.

        Returns:
            bool: True if the user is a manager, False otherwise.
        """
        return self._is_manager

    def can_access_worker_page(self) -> bool:
        """
        Checks if the user can access worker-specific pages.

        Returns:
            bool: True if the user is a worker, False otherwise.
        """
        return not self._is_manager

    def is_admin(self) -> bool:
        """
        Checks if the user is an admin.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return getattr(self, '_is_admin', False)

    def can_access_admin_features(self) -> bool:
        """
        Checks if the user can access admin-specific features.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return self.is_admin()

    def has_elevated_permissions(self) -> bool:
        """
        Checks if the user has elevated permissions (admin or manager).

        Returns:
            bool: True if the user is an admin or manager, False otherwise.
        """
        return self._is_manager or self.is_admin()

    @property
    def username(self) -> str:
        """
        Retrieves the user's username.

        Returns:
            str: The user's username.
        """
        return self._username



    @property
    def email(self) -> str:
        """
        Retrieves the user's email.

        Returns:
            str: The user's email.
        """
        return self._email
