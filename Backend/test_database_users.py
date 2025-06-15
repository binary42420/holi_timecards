from main import initialize_database_and_session
from db.controllers.users_controller import UsersController

def test_database_users():
    """Test database users and create test user if needed"""
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        users_controller = UsersController(db)
        
        print("🔍 Checking existing users...")
        
        # Try to get all users
        try:
            # Get all users (this might not work if there's no get_all method)
            print("📊 Attempting to list users...")
            
            # Try to find admin user
            try:
                admin_exists, is_manager = users_controller.check_user_existence_and_manager_status("admin", "admin")
                print(f"👤 Admin user exists: {admin_exists}, is_manager: {is_manager}")
            except Exception as e:
                print(f"❌ Error checking admin user: {e}")
                admin_exists = False
            
            if not admin_exists:
                print("🔧 Creating admin user...")
                try:
                    # Create admin user
                    admin_data = {
                        "username": "admin",
                        "password": "admin",
                        "name": "Administrator",
                        "email": "admin@handsonlabor.com",
                        "isManager": True,
                        "isApproval": True
                    }
                    
                    new_user = users_controller.create_entity(admin_data)
                    print(f"✅ Admin user created with ID: {new_user.id}")
                    
                except Exception as e:
                    print(f"❌ Error creating admin user: {e}")
            
            # Try to find test manager
            try:
                manager_exists, is_manager = users_controller.check_user_existence_and_manager_status("manager", "password")
                print(f"👤 Manager user exists: {manager_exists}, is_manager: {is_manager}")
            except Exception as e:
                print(f"❌ Error checking manager user: {e}")
                manager_exists = False
            
            if not manager_exists:
                print("🔧 Creating manager user...")
                try:
                    # Create manager user
                    manager_data = {
                        "username": "manager",
                        "password": "password",
                        "name": "Test Manager",
                        "email": "manager@handsonlabor.com",
                        "isManager": True,
                        "isApproval": True
                    }
                    
                    new_user = users_controller.create_entity(manager_data)
                    print(f"✅ Manager user created with ID: {new_user.id}")
                    
                except Exception as e:
                    print(f"❌ Error creating manager user: {e}")
                    
        except Exception as e:
            print(f"❌ Error accessing users: {e}")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

if __name__ == "__main__":
    test_database_users()
