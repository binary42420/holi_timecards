from main import initialize_database_and_session
from handlers.enhanced_schedule_handlers import handle_get_schedule_data
from db.controllers.users_controller import UsersController
from user_session import UserSession
from datetime import datetime, timedelta

def test_schedule_handler_direct():
    """Test the schedule handler directly"""
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        
        print("🔍 Testing Schedule Handler Directly...")
        
        # Get manager user
        users_controller = UsersController(db)
        manager_exists, is_manager = users_controller.check_user_existence_and_manager_status("manager", "password")
        
        if not manager_exists:
            print("❌ Manager user not found")
            return
            
        manager_id = users_controller.get_user_id_by_username_and_password("manager", "password")
        print(f"✅ Manager user ID: {manager_id}")
        
        # Create user session
        user_session = UserSession(manager_id, True)
        
        # Prepare test data
        today = datetime.now()
        start_date = today - timedelta(days=3)
        end_date = today + timedelta(days=3)
        
        test_data = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'view_type': 'week',
            'include_workers': True,
            'include_jobs': True,
            'include_clients': True,
            'filters': {}
        }
        
        print(f"📤 Calling schedule handler with data:")
        print(f"   Start: {start_date.isoformat()}")
        print(f"   End: {end_date.isoformat()}")
        
        # Call the handler directly
        try:
            result = handle_get_schedule_data(test_data, user_session)
            
            print(f"📥 Handler result:")
            print(f"   Success: {result.get('success')}")
            print(f"   Request ID: {result.get('request_id')}")
            
            if result.get('success'):
                data = result.get('data', {})
                shifts = data.get('shifts', [])
                workers = data.get('workers', [])
                jobs = data.get('jobs', [])
                clients = data.get('clients', [])
                
                print(f"✅ Schedule data retrieved successfully!")
                print(f"   📊 Shifts: {len(shifts)}")
                print(f"   👥 Workers: {len(workers)}")
                print(f"   💼 Jobs: {len(jobs)}")
                print(f"   🏢 Clients: {len(clients)}")
                
                # Show some sample data
                if shifts:
                    print(f"\n📊 Sample shifts:")
                    for i, shift in enumerate(shifts[:3]):
                        print(f"      Shift {i+1}: ID={shift.get('id')}, Job ID={shift.get('job_id')}")
                        print(f"                 Start: {shift.get('shift_start_datetime')}")
                        print(f"                 Job Name: {shift.get('job_name')}")
                
                if jobs:
                    print(f"\n💼 Sample jobs:")
                    for i, job in enumerate(jobs[:3]):
                        print(f"      Job {i+1}: ID={job.get('id')}, Name={job.get('jobName')}")
                        print(f"               Location: {job.get('location')}")
                        print(f"               Client: {job.get('client_company_name')}")
                
            else:
                print(f"❌ Handler failed: {result.get('error')}")
                
        except Exception as e:
            print(f"❌ Exception calling handler: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_schedule_handler_direct()
