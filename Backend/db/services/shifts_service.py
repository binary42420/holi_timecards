from sqlalchemy import Date
from typing import List
from db.models import Shift
from typing import List
from db.models import Shift
from db.repositories.shifts_repository import ShiftsRepository
from db.services.base_service import BaseService


class ShiftsService(BaseService):
    """
    Service class for handling complexes operations.
    """

    def __init__(self, repository: ShiftsRepository):
        """
        Initializes the ShiftsService with a shift repository.

        Parameters:
            repository: An instance of ShiftsRepository.
        """
        super().__init__(repository)

    def get_shifts_by_job_id(self, job_id: int) -> List[Shift]:
        """
        Retrieves all shifts for a given job ID.
        """
        return self.repository.get_shifts_by_job_id(job_id)

    def get_shift_date_by_shift_id(self, shift_id: str) -> Date:
        """
        Retrieves the shift's date by its ID.

        Parameters:
            shift_id (str): ID of the shift to retrieve the given_date for.

        Returns:
             The date of the shift.

        Raises:
            NoResultFound: If the shift with the specified ID is not found.
        """
        shift = self.repository.get_entity(shift_id)
        return shift.shiftDate

    def get_shift_id_by_day_and_part_and_workplace(self, day: str, part: str, workplace: int):
        shift = self.repository.get_shift_by_day_and_part_and_workplace(day, part, workplace)
        if shift:
            print(shift)
            return shift.id
        return None
