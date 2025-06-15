#!/usr/bin/env python3
"""
Test script to check client directory functionality and database content.
"""

from main import get_db_session
from db.controllers.client_companies_controller import ClientCompaniesController
from db.controllers.users_controller import UsersController
from db.controllers.jobs_controller import JobsController
from handlers.client_directory_handlers import handle_get_client_directory
from user_session import UserSession

def test_client_directory():
    """Test client directory functionality."""
    print("🧪 Testing client directory...")
    
    try:
        # Test database connection
        print("\n🔍 Testing database connection...")
        with get_db_session() as db:
            print("✅ Database connection successful")
            
            # Initialize controllers
            client_companies_controller = ClientCompaniesController(db)
            users_controller = UsersController(db)
            jobs_controller = JobsController(db)
            
            # Check client companies
            print("\n🏢 Checking client companies...")
            try:
                companies = client_companies_controller.get_all_entities()
                print(f"✅ Found {len(companies)} client companies:")
                for company in companies:
                    print(f"   - {company.name} (ID: {company.id})")
                    
                if len(companies) == 0:
                    print("⚠️  No client companies found - creating test data...")
                    # Create test client companies
                    test_companies = [
                        {"name": "ABC Events Inc"},
                        {"name": "XYZ Productions"},
                        {"name": "Event Masters LLC"}
                    ]
                    
                    for company_data in test_companies:
                        try:
                            company = client_companies_controller.create_entity(company_data)
                            print(f"✅ Created: {company.name} (ID: {company.id})")
                        except Exception as e:
                            print(f"❌ Error creating {company_data['name']}: {e}")
                    
                    # Re-check companies
                    companies = client_companies_controller.get_all_entities()
                    print(f"✅ Now have {len(companies)} client companies")
                    
            except Exception as e:
                print(f"❌ Error checking client companies: {e}")
                return False
            
            # Check users
            print("\n👥 Checking users...")
            try:
                # Check for manager user
                manager_exists, is_manager = users_controller.check_user_existence_and_manager_status("manager", "password")
                print(f"✅ Manager user exists: {manager_exists}, is_manager: {is_manager}")
                
                if manager_exists:
                    manager_id = users_controller.get_user_id_by_username_and_password("manager", "password")
                    print(f"✅ Manager user ID: {manager_id}")
                    
                    # Test client directory handler
                    print("\n🔍 Testing client directory handler...")
                    user_session = UserSession(manager_id, True)
                    result = handle_get_client_directory(user_session)
                    
                    print(f"✅ Handler result: {result}")
                    
                    if result.get('success'):
                        companies_data = result.get('data', {}).get('companies', [])
                        summary = result.get('data', {}).get('summary', {})
                        print(f"✅ Client directory returned {len(companies_data)} companies")
                        print(f"✅ Summary: {summary}")
                    else:
                        print(f"❌ Client directory handler failed: {result.get('error')}")
                        return False
                else:
                    print("❌ Manager user not found")
                    return False
                    
            except Exception as e:
                print(f"❌ Error checking users: {e}")
                return False
                
        print("\n🎉 Client directory test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Client directory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_client_directory()
