from sqlalchemy.orm import Session
from db.models import Job
from db.repositories.base_repository import BaseRepository
from typing import List


class JobsRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Job)

    def get_jobs_by_workplace_id(self, workplace_id: int) -> List[Job]:
        """
        DEPRECATED: Use get_all_active_jobs() instead.
        Retrieves all jobs associated with a specific workplace (manager).
        """
        return self.db.query(Job).filter(Job.workplace_id == workplace_id).all()

    def get_all_active_jobs(self) -> List[Job]:
        """
        Retrieves all active jobs for Hands on Labor.
        Since there's only one company, all jobs are available to all managers.
        """
        return self.db.query(Job).filter(Job.is_active == True).order_by(Job.created_at.desc()).all()

    def get_jobs_by_client_company_id(self, client_company_id: int):
        """
        Retrieves all jobs for a specific client company.

        Parameters:
            client_company_id (int): The client company ID.

        Returns:
            List[Job]: List of jobs for the client company.
        """
        return self.db.query(Job).filter(Job.client_company_id == client_company_id).all()
