from sqlalchemy.orm import Session
from db.models import ClientCompany
from db.repositories.client_companies_repository import ClientCompaniesRepository
from db.services.client_companies_service import ClientCompaniesService
from db.controllers.base_controller import BaseController
from typing import List


class ClientCompaniesController(BaseController):
    def __init__(self, db: Session):
        self.repository = ClientCompaniesRepository(db)
        self.service = ClientCompaniesService(self.repository)
        super().__init__(self.repository, self.service)

    def get_all_client_companies(self) -> List[dict]:
        """
        Retrieves all client companies and formats them for client-side display.
        """
        companies = self.service.get_all_client_companies()
        return [{"id": company.id, "name": company.name} for company in companies]

    # Add other methods like create_client_company if needed in the future
    # For now, we assume client companies are pre-populated or managed elsewhere.
