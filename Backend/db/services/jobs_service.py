from db.repositories.jobs_repository import JobsRepository
from db.services.base_service import BaseService
from db.models import Job
from typing import List


class JobsService(BaseService):
    def __init__(self, repository: JobsRepository):
        super().__init__(repository)

    def create_job(self, job_data: dict) -> Job:
        """
        Creates a new job.
        """
        return self.repository.create_entity(job_data)

    def get_jobs_by_workplace_id(self, workplace_id: int) -> List[Job]:
        """
        DEPRECATED: Use get_all_active_jobs() instead.
        For Hands on Labor single company, returns all active jobs.
        """
        # Ignore workplace_id since all jobs are for Hands on Labor
        return self.get_all_active_jobs()

    def get_all_active_jobs(self) -> List[Job]:
        """
        Retrieves all active jobs for Hands on Labor.
        """
        return self.repository.get_all_active_jobs()
