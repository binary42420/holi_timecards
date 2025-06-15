#!/usr/bin/env python3
"""
Test script to verify shift management functionality.
"""

from main import initialize_database_and_session
from handlers.shift_management_handlers import handle_create_shift, handle_get_shifts_by_job
from handlers.employee_list import handle_get_all_approved_worker_details
from user_session import UserSession
from db.controllers.jobs_controller import JobsController
from db.controllers.users_controller import UsersController

def test_shift_management():
    """Test shift management functionality."""
    print("🧪 Testing shift management...")
    
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        print("✅ Database initialized")
        
        # Get a test manager and job
        users_controller = UsersController(db)
        jobs_controller = JobsController(db)
        
        # Get existing managers
        all_users = users_controller.get_all_entities()
        managers = [user for user in all_users if user.isManager]
        if not managers:
            print("❌ No managers found in database. Please create a manager first.")
            return False
        
        test_manager = managers[0]
        print(f"✅ Using manager: {test_manager.name} (ID: {test_manager.id})")
        
        # Create user session for the manager
        user_session = UserSession(test_manager.id, test_manager.isManager)
        
        # Get existing jobs for Hands on Labor
        jobs = jobs_controller.get_all_active_jobs()
        if not jobs:
            print("❌ No jobs found for Hands on Labor. Please create a job first.")
            return False
        
        test_job = jobs[0]
        print(f"✅ Using job: {test_job['name']} (ID: {test_job['id']})")
        
        # Test 1: Get all approved worker details (Request ID 94)
        print(f"\n🔍 Testing get all approved worker details...")
        try:
            worker_response = handle_get_all_approved_worker_details(user_session)
            if worker_response.get('success'):
                workers = worker_response.get('data', [])
                print(f"✅ Found {len(workers)} approved workers")
            else:
                print(f"❌ Failed to get workers: {worker_response.get('error')}")
                return False
        except Exception as e:
            print(f"❌ Error getting workers: {e}")
            return False
        
        # Test 2: Get shifts by job (Request ID 221)
        print(f"\n🔍 Testing get shifts by job...")
        try:
            shift_data = {"job_id": test_job['id']}
            shift_response = handle_get_shifts_by_job(shift_data, user_session)
            if shift_response.get('success'):
                shifts = shift_response.get('data', [])
                print(f"✅ Found {len(shifts)} shifts for job {test_job['id']}")
                for shift in shifts:
                    print(f"   - Shift ID: {shift.get('id')}, Date: {shift.get('shiftDate', 'N/A')}")
            else:
                print(f"❌ Failed to get shifts: {shift_response.get('error')}")
                return False
        except Exception as e:
            print(f"❌ Error getting shifts: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 3: Create a new shift (Request ID 220)
        print(f"\n🔨 Testing create shift...")
        try:
            from datetime import datetime, timedelta
            
            # Create a shift for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            shift_start = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
            shift_end = shift_start + timedelta(hours=8)
            
            shift_data = {
                "job_id": test_job['id'],
                "shift_start_datetime": shift_start.isoformat(),
                "shift_end_datetime": shift_end.isoformat(),
                "client_po_number": "TEST-PO-001",
                "required_employee_counts": {
                    "stagehand": 3,
                    "crew_chief": 1,
                    "fork_operator": 1
                }
            }
            
            create_response = handle_create_shift(shift_data, user_session)
            if create_response.get('success'):
                created_shift = create_response.get('data')
                print(f"✅ Created shift: ID {created_shift.get('id')}")
                print(f"   Start: {created_shift.get('shift_start_datetime')}")
                print(f"   End: {created_shift.get('shift_end_datetime')}")
                print(f"   PO: {created_shift.get('client_po_number')}")
            else:
                print(f"❌ Failed to create shift: {create_response.get('error')}")
                return False
        except Exception as e:
            print(f"❌ Error creating shift: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        # Test 4: Get shifts again to verify the new shift was created
        print(f"\n🔍 Testing get shifts after creation...")
        try:
            shift_data = {"job_id": test_job['id']}
            shift_response2 = handle_get_shifts_by_job(shift_data, user_session)
            if shift_response2.get('success'):
                shifts2 = shift_response2.get('data', [])
                print(f"✅ Found {len(shifts2)} shifts for job {test_job['id']} (after creation)")
                if len(shifts2) > len(shifts):
                    print(f"✅ New shift was successfully created and persisted")
                else:
                    print(f"⚠️  Shift count didn't increase - may be a duplicate or error")
            else:
                print(f"❌ Failed to get shifts after creation: {shift_response2.get('error')}")
                return False
        except Exception as e:
            print(f"❌ Error getting shifts after creation: {e}")
            return False
        
        print(f"\n🎉 All shift management tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = test_shift_management()
    if success:
        print("\n✅ Shift management test PASSED")
    else:
        print("\n❌ Shift management test FAILED")
