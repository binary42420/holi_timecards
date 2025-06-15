from main import initialize_database_and_session
from db.controllers.shifts_controller import ShiftsController
from db.controllers.jobs_controller import JobsController
from db.controllers.users_controller import UsersController
from db.controllers.client_companies_controller import ClientCompaniesController
from datetime import datetime, timedelta

def test_database_content():
    """Test database content to see what data exists"""
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        
        # Initialize controllers
        shifts_controller = ShiftsController(db)
        jobs_controller = JobsController(db)
        users_controller = UsersController(db)
        client_companies_controller = ClientCompaniesController(db)
        
        print("🔍 Checking database content...")
        
        # Check users
        try:
            print("\n👥 USERS:")
            # Try to get some users by checking login
            admin_exists, is_manager = users_controller.check_user_existence_and_manager_status("manager", "password")
            print(f"   Manager user exists: {admin_exists}, is_manager: {is_manager}")
            
            if admin_exists:
                user_id = users_controller.get_user_id_by_username_and_password("manager", "password")
                print(f"   Manager user ID: {user_id}")
        except Exception as e:
            print(f"   ❌ Error checking users: {e}")
        
        # Check client companies
        try:
            print("\n🏢 CLIENT COMPANIES:")
            # This might not work if there's no get_all method
            print("   Checking for client companies...")
        except Exception as e:
            print(f"   ❌ Error checking client companies: {e}")
        
        # Check jobs
        try:
            print("\n💼 JOBS:")
            print("   Checking for jobs...")
            # Try to get jobs for the manager user
            if admin_exists:
                user_id = users_controller.get_user_id_by_username_and_password("manager", "password")
                # This might not work depending on the method signature
        except Exception as e:
            print(f"   ❌ Error checking jobs: {e}")
        
        # Check shifts
        try:
            print("\n📅 SHIFTS:")
            print("   Checking for shifts...")
            
            # Try to get shifts for a date range
            today = datetime.now().date()
            start_date = today - timedelta(days=7)
            end_date = today + timedelta(days=7)
            
            shifts = shifts_controller.get_shifts_by_date_range(start_date, end_date, None)
            print(f"   Found {len(shifts)} shifts in the last/next week")
            
            for shift in shifts[:5]:  # Show first 5 shifts
                print(f"      - Shift ID: {shift.id}, Job ID: {shift.job_id}")
                if hasattr(shift, 'shift_start_datetime') and shift.shift_start_datetime:
                    print(f"        Start: {shift.shift_start_datetime}")
                elif hasattr(shift, 'shiftDate') and shift.shiftDate:
                    print(f"        Date: {shift.shiftDate}, Part: {shift.shiftPart}")
                    
        except Exception as e:
            print(f"   ❌ Error checking shifts: {e}")
            
        print("\n✅ Database content check completed")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

if __name__ == "__main__":
    test_database_content()
