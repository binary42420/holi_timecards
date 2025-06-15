from main import initialize_database_and_session
from db.controllers.extended_settings_controller import ExtendedSettingsController
from db.extended_settings_models import TimesheetAdvancedSettings
from sqlalchemy import inspect

def test_timesheet_advanced_settings():
    """Test timesheet advanced settings functionality"""
    try:
        # Initialize database
        db, _ = initialize_database_and_session()
        
        print("🔍 Testing Timesheet Advanced Settings...")
        
        # Check if table exists
        inspector = inspect(db.bind)
        tables = inspector.get_table_names()
        
        if 'timesheet_advanced_settings' in tables:
            print("✅ timesheet_advanced_settings table exists")
            
            # Check table structure
            columns = inspector.get_columns('timesheet_advanced_settings')
            print(f"📊 Table has {len(columns)} columns")
        else:
            print("❌ timesheet_advanced_settings table does not exist")
            print("Available tables:", tables)
            return
        
        # Test controller
        try:
            controller = ExtendedSettingsController(db)
            print("✅ ExtendedSettingsController created successfully")
            
            # Test getting current settings
            try:
                current_settings = db.query(TimesheetAdvancedSettings).first()
                if current_settings:
                    print(f"✅ Found existing timesheet advanced settings with ID: {current_settings.id}")
                    print(f"   Overtime rate multiplier: {current_settings.overtime_rate_multiplier}")
                    print(f"   Require photo clock in: {current_settings.require_photo_clock_in}")
                else:
                    print("ℹ️ No existing timesheet advanced settings found")
                
            except Exception as e:
                print(f"❌ Error querying timesheet advanced settings: {e}")
            
            # Test validation
            try:
                test_data = {
                    'require_photo_clock_in': True,
                    'require_location_verification': False,
                    'overtime_rate_multiplier': 1.5,
                    'auto_clock_out_hours': 10
                }
                
                errors = controller.validate_timesheet_advanced_settings(test_data)
                if errors:
                    print(f"⚠️ Validation errors: {errors}")
                else:
                    print("✅ Test data validation passed")
                
                # Test update
                updated_settings = controller.update_timesheet_advanced_settings(test_data)
                print(f"✅ Successfully updated timesheet advanced settings with ID: {updated_settings.id}")
                
                # Test to_dict method
                settings_dict = updated_settings.to_dict()
                print(f"✅ to_dict() method works, returned {len(settings_dict)} fields")
                print(f"   Sample fields: require_photo_clock_in={settings_dict.get('require_photo_clock_in')}")
                print(f"   Sample fields: overtime_rate_multiplier={settings_dict.get('overtime_rate_multiplier')}")
                
            except Exception as e:
                print(f"❌ Error testing update: {e}")
                
        except Exception as e:
            print(f"❌ Error creating controller: {e}")
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")

if __name__ == "__main__":
    test_timesheet_advanced_settings()
