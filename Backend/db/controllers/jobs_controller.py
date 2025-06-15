from sqlalchemy.orm import Session
from db.models import Job
from db.repositories.jobs_repository import JobsRepository
from db.services.jobs_service import JobsService
from db.controllers.base_controller import BaseController
from typing import List, Dict # Corrected: Dict instead of dict


class JobsController(BaseController):
    def __init__(self, db: Session):
        self.repository = JobsRepository(db)
        self.service = JobsService(self.repository)
        super().__init__(self.repository, self.service)

    def create_job(self, job_data: dict) -> dict:
        """
        Creates a new job and returns its details.
        job_data should include: name, client_company_id, venue_name, venue_address
        """
        job = self.service.create_job(job_data)
        return {
            "id": job.id,
            "name": job.name,
            "client_company_id": job.client_company_id,
            "venue_name": job.venue_name,
            "venue_address": job.venue_address,
            "venue_contact_info": job.venue_contact_info,
            "description": job.description,
            "created_by": job.created_by,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "is_active": job.is_active,
            "estimated_start_date": job.estimated_start_date.isoformat() if job.estimated_start_date else None,
            "estimated_end_date": job.estimated_end_date.isoformat() if job.estimated_end_date else None
        }

    def get_jobs_by_workplace_id(self, workplace_id: int) -> List[dict]:
        """
        DEPRECATED: Use get_all_active_jobs() instead.
        Retrieves jobs for a given workplace ID (manager's user_id).
        """
        jobs = self.service.get_jobs_by_workplace_id(workplace_id)
        return [
            {
                "id": job.id,
                "name": job.name,
                "client_company_id": job.client_company_id, # Consider joining to get company name
                "workplace_id": job.workplace_id
            } for job in jobs
        ]

    def get_all_active_jobs(self) -> List[dict]:
        """
        Retrieves all active jobs for Hands on Labor and formats them for the client.
        Since there's only one company, all managers can see all jobs.
        """
        jobs = self.service.get_all_active_jobs()
        return [
            {
                "id": job.id,
                "name": job.name,
                "client_company_id": job.client_company_id,
                "venue_name": job.venue_name,
                "venue_address": job.venue_address,
                "venue_contact_info": job.venue_contact_info,
                "description": job.description,
                "created_by": job.created_by,
                "created_at": job.created_at.isoformat() if job.created_at else None,
                "is_active": job.is_active,
                "estimated_start_date": job.estimated_start_date.isoformat() if job.estimated_start_date else None,
                "estimated_end_date": job.estimated_end_date.isoformat() if job.estimated_end_date else None
            } for job in jobs
        ]

    def get_jobs_by_client_company_id(self, client_company_id: int):
        """
        Retrieves all jobs for a specific client company.

        Parameters:
            client_company_id (int): The client company ID.

        Returns:
            List[Job]: List of jobs for the client company.
        """
        return self.repository.get_jobs_by_client_company_id(client_company_id)
