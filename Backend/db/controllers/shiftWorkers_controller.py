from __future__ import annotations
from typing import Type
from sqlalchemy.orm import Session
from db.controllers.base_controller import BaseController
from db.repositories.shiftWorkers_repository import ShiftWorkersRepository
from db.services.shiftWorkers_service import ShiftWorkersService
from db.models import EmployeeType, ShiftWorker


class ShiftWorkersController(BaseController):
    """
    ShiftWorkersController Class

    Controller class for managing ShiftWorker entities.
    """

    def __init__(self, db: Session):
        """
        Initializes the ShiftWorkersController with a database session.

        Parameters:
            db (Session): SQLAlchemy Session for database interactions.
        """
        self.repository = ShiftWorkersRepository(db)
        self.service = ShiftWorkersService(self.repository)
        super().__init__(self.repository, self.service)

    def get_entity_shift_worker(self, shift_id: str, user_id: str):
        """
        Retrieves a shift worker by shift ID and user ID.

        Args:
            shift_id (str): ID of the shift
            user_id (str): ID of the worker

        Returns: An entity of ShiftWorker

        """
        return self.repository.get_entity_shift_worker(shift_id, user_id)

    def delete_entity_shift_worker(self, shift_id: str, user_id: str):
        """
        Deletes a shift worker by shift ID and user ID.

        Args:
            shift_id (str): ID of the shift
            user_id (str): ID of the worker

        """
        self.repository.delete_entity_shift_worker(shift_id, user_id)

    def get_worker_shifts_by_worker_id(self, worker_id: str):
        """
        Retrieves all shifts for a worker by worker ID.
        Args:
            worker_id (str): ID of the worker to retrieve shifts for.

        Returns:
            List[ShiftWorker]: A list of all shifts for the worker.
        """
        return self.repository.get_worker_shifts_by_worker_id(worker_id)

    def get_shift_workers_by_shift_id(self, shift_id: str):
        """
        Retrieves all workers for a shift by shift ID.
        Args:
            shift_id (str): ID of the shift to retrieve workers for.

        Returns:
            List[ShiftWorker]: A list of all workers for the shift.
        """
        return self.repository.get_shift_workers_by_shift_id(shift_id)

    def is_shift_assigned_to_worker(self, shift_id: str, worker_id: str):
        """
        Checks if a shift is assigned to a worker.
        Args:
            shift_id (str): ID of the shift
            worker_id (str): ID of the worker

        Returns:
            bool: True if the shift is assigned to the worker, False otherwise.
        """
        return self.repository.is_shift_assigned_to_worker(shift_id, worker_id)

    def convert_shift_workers_by_shift_id_to_client(self, shift_id: str) -> list[str]:
        """
        Retrieves all workers for a shift by shift ID.
        Args:
            shift_id (str): ID of the shift to retrieve workers for.

        Returns:
            List[str]: A list of all workers for the shift.
        """
        return self.repository.convert_shift_workers_by_shift_id_to_client(shift_id)

    def delete_entity_by_composite_key(self, shift_id: int, user_id: int, role_assigned_str: str):
        """
        Deletes a ShiftWorker entity by its composite primary key.
        Converts role_assigned_str to EmployeeType enum.
        """
        try:
            role_assigned = EmployeeType(role_assigned_str)
            return self.repository.delete_entity_by_composite_key(shift_id, user_id, role_assigned)
        except ValueError:
            # Handle invalid role_assigned_str
            print(f"Invalid role assigned string: {role_assigned_str}")
            return None

    def submit_times_for_worker_on_shift(self, shift_id: int, user_id: int, role_assigned_str: str, clock_in_time_str: str | None, clock_out_time_str: str | None) -> Type[ShiftWorker] | None:
        """
        Submits clock-in and clock-out times for a specific worker on a shift.

        Args:
            shift_id (int): ID of the shift.
            user_id (int): ID of the worker.
            role_assigned_str (str): The role assigned to the worker for this shift (string representation of EmployeeType).
            clock_in_time_str (str | None): The clock-in time in ISO 8601 format (e.g., "YYYY-MM-DDTHH:MM:SS").
            clock_out_time_str (str | None): The clock-out time in ISO 8601 format.

        Returns:
            ShiftWorker: The updated ShiftWorker entity if found, None otherwise.
        """
        role_assigned = EmployeeType(role_assigned_str)
        return self.service.record_shift_times(shift_id, user_id, role_assigned, clock_in_time_str, clock_out_time_str)

    def get_shift_worker(self, shift_id: int, user_id: int, role_assigned_str: str):
        """
        Get a specific shift worker record.

        Args:
            shift_id (int): The shift ID
            user_id (int): The user ID
            role_assigned_str (str): The role assigned as string

        Returns:
            ShiftWorker: The shift worker record if found, None otherwise
        """
        from ..models import EmployeeType
        role_assigned = EmployeeType(role_assigned_str)
        return self.repository.get_shift_worker(shift_id, user_id, role_assigned)

    def update_shift_worker_times(self, shift_id: int, user_id: int, role_assigned_str: str, update_data: dict):
        """
        Update timesheet data for a shift worker.

        Args:
            shift_id (int): The shift ID
            user_id (int): The user ID
            role_assigned_str (str): The role assigned as string
            update_data (dict): Dictionary of fields to update

        Returns:
            ShiftWorker: The updated shift worker record
        """
        from ..models import EmployeeType
        role_assigned = EmployeeType(role_assigned_str)
        shift_worker = self.repository.get_shift_worker(shift_id, user_id, role_assigned)

        if shift_worker:
            for key, value in update_data.items():
                if hasattr(shift_worker, key):
                    setattr(shift_worker, key, value)

            self.repository.db.commit()
            self.repository.db.refresh(shift_worker)
            return shift_worker
        return None

    def submit_timesheet_for_worker(self, shift_id: int, worker_id: int, submitted_by_id: int) -> bool:
        """
        Mark timesheet as submitted for a worker.

        Args:
            shift_id (int): The shift ID
            worker_id (int): The worker's user ID
            submitted_by_id (int): ID of user submitting (crew chief or manager)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from datetime import datetime

            # Get all shift worker records for this worker on this shift
            shift_workers = self.repository.get_workers_for_shift_and_user(shift_id, worker_id)

            for sw in shift_workers:
                sw.times_submitted_at = datetime.now()
                sw.times_submitted_by = submitted_by_id
                # Recalculate hours when submitting
                sw.calculate_total_hours()

            self.repository.db.commit()
            return True
        except Exception as e:
            print(f"Error submitting timesheet: {e}")
            self.repository.db.rollback()
            return False

    def approve_timesheet_for_worker(self, shift_id: int, worker_id: int, approved_by_id: int) -> bool:
        """
        Approve timesheet for a worker.

        Args:
            shift_id (int): The shift ID
            worker_id (int): The worker's user ID
            approved_by_id (int): ID of manager approving

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            from datetime import datetime

            # Get all shift worker records for this worker on this shift
            shift_workers = self.repository.get_workers_for_shift_and_user(shift_id, worker_id)

            for sw in shift_workers:
                sw.is_approved = True
                sw.approved_at = datetime.now()
                sw.approved_by = approved_by_id

            self.repository.db.commit()
            return True
        except Exception as e:
            print(f"Error approving timesheet: {e}")
            self.repository.db.rollback()
            return False

    def get_employee_timesheet_history(self, employee_id: int, start_date: str = None, end_date: str = None) -> list:
        """
        Get timesheet history for an employee.

        Args:
            employee_id (int): The employee's user ID
            start_date (str): Optional start date filter (YYYY-MM-DD)
            end_date (str): Optional end date filter (YYYY-MM-DD)

        Returns:
            list: List of timesheet records with shift details
        """
        return self.service.get_employee_timesheet_history(employee_id, start_date, end_date)

    def get_submitted_timesheets_for_workplace(self, workplace_id: str) -> list:
        """
        Get all submitted timesheets for a workplace.

        Args:
            workplace_id (str): The workplace ID

        Returns:
            list: List of submitted shift worker records
        """
        try:
            # Get all shift workers with submitted timesheets for this workplace
            from sqlalchemy import and_
            from ..models import ShiftWorker, Shift, User

            query = self.repository.db.query(ShiftWorker).join(
                Shift, ShiftWorker.shiftID == Shift.id
            ).join(
                User, ShiftWorker.userID == User.id
            ).filter(
                and_(
                    User.workplaceID == workplace_id,
                    ShiftWorker.times_submitted_at.isnot(None)
                )
            ).order_by(ShiftWorker.times_submitted_at.desc())

            return query.all()
        except Exception as e:
            print(f"Error getting submitted timesheets for workplace: {e}")
            return []

    def reject_timesheet_for_worker(self, shift_id: int, worker_id: int, rejected_by_id: int) -> bool:
        """
        Reject timesheet for a worker (reset submission status).

        Args:
            shift_id (int): The shift ID
            worker_id (int): The worker's user ID
            rejected_by_id (int): ID of manager rejecting

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all shift worker records for this worker on this shift
            shift_workers = self.repository.get_workers_for_shift_and_user(shift_id, worker_id)

            for sw in shift_workers:
                # Reset submission status
                sw.times_submitted_at = None
                sw.times_submitted_by = None
                sw.is_approved = False
                sw.approved_at = None
                sw.approved_by = None

            self.repository.db.commit()
            return True
        except Exception as e:
            print(f"Error rejecting timesheet: {e}")
            self.repository.db.rollback()
            return False

    # === TIMECARD MANAGEMENT METHODS ===

    def get_workers_by_shift_id(self, shift_id: int):
        """
        Get all workers assigned to a specific shift for timecard management.
        """
        return self.repository.get_shift_workers_by_shift_id(str(shift_id))

    def get_shift_worker_for_timecard(self, shift_id: int, user_id: int):
        """
        Get a specific shift worker record for timecard (any role).
        """
        # Get all records for this user on this shift (they might have multiple roles)
        workers = self.repository.get_workers_for_shift_and_user(shift_id, user_id)
        return workers[0] if workers else None

    def update_clock_time(self, shift_id: int, user_id: int, action: str, time, manager_id: int) -> bool:
        """
        Update clock in/out time for a worker.
        """
        try:
            from datetime import datetime

            # Get the shift worker record
            shift_worker = self.get_shift_worker_for_timecard(shift_id, user_id)
            if not shift_worker:
                return False

            # Update status and time based on action
            if action == "clock_in":
                # Find the next available clock_in slot
                if not shift_worker.clock_in_time_1:
                    shift_worker.clock_in_time_1 = time
                elif not shift_worker.clock_in_time_2:
                    shift_worker.clock_in_time_2 = time
                elif not shift_worker.clock_in_time_3:
                    shift_worker.clock_in_time_3 = time
                else:
                    return False  # All slots filled

                shift_worker.current_status = 'clocked_in'

            elif action == "clock_out":
                # Find the corresponding clock_out slot
                if shift_worker.clock_in_time_1 and not shift_worker.clock_out_time_1:
                    shift_worker.clock_out_time_1 = time
                elif shift_worker.clock_in_time_2 and not shift_worker.clock_out_time_2:
                    shift_worker.clock_out_time_2 = time
                elif shift_worker.clock_in_time_3 and not shift_worker.clock_out_time_3:
                    shift_worker.clock_out_time_3 = time
                else:
                    return False  # No matching clock_in or all slots filled

                shift_worker.current_status = 'clocked_out'

            shift_worker.last_action_time = time

            # Recalculate total hours
            shift_worker.calculate_total_hours()

            self.repository.db.commit()
            return True

        except Exception as e:
            print(f"Error updating clock time: {e}")
            self.repository.db.rollback()
            return False

    def mark_worker_absent(self, shift_id: int, user_id: int, manager_id: int) -> bool:
        """
        Mark a worker as absent for a shift.
        """
        try:
            from datetime import datetime

            shift_worker = self.get_shift_worker_for_timecard(shift_id, user_id)
            if not shift_worker:
                return False

            shift_worker.is_absent = True
            shift_worker.marked_absent_at = datetime.now()
            shift_worker.marked_absent_by = manager_id
            shift_worker.current_status = 'absent'

            self.repository.db.commit()
            return True

        except Exception as e:
            print(f"Error marking worker absent: {e}")
            self.repository.db.rollback()
            return False

    def update_worker_notes(self, shift_id: int, user_id: int, notes: str) -> bool:
        """
        Update notes for a worker on a shift.
        """
        try:
            shift_worker = self.get_shift_worker_for_timecard(shift_id, user_id)
            if not shift_worker:
                return False

            shift_worker.shift_notes = notes

            self.repository.db.commit()
            return True

        except Exception as e:
            print(f"Error updating worker notes: {e}")
            self.repository.db.rollback()
            return False

    def clock_out_all_workers(self, shift_id: int, time, manager_id: int) -> list:
        """
        Clock out all workers still clocked in for a shift.
        """
        try:
            workers = self.get_workers_by_shift_id(shift_id)
            clocked_out_workers = []

            for worker in workers:
                current_status = getattr(worker, 'current_status', 'not_started')
                if current_status == 'clocked_in':
                    if self.update_clock_time(shift_id, worker.userID, 'clock_out', time, manager_id):
                        clocked_out_workers.append({
                            'user_id': worker.userID,
                            'clocked_out_at': time.isoformat()
                        })

            return clocked_out_workers

        except Exception as e:
            print(f"Error clocking out all workers: {e}")
            return []

    def generate_shift_timesheet(self, shift_id: int) -> dict:
        """
        Generate a draft timesheet for a shift.
        """
        try:
            from ..controllers.users_controller import UsersController
            from ..controllers.shifts_controller import ShiftsController

            workers = self.get_workers_by_shift_id(shift_id)
            users_controller = UsersController(self.repository.db)
            shifts_controller = ShiftsController(self.repository.db)

            # Get shift details
            shift = shifts_controller.get_shift_by_id(shift_id)

            timesheet_data = {
                'shift_id': shift_id,
                'shift_info': {
                    'shift_start_datetime': shift.shift_start_datetime.isoformat() if shift.shift_start_datetime else None,
                    'shift_end_datetime': shift.shift_end_datetime.isoformat() if shift.shift_end_datetime else None,
                    'shift_description': getattr(shift, 'shift_description', ''),
                },
                'workers': [],
                'summary': {
                    'total_workers': len(workers),
                    'total_regular_hours': 0,
                    'total_overtime_hours': 0,
                    'total_cost': 0  # Would need hourly rates to calculate
                }
            }

            for worker in workers:
                user = users_controller.get_entity(worker.userID)

                worker_data = {
                    'user_id': worker.userID,
                    'user_name': user.name if user else 'Unknown',
                    'role_assigned': worker.role_assigned.value if worker.role_assigned else None,
                    'time_pairs': worker.get_time_pairs(),
                    'total_hours_worked': worker.total_hours_worked or 0,
                    'overtime_hours': worker.overtime_hours or 0,
                    'is_absent': getattr(worker, 'is_absent', False),
                    'shift_notes': getattr(worker, 'shift_notes', ''),
                    'current_status': getattr(worker, 'current_status', 'not_started')
                }

                timesheet_data['workers'].append(worker_data)
                timesheet_data['summary']['total_regular_hours'] += (worker.total_hours_worked or 0)
                timesheet_data['summary']['total_overtime_hours'] += (worker.overtime_hours or 0)

            return timesheet_data

        except Exception as e:
            print(f"Error generating shift timesheet: {e}")
            return {}

    def get_shifts_for_user(self, user_id: int):
        """
        Get all shift assignments for a specific user.

        Args:
            user_id (int): The user ID

        Returns:
            list: List of ShiftWorker records for the user
        """
        try:
            from ..models import ShiftWorker

            query = self.repository.db.query(ShiftWorker).filter(
                ShiftWorker.userID == user_id
            ).order_by(ShiftWorker.shiftID.desc())

            return query.all()
        except Exception as e:
            print(f"Error getting shifts for user: {e}")
            return []

    def get_crew_chief_shifts_for_user(self, user_id: int):
        """
        Get shifts where the user is assigned as crew chief.

        Args:
            user_id (int): The user ID

        Returns:
            list: List of ShiftWorker records where user is crew chief
        """
        try:
            from ..models import ShiftWorker, EmployeeType

            query = self.repository.db.query(ShiftWorker).filter(
                ShiftWorker.userID == user_id,
                ShiftWorker.role_assigned == EmployeeType.CREW_CHIEF
            ).order_by(ShiftWorker.shiftID.desc())

            return query.all()
        except Exception as e:
            print(f"Error getting crew chief shifts for user: {e}")
            return []

    def get_workers_for_shift(self, shift_id: int):
        """
        Get all workers assigned to a specific shift.

        Args:
            shift_id (int): The shift ID

        Returns:
            list: List of ShiftWorker records for the shift
        """
        try:
            from ..models import ShiftWorker

            query = self.repository.db.query(ShiftWorker).filter(
                ShiftWorker.shiftID == shift_id
            )

            return query.all()
        except Exception as e:
            print(f"Error getting workers for shift: {e}")
            return []
