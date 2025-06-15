from main import initialize_database_and_session
from db.controllers.extended_settings_controller import ExtendedSettingsController
from db.models import UserManagementSettings
from sqlalchemy import inspect

def test_user_management_settings():
    """Test user management settings functionality"""
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        
        print("🔍 Testing User Management Settings...")
        
        # Check if table exists
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if 'user_management_settings' in tables:
            print("✅ user_management_settings table exists")
            
            # Check table structure
            columns = inspector.get_columns('user_management_settings')
            print(f"📊 Table has {len(columns)} columns:")
            for col in columns[:10]:  # Show first 10 columns
                print(f"   - {col['name']}: {col['type']}")
        else:
            print("❌ user_management_settings table does not exist")
            print("Available tables:", tables)
            return
        
        # Test controller
        try:
            controller = ExtendedSettingsController(db)
            print("✅ ExtendedSettingsController created successfully")
            
            # Test getting current settings
            try:
                current_settings = db.query(UserManagementSettings).first()
                if current_settings:
                    print(f"✅ Found existing user management settings with ID: {current_settings.id}")
                else:
                    print("ℹ️ No existing user management settings found")
                
            except Exception as e:
                print(f"❌ Error querying user management settings: {e}")
            
            # Test validation
            try:
                test_data = {
                    'auto_approve_employees': False,
                    'require_manager_approval': True,
                    'password_min_length': 8,
                    'session_timeout_minutes': 480
                }
                
                errors = controller.validate_user_management_settings(test_data)
                if errors:
                    print(f"⚠️ Validation errors: {errors}")
                else:
                    print("✅ Test data validation passed")
                
                # Test update
                updated_settings = controller.update_user_management_settings(test_data)
                print(f"✅ Successfully updated user management settings with ID: {updated_settings.id}")
                
            except Exception as e:
                print(f"❌ Error testing update: {e}")
                
        except Exception as e:
            print(f"❌ Error creating controller: {e}")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

if __name__ == "__main__":
    test_user_management_settings()
