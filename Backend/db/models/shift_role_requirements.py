from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ShiftRoleRequirement(Base):
    """
    Model for tracking role requirements for each shift.
    Defines how many of each role type are needed for a shift.
    """
    __tablename__ = 'shift_role_requirements'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    shift_id = Column(Integer, ForeignKey('shifts.id'), nullable=False)
    
    # Role counts required
    crew_chiefs_needed = Column(Integer, default=0, nullable=False)
    stagehands_needed = Column(Integer, default=0, nullable=False)
    forklift_operators_needed = Column(Integer, default=0, nullable=False)
    truck_drivers_needed = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    shift = relationship("Shift", back_populates="role_requirements")
    
    def to_dict(self):
        """Convert role requirements to dictionary."""
        return {
            'id': self.id,
            'shift_id': self.shift_id,
            'crew_chiefs_needed': self.crew_chiefs_needed,
            'stagehands_needed': self.stagehands_needed,
            'forklift_operators_needed': self.forklift_operators_needed,
            'truck_drivers_needed': self.truck_drivers_needed,
            'total_workers_needed': self.get_total_workers_needed(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_total_workers_needed(self):
        """Calculate total number of workers needed for this shift."""
        return (
            self.crew_chiefs_needed + 
            self.stagehands_needed + 
            self.forklift_operators_needed + 
            self.truck_drivers_needed
        )
    
    def get_role_breakdown(self):
        """Get a breakdown of roles needed."""
        breakdown = []
        
        if self.crew_chiefs_needed > 0:
            breakdown.append({
                'role': 'Crew Chief',
                'code': 'CC',
                'count': self.crew_chiefs_needed,
                'color': '#28a745'  # Green
            })
        
        if self.forklift_operators_needed > 0:
            breakdown.append({
                'role': 'Forklift Operator',
                'code': 'FO',
                'count': self.forklift_operators_needed,
                'color': '#fd7e14'  # Orange
            })
        
        if self.truck_drivers_needed > 0:
            breakdown.append({
                'role': 'Truck Driver',
                'code': 'TRK',
                'count': self.truck_drivers_needed,
                'color': '#6f42c1'  # Purple
            })
        
        if self.stagehands_needed > 0:
            breakdown.append({
                'role': 'Stagehand',
                'code': 'SH',
                'count': self.stagehands_needed,
                'color': '#007bff'  # Blue
            })
        
        return breakdown
