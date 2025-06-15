from main import initialize_database_and_session
from db.controllers.jobs_controller import JobsController
from db.controllers.shifts_controller import ShiftsController
from db.controllers.users_controller import UsersController
from datetime import datetime, timedelta

def test_jobs_and_shifts():
    """Test jobs and shifts data in detail"""
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        
        # Initialize controllers
        jobs_controller = JobsController(db)
        shifts_controller = ShiftsController(db)
        users_controller = UsersController(db)
        
        print("🔍 Detailed Jobs and Shifts Analysis...")
        
        # Get manager user
        try:
            manager_exists, is_manager = users_controller.check_user_existence_and_manager_status("manager", "password")
            if manager_exists:
                manager_id = users_controller.get_user_id_by_username_and_password("manager", "password")
                print(f"✅ Manager user ID: {manager_id}")
            else:
                print("❌ Manager user not found")
                return
        except Exception as e:
            print(f"❌ Error getting manager: {e}")
            return
        
        # Check jobs directly from database
        try:
            from db.models import Job
            jobs = db.query(Job).all()
            print(f"\n💼 JOBS IN DATABASE: {len(jobs)}")
            for job in jobs:
                print(f"   Job ID: {job.id}")
                print(f"   Name: {job.name}")
                print(f"   Description: {job.description}")
                print(f"   Venue: {job.venue_name}")
                print(f"   Client Company ID: {job.client_company_id}")
                print(f"   Created by: {job.created_by}")
                print(f"   Start Date: {job.estimated_start_date}")
                print(f"   End Date: {job.estimated_end_date}")
                print("   ---")
        except Exception as e:
            print(f"❌ Error querying jobs directly: {e}")
        
        # Test jobs controller methods
        try:
            print(f"\n🔧 TESTING JOBS CONTROLLER:")
            
            # Try to get jobs for manager
            try:
                # Check what methods are available
                print(f"   Available methods: {[method for method in dir(jobs_controller) if not method.startswith('_')]}")
                
                # Try different ways to get jobs
                if hasattr(jobs_controller, 'get_all_jobs'):
                    all_jobs = jobs_controller.get_all_jobs()
                    print(f"   get_all_jobs(): {len(all_jobs)} jobs")
                
                if hasattr(jobs_controller, 'get_jobs_for_user'):
                    user_jobs = jobs_controller.get_jobs_for_user(manager_id)
                    print(f"   get_jobs_for_user({manager_id}): {len(user_jobs)} jobs")
                
                if hasattr(jobs_controller, 'get_all_entities'):
                    all_entities = jobs_controller.get_all_entities()
                    print(f"   get_all_entities(): {len(all_entities)} jobs")
                    
            except Exception as e:
                print(f"   ❌ Error testing jobs controller methods: {e}")
                
        except Exception as e:
            print(f"❌ Error with jobs controller: {e}")
        
        # Check shifts
        try:
            from db.models import Shift
            shifts = db.query(Shift).all()
            print(f"\n📅 SHIFTS IN DATABASE: {len(shifts)}")
            for shift in shifts[:5]:  # Show first 5
                print(f"   Shift ID: {shift.id}")
                print(f"   Job ID: {shift.job_id}")
                if hasattr(shift, 'shift_start_datetime'):
                    print(f"   Start: {shift.shift_start_datetime}")
                if hasattr(shift, 'shift_end_datetime'):
                    print(f"   End: {shift.shift_end_datetime}")
                print("   ---")
        except Exception as e:
            print(f"❌ Error querying shifts: {e}")
        
        # Test schedule data retrieval (like the frontend would do)
        try:
            print(f"\n📊 TESTING SCHEDULE DATA RETRIEVAL:")
            today = datetime.now().date()
            start_date = today - timedelta(days=7)
            end_date = today + timedelta(days=7)
            
            shifts = shifts_controller.get_shifts_by_date_range(start_date, end_date, None)
            print(f"   Shifts in date range: {len(shifts)}")
            
            # Get unique job IDs from shifts
            job_ids = list(set([shift.job_id for shift in shifts]))
            print(f"   Unique job IDs in shifts: {job_ids}")
            
            # Try to get jobs for these IDs
            for job_id in job_ids:
                try:
                    job = db.query(Job).filter(Job.id == job_id).first()
                    if job:
                        print(f"   Job {job_id}: {job.name}")
                    else:
                        print(f"   Job {job_id}: NOT FOUND")
                except Exception as e:
                    print(f"   Job {job_id}: Error - {e}")
                    
        except Exception as e:
            print(f"❌ Error testing schedule data retrieval: {e}")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

if __name__ == "__main__":
    test_jobs_and_shifts()
