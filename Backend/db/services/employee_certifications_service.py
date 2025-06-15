from typing import List, Optional
from main import get_db_session
from ..repositories.employee_certifications_repository import EmployeeCertificationsRepository
from ..controllers.users_controller import UsersController
from config.constants import db


class EmployeeCertificationsService:
    """
    Service layer for employee certifications business logic.
    """

    def __init__(self, repository: EmployeeCertificationsRepository):
        self.repository = repository

    def get_employees_by_role_capability(self, role: str, workplace_id: int = None) -> List[dict]:
        """
        Get all employees who can fill a specific role.
        For Hands on Labor: workplace_id is ignored (single company).

        Args:
            role (str): Role to filter by
            workplace_id (int): Ignored - kept for backward compatibility

        Returns:
            List[dict]: List of employee data with certification info
        """
        # Get certifications for users who can fill the role
        certifications = self.repository.get_users_with_role_capability(role)

        employees = []
        with get_db_session() as session:
            users_controller = UsersController(session)

        for cert in certifications:
            try:
                user = users_controller.get_entity(cert.user_id)
                if not user or not user.isActive or not user.isApproval:
                    continue

                # For Hands on Labor: All employees work for same company
                employee_data = {
                    'id': user.id,
                    'name': user.name,
                    'username': user.username,
                    'employee_type': user.employee_type.value if user.employee_type else None,
                    'certifications': cert.to_dict(),
                    'available_roles': cert.get_role_list()
                }
                employees.append(employee_data)

            except Exception as e:
                print(f"Error processing certification for user {cert.user_id}: {e}")
                continue

        return employees

    def get_all_employees_with_certifications(self, workplace_id: int = None) -> List[dict]:
        """
        Get all employees with their certification information.
        For Hands on Labor: workplace_id is ignored (single company).

        Args:
            workplace_id (int): Ignored - kept for backward compatibility

        Returns:
            List[dict]: List of employee data with certification info
        """
        employees = []

        # For Hands on Labor: Get all employees (single company)
        try:
            all_certifications = self.repository.get_all_with_users()

            for cert in all_certifications:
                if cert.user and cert.user.isActive and cert.user.isApproval:
                    employee_data = {
                        'id': cert.user.id,
                        'name': cert.user.name,
                        'username': cert.user.username,
                        'employee_type': cert.user.employee_type.value if cert.user.employee_type else None,
                        'certifications': cert.to_dict(),
                        'available_roles': cert.get_role_list()
                    }
                    employees.append(employee_data)

        except Exception as e:
            print(f"Error getting all employees with certifications: {e}")
            return []

        return employees
