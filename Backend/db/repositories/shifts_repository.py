from datetime import date
from typing import List
from sqlalchemy.orm import Session
from db.models import Shift
from db.repositories.base_repository import BaseRepository
from db.repositories.shiftWorkers_repository import ShiftWorkersRepository


class ShiftsRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db, Shift)

    def get_shifts_by_job_id(self, job_id: int) -> List[Shift]:
        """
        Retrieves all shifts associated with a specific job ID, ordered by date and part.
        """
        try:
            # Try to order by new datetime fields first, fallback to legacy fields
            # Use COALESCE to handle NULL values instead of NULLS LAST (MariaDB compatibility)
            from sqlalchemy import func
            return self.db.query(Shift).filter(Shift.job_id == job_id).order_by(
                func.coalesce(Shift.shift_start_datetime, '9999-12-31 23:59:59').asc(),
                Shift.shiftDate,
                Shift.shiftPart
            ).all()
        except Exception as e:
            # Fallback to legacy fields only if datetime fields don't exist
            print(f"Using legacy shift fields due to: {e}")
            return self.db.query(Shift).filter(Shift.job_id == job_id).order_by(Shift.shiftDate, Shift.shiftPart).all()

    def get_shift_by_day_and_part_and_workplace(self, day: str, part: str, workplace: int):
        return self.db.query(Shift).filter(Shift.shiftDay == day, Shift.shiftPart == part,
                                           Shift.workPlaceID == workplace).first()

    def get_all_shifts_since_date(self, given_date: date):
        """
        Retrieves all shifts of a worker since a given date.

        Parameters:
            given_date (date): Date to retrieve the shifts since.

        Returns:
            List of shifts of the worker since the given date.
        """
        return self.db.query(Shift).filter(
            Shift.shiftDate >= given_date
        ).all()

    def get_all_shifts_since_date_for_given_worker(self, date: date, worker_id: str) -> List[Shift]:
        """
        Retrieves all shifts of a worker since a given date.
        Args:
            date (date): Date to retrieve the shifts since.
            worker_id (str): ID of the worker to retrieve shifts for.

        Returns: List of shifts of the worker since the given date.
        """
        # Reuse the get_all_shifts_since_date function
        shifts = self.get_all_shifts_since_date(date)

        # Get the shift workers repository
        shift_workers_repository = ShiftWorkersRepository(self.db)

        # Filter shifts based on the given worker ID
        shifts_for_worker = [shift for shift in shifts if
                             shift_workers_repository.is_shift_assigned_to_worker(shift.id, worker_id)]
        return shifts_for_worker

    def get_all_shifts_since_date_for_given_workplace(self, given_date: date, workplace_id: str) -> List[Shift]:
        """
        Retrieves all shifts of a workplace since a given date.
        Args:
            given_date (date): Date to retrieve the shifts since.
            workplace_id (str): ID of the workplace to retrieve shifts for.

        Returns: List of shifts of the workplace since the given date.
        """
        # Reuse the get_all_shifts_since_date function
        shifts = self.get_all_shifts_since_date(given_date)

        # Filter shifts based on the given workplace ID
        shifts_for_workplace = [shift for shift in shifts if shift.workPlaceID == workplace_id]
        return shifts_for_workplace

    def get_all_shifts_between_dates_for_given_workplace(self, start_date, end_date, workplace_id):
        """
        Retrieves all shifts of a workplace between two given dates.
        Args:
            start_date (date): Start date to retrieve the shifts from.
            end_date (date): End date to retrieve the shifts until.
            workplace_id (str): ID of the workplace to retrieve shifts for.

        Returns: List of shifts of the workplace between the given dates.
        """
        return self.db.query(Shift).filter(
            Shift.shiftDate >= start_date,
            Shift.shiftDate <= end_date,
            Shift.workPlaceID == workplace_id
        ).all()

    def get_all_shifts_between_dates_for_given_worker(self, worker_id, start_date, end_date):
        """
        Retrieves all shifts of a worker between two given dates.
        Args:
            worker_id (str): ID of the worker to retrieve shifts for.
            start_date (date): Start date to retrieve the shifts from.
            end_date (date): End date to retrieve the shifts until.

        Returns: List of shifts of the worker between the given dates.
        """
        # Get the shift workers repository
        shift_workers_repository = ShiftWorkersRepository(self.db)

        # Get all shifts between the given dates
        shifts = self.db.query(Shift).filter(
            Shift.shiftDate >= start_date,
            Shift.shiftDate <= end_date
        ).all()

        # Filter shifts based on the given worker ID
        shifts_for_worker = [shift for shift in shifts if
                             shift_workers_repository.is_shift_assigned_to_worker(shift.id, worker_id)]
        return shifts_for_worker

    def get_shift_by_day_and_part(self, workplace_id, shift_date, shift_part):
        """
        Retrieves the shift by day and part.

        Parameters:
            workplace_id (int): ID of the workplace.
            shift_date (date): Date of the shift.
            shift_part (str): Part of the shift.

        Returns:
            Shift: The shift by day and part.
        """
        return self.db.query(Shift).filter(Shift.workPlaceID == workplace_id, Shift.shiftDate == shift_date,
                                           Shift.shiftPart == shift_part).first()

    def get_shift_by_date_and_part(self, shift_date, shift_part):
        """
        Retrieves the shift by date and part for Hands on Labor (single company).
        Since there's only one company, we don't need workplace filtering.

        Parameters:
            shift_date (date): Date of the shift.
            shift_part (str): Part of the shift.

        Returns:
            Shift: The shift by date and part.
        """
        return self.db.query(Shift).filter(Shift.shiftDate == shift_date,
                                           Shift.shiftPart == shift_part).first()
