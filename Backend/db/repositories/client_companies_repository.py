from sqlalchemy.orm import Session
from db.models import ClientCompany
from db.repositories.base_repository import BaseRepository


class ClientCompaniesRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, ClientCompany)

    # Add any client company specific query methods here if needed in the future
    # For example, find_by_name, etc.
    # BaseRepository.get_all_entities() will be used for listing all.
