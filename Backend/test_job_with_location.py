#!/usr/bin/env python3
"""
Test script to verify job creation with location information.
"""

from main import initialize_database_and_session
from handlers.job_handlers import handle_create_job, handle_get_jobs_by_manager
from user_session import UserSession
from db.controllers.users_controller import UsersController
from db.controllers.client_companies_controller import ClientCompaniesController

def test_job_with_location():
    """Test job creation with location information."""
    print("🧪 Testing job creation with location...")
    
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        print("✅ Database initialized")
        
        # Get a test manager
        users_controller = UsersController(db)
        all_users = users_controller.get_all_entities()
        managers = [user for user in all_users if user.isManager]
        if not managers:
            print("❌ No managers found in database. Please create a manager first.")
            return False
        
        test_manager = managers[0]
        print(f"✅ Using manager: {test_manager.name} (ID: {test_manager.id})")
        
        # Create user session for the manager
        user_session = UserSession(test_manager.id, test_manager.isManager)
        
        # Get a client company
        client_companies_controller = ClientCompaniesController(db)
        client_companies = client_companies_controller.get_all_entities()
        if not client_companies:
            print("❌ No client companies found. Please create a client company first.")
            return False
        
        test_client = client_companies[0]
        print(f"✅ Using client company: {test_client.name} (ID: {test_client.id})")
        
        # Test job creation with location
        print(f"\n🔨 Testing job creation with location...")
        job_data = {
            "name": "Comic-Con Booth Setup",
            "client_company_id": test_client.id,
            "venue_name": "San Diego Convention Center",
            "venue_address": "111 W Harbor Dr, San Diego, CA 92101",
            "venue_contact_info": "Event Coordinator - (619) 525-5000",
            "description": "Setup and teardown of exhibition booths for Comic-Con International"
        }
        
        create_response = handle_create_job(job_data, user_session)
        if create_response.get('success'):
            created_job = create_response.get('data')
            print(f"✅ Job created successfully:")
            print(f"   ID: {created_job.get('id')}")
            print(f"   Name: {created_job.get('name')}")
            print(f"   Venue: {created_job.get('venue_name')}")
            print(f"   Address: {created_job.get('venue_address')}")
            print(f"   Contact: {created_job.get('venue_contact_info')}")
            print(f"   Description: {created_job.get('description')}")
        else:
            print(f"❌ Failed to create job: {create_response.get('error')}")
            return False
        
        # Test job retrieval
        print(f"\n🔍 Testing job retrieval...")
        jobs_response = handle_get_jobs_by_manager(user_session)
        if jobs_response.get('success'):
            jobs = jobs_response.get('data', [])
            print(f"✅ Found {len(jobs)} jobs:")
            for job in jobs:
                print(f"   - {job.get('name')} at {job.get('venue_name', 'No venue')}")
        else:
            print(f"❌ Failed to get jobs: {jobs_response.get('error')}")
            return False
        
        print(f"\n🎉 All tests passed! Job creation with location is working correctly.")
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
    success = test_job_with_location()
    if success:
        print("\n✅ Job with location test PASSED")
    else:
        print("\n❌ Job with location test FAILED")
