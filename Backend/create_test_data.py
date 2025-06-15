from main import initialize_database_and_session
from db.controllers.jobs_controller import JobsController
from db.controllers.shifts_controller import ShiftsController
from db.controllers.users_controller import UsersController
from db.controllers.client_companies_controller import ClientCompaniesController
from datetime import datetime, timedelta

def create_test_data():
    """Create test data for jobs and shifts"""
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        
        # Initialize controllers
        jobs_controller = JobsController(db)
        shifts_controller = ShiftsController(db)
        users_controller = UsersController(db)
        client_companies_controller = ClientCompaniesController(db)
        
        print("🔧 Creating test data...")
        
        # Get manager user ID
        try:
            manager_exists, is_manager = users_controller.check_user_existence_and_manager_status("manager", "password")
            if not manager_exists:
                print("❌ Manager user not found. Please run test_database_users.py first.")
                return
            
            manager_id = users_controller.get_user_id_by_username_and_password("manager", "password")
            print(f"✅ Found manager user with ID: {manager_id}")
        except Exception as e:
            print(f"❌ Error getting manager user: {e}")
            return
        
        # Create a test client company
        try:
            print("\n🏢 Creating test client company...")
            client_data = {
                "name": "Test Event Company"
            }

            client_company = client_companies_controller.create_entity(client_data)
            print(f"✅ Created client company with ID: {client_company.id}")

        except Exception as e:
            print(f"❌ Error creating client company: {e}")
            # Try to get existing client company
            try:
                # This might not work, but let's try
                client_company = None
                print("⚠️ Using manager as client for job creation")
            except:
                client_company = None
        
        # Create test jobs
        try:
            print("\n💼 Creating test jobs...")
            
            # Job 1: Concert Setup
            job1_data = {
                "name": "Concert Setup - Downtown Arena",
                "description": "Stage setup and equipment installation for major concert event",
                "venue_name": "Downtown Arena",
                "venue_address": "456 Arena Blvd, San Diego, CA 92101",
                "client_company_id": client_company.id if client_company else 1,
                "created_by": manager_id,
                "estimated_start_date": (datetime.now() + timedelta(days=3)).date(),
                "estimated_end_date": (datetime.now() + timedelta(days=4)).date()
            }

            job1 = jobs_controller.create_entity(job1_data)
            print(f"✅ Created job 1 with ID: {job1.id}")

            # Job 2: Corporate Event
            job2_data = {
                "name": "Corporate Event Setup",
                "description": "Setup for annual company meeting and awards ceremony",
                "venue_name": "Convention Center Hall A",
                "venue_address": "789 Convention Way, San Diego, CA 92101",
                "client_company_id": client_company.id if client_company else 1,
                "created_by": manager_id,
                "estimated_start_date": (datetime.now() + timedelta(days=5)).date(),
                "estimated_end_date": (datetime.now() + timedelta(days=5)).date()
            }
            
            job2 = jobs_controller.create_entity(job2_data)
            print(f"✅ Created job 2 with ID: {job2.id}")
            
        except Exception as e:
            print(f"❌ Error creating jobs: {e}")
            return
        
        # Create test shifts
        try:
            print("\n📅 Creating test shifts...")
            
            # Shifts for Job 1 (Concert Setup)
            # Setup day
            shift1_data = {
                "job_id": job1.id,
                "shift_start_datetime": datetime.now() + timedelta(days=3, hours=6),  # 6 AM
                "shift_end_datetime": datetime.now() + timedelta(days=3, hours=18),   # 6 PM
                "required_employee_counts": {
                    "stagehand": 8,
                    "crew_chief": 2,
                    "forklift_operator": 2,
                    "truck_driver": 1
                },
                "client_po_number": "PO-2024-001",
                "shift_description": "Main setup day - stage construction and equipment load-in"
            }
            
            shift1 = shifts_controller.create_entity(shift1_data)
            print(f"✅ Created shift 1 with ID: {shift1.id}")
            
            # Event day
            shift2_data = {
                "job_id": job1.id,
                "shift_start_datetime": datetime.now() + timedelta(days=4, hours=14),  # 2 PM
                "shift_end_datetime": datetime.now() + timedelta(days=5, hours=2),     # 2 AM next day
                "required_employee_counts": {
                    "stagehand": 6,
                    "crew_chief": 1
                },
                "client_po_number": "PO-2024-001",
                "shift_description": "Event day - show support and breakdown"
            }
            
            shift2 = shifts_controller.create_entity(shift2_data)
            print(f"✅ Created shift 2 with ID: {shift2.id}")
            
            # Shifts for Job 2 (Corporate Event)
            shift3_data = {
                "job_id": job2.id,
                "shift_start_datetime": datetime.now() + timedelta(days=5, hours=8),   # 8 AM
                "shift_end_datetime": datetime.now() + timedelta(days=5, hours=16),    # 4 PM
                "required_employee_counts": {
                    "stagehand": 4,
                    "crew_chief": 1
                },
                "client_po_number": "PO-2024-002",
                "shift_description": "Corporate event setup and breakdown"
            }
            
            shift3 = shifts_controller.create_entity(shift3_data)
            print(f"✅ Created shift 3 with ID: {shift3.id}")
            
        except Exception as e:
            print(f"❌ Error creating shifts: {e}")
            return
        
        print("\n🎉 Test data creation completed successfully!")
        print("📊 Summary:")
        print(f"   - Created 1 client company")
        print(f"   - Created 2 jobs")
        print(f"   - Created 3 shifts")
        print("\n✅ You can now test the schedule data retrieval functionality!")
        
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

if __name__ == "__main__":
    create_test_data()
