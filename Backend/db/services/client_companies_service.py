from db.repositories.client_companies_repository import ClientCompaniesRepository
from db.services.base_service import BaseService
from db.models import ClientCompany
from typing import List


class ClientCompaniesService(BaseService):
    def __init__(self, repository: ClientCompaniesRepository):
        super().__init__(repository)

    def get_all_client_companies(self) -> List[ClientCompany]:
        """
        Retrieves all client companies.
        """
        return self.repository.get_all_entities()
