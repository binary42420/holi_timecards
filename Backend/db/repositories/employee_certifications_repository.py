from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound
from typing import Optional, List
from .base_repository import BaseRepository
from ..models import EmployeeCertification


class EmployeeCertificationsRepository(BaseRepository):
    """
    Repository for managing employee certifications.
    """

    def __init__(self, db: Session):
        super().__init__(db, EmployeeCertification)

    def get_by_user_id(self, user_id: int) -> Optional[EmployeeCertification]:
        """
        Get certification record for a specific user.
        
        Args:
            user_id (int): The user's ID
            
        Returns:
            EmployeeCertification or None
        """
        try:
            return self.db.query(EmployeeCertification).filter(
                EmployeeCertification.user_id == user_id
            ).first()
        except NoResultFound:
            return None

    def get_users_with_role_capability(self, role: str) -> List[EmployeeCertification]:
        """
        Get all certifications for users who can fill a specific role.
        
        Args:
            role (str): Role to filter by
            
        Returns:
            List[EmployeeCertification]: List of certifications
        """
        query = self.db.query(EmployeeCertification)
        
        if role.lower() in ['crew_chief', 'cc']:
            query = query.filter(EmployeeCertification.can_crew_chief == True)
        elif role.lower() in ['forklift', 'forklift_operator', 'fo']:
            query = query.filter(EmployeeCertification.can_forklift == True)
        elif role.lower() in ['truck', 'truck_driver', 'trk']:
            query = query.filter(EmployeeCertification.can_truck == True)
        elif role.lower() in ['stagehand', 'sh']:
            # Everyone can be a stagehand, so return all certifications
            pass
        else:
            # Unknown role, return empty list
            return []
            
        return query.all()

    def get_all_with_users(self) -> List[EmployeeCertification]:
        """
        Get all certifications with user data loaded.
        
        Returns:
            List[EmployeeCertification]: List of certifications with user relationships loaded
        """
        return self.db.query(EmployeeCertification).join(
            EmployeeCertification.user
        ).all()
