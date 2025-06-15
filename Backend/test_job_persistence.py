#!/usr/bin/env python3
"""
Test script to verify job creation and persistence in the database.
"""

from main import initialize_database_and_session
from db.controllers.jobs_controller import JobsController
from db.controllers.client_companies_controller import ClientCompaniesController
from db.controllers.users_controller import UsersController

def test_job_persistence():
    """Test job creation and retrieval to verify database persistence."""
    print("🧪 Testing job persistence...")
    
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        print("✅ Database initialized")
        
        # Initialize controllers
        jobs_controller = JobsController(db)
        client_companies_controller = ClientCompaniesController(db)
        users_controller = UsersController(db)
        
        # Get or create a test client company
        print("\n📋 Setting up test data...")
        try:
            # Try to get existing client companies
            client_companies = client_companies_controller.get_all_entities()
            if client_companies:
                test_client_company = client_companies[0]
                print(f"✅ Using existing client company: {test_client_company.name} (ID: {test_client_company.id})")
            else:
                # Create a test client company
                client_data = {"name": "Test Company Ltd"}
                test_client_company = client_companies_controller.create_entity(client_data)
                print(f"✅ Created test client company: {test_client_company.name} (ID: {test_client_company.id})")
        except Exception as e:
            print(f"❌ Error setting up client company: {e}")
            return False
        
        # Get or create a test manager
        try:
            # Try to get existing managers
            all_users = users_controller.get_all_entities()
            managers = [user for user in all_users if user.isManager]
            if managers:
                test_manager = managers[0]
                print(f"✅ Using existing manager: {test_manager.name} (ID: {test_manager.id})")
            else:
                print("❌ No managers found in database. Please create a manager first.")
                return False
        except Exception as e:
            print(f"❌ Error getting manager: {e}")
            return False
        
        # Test job creation
        print(f"\n🔨 Creating test job...")
        job_data = {
            "name": "Test Job - Persistence Check",
            "client_company_id": test_client_company.id,
            "workplace_id": test_manager.id
        }
        
        try:
            created_job = jobs_controller.create_job(job_data)
            print(f"✅ Job created: {created_job['name']} (ID: {created_job['id']})")
        except Exception as e:
            print(f"❌ Error creating job: {e}")
            return False
        
        # Test job retrieval immediately after creation
        print(f"\n🔍 Testing immediate retrieval...")
        try:
            jobs_for_manager = jobs_controller.get_jobs_by_workplace_id(test_manager.id)
            print(f"✅ Found {len(jobs_for_manager)} jobs for manager {test_manager.id}")
            
            # Check if our created job is in the list
            created_job_found = any(job['id'] == created_job['id'] for job in jobs_for_manager)
            if created_job_found:
                print(f"✅ Created job found in immediate retrieval")
            else:
                print(f"❌ Created job NOT found in immediate retrieval")
                return False
                
        except Exception as e:
            print(f"❌ Error retrieving jobs: {e}")
            return False
        
        # Close and reopen database session to test persistence
        print(f"\n🔄 Testing persistence across sessions...")
        db.close()
        
        # Reinitialize database session
        db2, _ = initialize_database_and_session()
        jobs_controller2 = JobsController(db2)
        
        try:
            jobs_for_manager2 = jobs_controller2.get_jobs_by_workplace_id(test_manager.id)
            print(f"✅ Found {len(jobs_for_manager2)} jobs for manager {test_manager.id} in new session")
            
            # Check if our created job persists across sessions
            created_job_found2 = any(job['id'] == created_job['id'] for job in jobs_for_manager2)
            if created_job_found2:
                print(f"✅ Created job persists across database sessions")
            else:
                print(f"❌ Created job does NOT persist across database sessions")
                return False
                
        except Exception as e:
            print(f"❌ Error retrieving jobs in new session: {e}")
            return False
        finally:
            db2.close()
        
        print(f"\n🎉 All tests passed! Job persistence is working correctly.")
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
    success = test_job_persistence()
    if success:
        print("\n✅ Job persistence test PASSED")
    else:
        print("\n❌ Job persistence test FAILED")
