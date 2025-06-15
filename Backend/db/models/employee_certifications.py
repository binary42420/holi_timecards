from sqlalchemy import Column, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class EmployeeCertification(Base):
    """
    Model for tracking employee certifications/perks.
    All employees are stagehands by default, with optional additional certifications.
    """
    __tablename__ = 'employee_certifications'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Certification flags
    can_crew_chief = Column(Boolean, default=False, nullable=False)
    can_forklift = Column(Boolean, default=False, nullable=False)
    can_truck = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="certifications")
    
    def to_dict(self):
        """Convert certification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'can_crew_chief': self.can_crew_chief,
            'can_forklift': self.can_forklift,
            'can_truck': self.can_truck,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_role_list(self):
        """Get list of roles this employee is certified for."""
        roles = ['Stagehand']  # Everyone is a stagehand
        
        if self.can_crew_chief:
            roles.append('Crew Chief')
        if self.can_forklift:
            roles.append('Forklift Operator')
        if self.can_truck:
            roles.append('Truck Driver')
            
        return roles
    
    def can_fill_role(self, role):
        """Check if employee can fill a specific role."""
        role_lower = role.lower()
        
        if role_lower in ['stagehand', 'sh']:
            return True  # Everyone can be a stagehand
        elif role_lower in ['crew chief', 'cc']:
            return self.can_crew_chief
        elif role_lower in ['forklift operator', 'forklift', 'fo']:
            return self.can_forklift
        elif role_lower in ['truck driver', 'truck', 'trk']:
            return self.can_truck
        
        return False
