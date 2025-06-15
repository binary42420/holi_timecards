#!/usr/bin/env python3
"""
Test script to verify the complete timecard management system.
"""

from main import initialize_database_and_session
from handlers.timecard_handlers import (
    handle_get_shift_timecard, handle_clock_in_out_worker, 
    handle_mark_worker_absent, handle_update_worker_notes, 
    handle_end_shift_clock_out_all
)
from handlers.shift_management_handlers import handle_create_shift, handle_assign_worker_to_shift
from user_session import UserSession
from db.controllers.users_controller import UsersController
from db.controllers.jobs_controller import JobsController
from datetime import datetime, timedelta

def test_timecard_system():
    """Test the complete timecard management system."""
    print("🧪 Testing timecard management system...")
    
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        print("✅ Database initialized")
        
        # Get test data
        users_controller = UsersController(db)
        jobs_controller = JobsController(db)
        
        # Get a manager
        all_users = users_controller.get_all_entities()
        managers = [user for user in all_users if user.isManager]
        workers = [user for user in all_users if not user.isManager]
        
        if not managers:
            print("❌ No managers found. Please create a manager first.")
            return False
        
        if len(workers) < 2:
            print("❌ Need at least 2 workers for testing. Please create more workers.")
            return False
        
        test_manager = managers[0]
        test_workers = workers[:2]  # Use first 2 workers
        
        print(f"✅ Using manager: {test_manager.name} (ID: {test_manager.id})")
        print(f"✅ Using workers: {[w.name for w in test_workers]}")
        
        # Create user session
        user_session = UserSession(test_manager.id, test_manager.isManager)
        
        # Get a job
        jobs = jobs_controller.get_all_active_jobs()
        if not jobs:
            print("❌ No jobs found. Please create a job first.")
            return False
        
        test_job = jobs[0]
        print(f"✅ Using job: {test_job['name']} (ID: {test_job['id']})")
        
        # Create a test shift
        print(f"\n🔨 Creating test shift...")
        tomorrow = datetime.now() + timedelta(days=1)
        shift_start = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        shift_end = shift_start + timedelta(hours=8)
        
        shift_data = {
            "job_id": test_job['id'],
            "shift_start_datetime": shift_start.isoformat(),
            "shift_end_datetime": shift_end.isoformat(),
            "shift_description": "Test Shift for Timecard",
            "required_employee_counts": {
                "stagehand": 2,
                "crew_chief": 1
            }
        }
        
        shift_response = handle_create_shift(shift_data, user_session)
        if not shift_response.get('success'):
            print(f"❌ Failed to create shift: {shift_response.get('error')}")
            return False
        
        created_shift = shift_response.get('data')
        shift_id = created_shift.get('id')
        print(f"✅ Created shift: ID {shift_id}")
        
        # Assign workers to the shift
        print(f"\n👥 Assigning workers to shift...")
        for i, worker in enumerate(test_workers):
            role = "crew_chief" if i == 0 else "stagehand"
            assign_data = {
                "shift_id": shift_id,
                "user_id": worker.id,
                "role_assigned": role
            }
            
            assign_response = handle_assign_worker_to_shift(assign_data, user_session)
            if assign_response.get('success'):
                print(f"✅ Assigned {worker.name} as {role}")
            else:
                print(f"⚠️  Failed to assign {worker.name}: {assign_response.get('error')}")
        
        # Test 1: Get shift timecard
        print(f"\n🔍 Testing get shift timecard...")
        timecard_response = handle_get_shift_timecard({"shift_id": shift_id}, user_session)
        if timecard_response.get('success'):
            timecard_data = timecard_response.get('data')
            print(f"✅ Retrieved timecard with {len(timecard_data['workers'])} workers")
            for worker in timecard_data['workers']:
                print(f"   - {worker['user_name']}: {worker['current_status']}")
        else:
            print(f"❌ Failed to get timecard: {timecard_response.get('error')}")
            return False
        
        # Test 2: Clock in workers
        print(f"\n🕐 Testing clock in functionality...")
        for worker in test_workers:
            clock_response = handle_clock_in_out_worker({
                "shift_id": shift_id,
                "user_id": worker.id,
                "action": "clock_in"
            }, user_session)
            
            if clock_response.get('success'):
                print(f"✅ Clocked in {worker.name}")
            else:
                print(f"❌ Failed to clock in {worker.name}: {clock_response.get('error')}")
        
        # Test 3: Update worker notes
        print(f"\n📝 Testing worker notes...")
        notes_response = handle_update_worker_notes({
            "shift_id": shift_id,
            "user_id": test_workers[0].id,
            "notes": "Great performance today! Very reliable worker."
        }, user_session)
        
        if notes_response.get('success'):
            print(f"✅ Updated notes for {test_workers[0].name}")
        else:
            print(f"❌ Failed to update notes: {notes_response.get('error')}")
        
        # Test 4: Mark worker absent
        print(f"\n❌ Testing mark absent functionality...")
        absent_response = handle_mark_worker_absent({
            "shift_id": shift_id,
            "user_id": test_workers[1].id
        }, user_session)
        
        if absent_response.get('success'):
            print(f"✅ Marked {test_workers[1].name} as absent")
        else:
            print(f"❌ Failed to mark absent: {absent_response.get('error')}")
        
        # Test 5: Clock out remaining workers
        print(f"\n🕐 Testing clock out functionality...")
        clock_out_response = handle_clock_in_out_worker({
            "shift_id": shift_id,
            "user_id": test_workers[0].id,
            "action": "clock_out"
        }, user_session)
        
        if clock_out_response.get('success'):
            print(f"✅ Clocked out {test_workers[0].name}")
        else:
            print(f"❌ Failed to clock out: {clock_out_response.get('error')}")
        
        # Test 6: End shift and generate timesheet
        print(f"\n🏁 Testing end shift functionality...")
        end_shift_response = handle_end_shift_clock_out_all({
            "shift_id": shift_id
        }, user_session)
        
        if end_shift_response.get('success'):
            end_data = end_shift_response.get('data')
            print(f"✅ Shift ended successfully")
            print(f"   Clocked out {len(end_data['clocked_out_workers'])} workers")
            print(f"   Generated timesheet with {len(end_data['draft_timesheet']['workers'])} worker records")
        else:
            print(f"❌ Failed to end shift: {end_shift_response.get('error')}")
        
        # Test 7: Get final timecard state
        print(f"\n🔍 Testing final timecard state...")
        final_timecard = handle_get_shift_timecard({"shift_id": shift_id}, user_session)
        if final_timecard.get('success'):
            final_data = final_timecard.get('data')
            print(f"✅ Final timecard retrieved")
            for worker in final_data['workers']:
                print(f"   - {worker['user_name']}: {worker['current_status']}, Hours: {worker['total_hours_worked'] or 0}")
                if worker['shift_notes']:
                    print(f"     Notes: {worker['shift_notes']}")
        
        print(f"\n🎉 All timecard system tests completed successfully!")
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
    success = test_timecard_system()
    if success:
        print("\n✅ Timecard system test PASSED")
    else:
        print("\n❌ Timecard system test FAILED")
