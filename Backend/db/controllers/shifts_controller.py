from datetime import date, datetime
from main import get_db_session
from sqlalchemy import Date
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session
from typing import List
from typing import List
from db.controllers.base_controller import BaseController
from db.models import Shift
from db.repositories.shifts_repository import ShiftsRepository
from db.services.shifts_service import ShiftsService
from db.controllers.shiftWorkers_controller import ShiftWorkersController


class ShiftsController(BaseController):
    """
    ShiftsController Class

    Controller class for managing shift entities.
    """

    def __init__(self, db: Session):
        """
        Initializes the ShiftsController with a database session.

        Parameters:
            db (Session): SQLAlchemy Session for database interactions.
        """
        self.repository = ShiftsRepository(db)
        self.service = ShiftsService(self.repository)
        super().__init__(self.repository, self.service)

    def get_shifts_by_job_id(self, job_id: int, is_manager: bool = True) -> List[dict]:
        """
        Retrieves all shifts for a given job ID and formats them for the client.
        """
        shifts = self.service.get_shifts_by_job_id(job_id)
        # Ensure convert_shifts_for_client also includes client_po_number and required_employee_counts
        return convert_shifts_for_client(shifts, self.repository.db, is_manager)

    def get_shift_by_id(self, shift_id: int):
        """
        Retrieves a shift by its ID.

        Args:
            shift_id (int): The shift ID

        Returns:
            Shift: The shift entity if found, None otherwise
        """
        return self.get_entity(shift_id)

    def get_shift_date_by_shift_id(self, shift_id: str) -> Date:
        """
        Retrieves the shift's date by its ID.

        Parameters:
            shift_id (str): ID of the shift to retrieve the date for.

        Returns:
             The date of the shift.

        Raises:
            NoResultFound: If the shift with the specified ID is not found.
        """
        return self.service.get_shift_date_by_shift_id(shift_id)

    def get_all_shifts_of_worker_since_date(self, date: date):
        """
        Retrieves all shifts of a worker since a given date.

        Parameters:
            date (date): Date to retrieve the shifts since.

        Returns:
            List of shifts of the worker since the given date.
        """
        try:
            shifts = self.repository.get_all_shifts_since_date(date)
            return shifts
        except NoResultFound:
            return None  # It's okay to assume that the worker has no shifts since the given date.

    def get_all_shifts_since_date_for_given_worker(self, date: date, worker_id: str):
        """
        Retrieves all shifts of a worker since a given date.

        Args:
            date (date): Date to retrieve the shifts since.
            worker_id (str): ID of the worker to retrieve shifts for.

        Returns: List of shifts of the worker since the given date.
        """
        return self.repository.get_all_shifts_since_date_for_given_worker(date, worker_id)

    def get_future_shifts_for_user(self, user_id: str):
        """
        Retrieves all future shifts for the specified user.

        Parameters:
            user_id (str): ID of the user to retrieve shifts for.

        Returns:
            List of future shifts for the specified user.
        """
        # This method is just a wrapper around the get_all_shifts_since_date_for_given_worker method
        return self.get_all_shifts_since_date_for_given_worker(datetime.now(), user_id)

    def get_all_shifts_since_date_for_given_workplace(self, given_date: date, workplace_id: str):
        """
        Retrieves all shifts of a workplace since a given date.

        Args:
            given_date (date): Date to retrieve the shifts since.
            workplace_id (str): ID of the workplace to retrieve shifts for.

        Returns: List of shifts of the workplace since the given date.
        """
        return self.repository.get_all_shifts_since_date_for_given_workplace(given_date, workplace_id)

    def get_all_shifts_between_dates_for_given_workplace(self, start_date: date, end_date: date, workplace_id: str):
        """
        Retrieves all shifts of a workplace between two given dates.

        Args:
            start_date (date): Start date to retrieve the shifts from.
            end_date (date): End date to retrieve the shifts until.
            workplace_id (str): ID of the workplace to retrieve shifts for.

        Returns: List of shifts of the workplace between the given dates.
        """
        return self.repository.get_all_shifts_between_dates_for_given_workplace(start_date, end_date, workplace_id)

    def get_future_shifts_for_workplace(self, workplace_id: str):
        """
        Retrieves all future shifts for the specified workplace.

        Parameters:
            workplace_id (str): ID of the workplace to retrieve shifts for.

        Returns:
            List of future shifts for the specified workplace.
        """
        # This method is just a wrapper around the get_all_shifts_since_date_for_given_workplace method
        return self.get_all_shifts_since_date_for_given_workplace(datetime.now(), workplace_id)

    def get_shift_id_by_day_and_part_and_workplace(self, day: str, part: str, workplace: int):
        return self.service.get_shift_id_by_day_and_part_and_workplace(day, part, workplace)

    def get_shifts_by_date_range(self, start_date, end_date, workplace_id=None):
        """
        Get shifts within a date range, optionally filtered by workplace.

        Args:
            start_date: Start date for the range
            end_date: End date for the range
            workplace_id: Optional workplace ID filter

        Returns:
            List of shifts within the date range
        """
        try:
            from sqlalchemy import and_, or_
            from ..models import Shift, Job, User

            query = self.repository.db.query(Shift)

            # Filter by date range - check both new datetime fields and legacy date fields
            date_filter = or_(
                and_(
                    Shift.shift_start_datetime >= start_date,
                    Shift.shift_start_datetime <= end_date
                ),
                and_(
                    Shift.shiftDate >= start_date,
                    Shift.shiftDate <= end_date
                )
            )
            query = query.filter(date_filter)

            # Filter by workplace if specified
            if workplace_id:
                # Join with Job and User to filter by workplace
                query = query.join(Job, Shift.job_id == Job.id, isouter=True)
                query = query.join(User, Job.created_by == User.id, isouter=True)
                query = query.filter(or_(
                    User.id == workplace_id  # For manager's own workplace
                ))

            return query.order_by(Shift.shift_start_datetime.asc(), Shift.shiftDate.asc()).all()

        except Exception as e:
            print(f"Error getting shifts by date range: {e}")
            return []

    def get_all_shifts_between_dates_for_given_worker(self, id, start_date, end_date):
        return self.repository.get_all_shifts_between_dates_for_given_worker(id, start_date, end_date)

    def get_shift_by_day_and_part(self, workplace_id, shift_date, shift_part):
        return self.repository.get_shift_by_day_and_part(workplace_id, shift_date, shift_part)

    def get_shift_by_date_and_part(self, shift_date, shift_part):
        """
        Get a shift by date and part for Hands on Labor (single company).
        Since there's only one company, we don't need workplace_id filtering.
        """
        return self.repository.get_shift_by_date_and_part(shift_date, shift_part)

