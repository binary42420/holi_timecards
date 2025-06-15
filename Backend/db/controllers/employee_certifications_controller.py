from sqlalchemy.orm import Session
from typing import List, Optional
from ..repositories.employee_certifications_repository import EmployeeCertificationsRepository
from ..services.employee_certifications_service import EmployeeCertificationsService
from .base_controller import BaseController


class EmployeeCertificationsController(BaseController):
    """
    Controller for managing employee certifications.
    """

    def __init__(self, db: Session):
        self.repository = EmployeeCertificationsRepository(db)
        self.service = EmployeeCertificationsService(self.repository)
        super().__init__(self.repository, self.service)

    def get_certification_by_user_id(self, user_id: int):
        """
        Get certification record for a specific user.
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            EmployeeCertification or None
        """
        return self.repository.get_by_user_id(user_id)

    def create_or_update_certification(self, user_id: int, certification_data: dict):
        """
        Create or update certification for a user.
        
        Args:
            user_id (int): The user's ID
            certification_data (dict): Certification flags
            
        Returns:
            EmployeeCertification: The created/updated certification
        """
        existing = self.repository.get_by_user_id(user_id)
        
        if existing:
            # Update existing certification
            update_data = {
                'can_crew_chief': certification_data.get('can_crew_chief', existing.can_crew_chief),
                'can_forklift': certification_data.get('can_forklift', existing.can_forklift),
                'can_truck': certification_data.get('can_truck', existing.can_truck)
            }
            return self.repository.update_entity(existing.id, update_data)
        else:
            # Create new certification
            cert_data = {
                'user_id': user_id,
                'can_crew_chief': certification_data.get('can_crew_chief', False),
                'can_forklift': certification_data.get('can_forklift', False),
                'can_truck': certification_data.get('can_truck', False)
            }
            return self.repository.create_entity(cert_data)

    def get_employees_by_role_capability(self, role: str, workplace_id: int = None) -> List[dict]:
        """
        Get all employees who can fill a specific role.
        
        Args:
            role (str): Role to filter by ('crew_chief', 'forklift', 'truck', 'stagehand')
            workplace_id (int): Optional workplace filter
            
        Returns:
            List[dict]: List of employee data with certification info
        """
        return self.service.get_employees_by_role_capability(role, workplace_id)

    def get_all_employees_with_certifications(self, workplace_id: int = None) -> List[dict]:
        """
        Get all employees with their certification information.
        
        Args:
            workplace_id (int): Optional workplace filter
            
        Returns:
            List[dict]: List of employee data with certification info
        """
        return self.service.get_all_employees_with_certifications(workplace_id)