def convert_shift_for_client(shift: Shift, db, is_manager=True) -> dict:
    """
    Converts a shift to a dictionary format for client-side consumption.
    If the user is a manager, the dictionary will also include the workers assigned to the shift.

    Parameters:
        shift (Shift): The shift to convert.
        db (Session): SQLAlchemy Session for database interactions.
        is_manager (bool): A boolean indicating whether the user is a manager.

    Returns:
        dict: A dictionary representation of the shift.
    """
    with get_db_session() as session:
        shift_workers_controller = ShiftWorkersController(session)

        shifts_for_client = {
            'id': shift.id,
            'job_id': shift.job_id,
            "required_employee_counts": shift.required_employee_counts if shift.required_employee_counts else {},
            "client_po_number": shift.client_po_number if shift.client_po_number else "",
            "shift_description": shift.shift_description if shift.shift_description else "",
            "special_instructions": shift.special_instructions if shift.special_instructions else ""
        }

        # Add new datetime fields if available
        if hasattr(shift, 'shift_start_datetime') and shift.shift_start_datetime:
            shifts_for_client['shift_start_datetime'] = shift.shift_start_datetime.isoformat()
            if hasattr(shift, 'shift_end_datetime') and shift.shift_end_datetime:
                shifts_for_client['shift_end_datetime'] = shift.shift_end_datetime.isoformat()

        # Add legacy fields for backward compatibility
        if hasattr(shift, 'shiftDate') and shift.shiftDate:
            shifts_for_client['shiftDate'] = shift.shiftDate.isoformat()
        if hasattr(shift, 'shiftPart') and shift.shiftPart:
            shifts_for_client['shiftPart'] = shift.shiftPart.value

        if is_manager:
            workers = shift_workers_controller.convert_shift_workers_by_shift_id_to_client(shift.id)
            shifts_for_client["workers"] = workers

        return shifts_for_client


def convert_shifts_for_client(shifts: list[Shift], db, is_manager=True) -> list[dict]:
    """
    Converts a list of shifts to a dictionary format for client-side consumption.

    Parameters:
        shifts (List[Shift]): The shifts to convert.
        db (Session): SQLAlchemy Session for database interactions.
        is_manager (bool): A boolean indicating whether the user is a manager.

    Returns:
        List[dict]: A list of dictionary representations of the shifts.
    """
    return [convert_shift_for_client(shift, db, is_manager) for shift in shifts]
