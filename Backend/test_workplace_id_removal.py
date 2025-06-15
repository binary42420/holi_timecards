#!/usr/bin/env python3
"""
Test script to verify that workplace_id removal was successful.
This script tests all Extended Settings functionality without workplace_id.
"""

import sys
import traceback
from main import initialize_database_and_session
from db.controllers.extended_settings_controller import ExtendedSettingsController
from db.services.extended_settings_service import ExtendedSettingsService
from db.controllers.workplace_settings_controller import WorkplaceSettingsController

def test_extended_settings():
    """Test Extended Settings functionality without workplace_id."""
    print("🧪 Testing Extended Settings without workplace_id...")
    
    try:
        db, session = initialize_database_and_session()
        
        # Test Extended Settings Controller
        controller = ExtendedSettingsController(session)
        service = ExtendedSettingsService(session)
        
        print("✅ Controllers initialized successfully")
        
        # Test getting all settings (should work without workplace_id)
        try:
            all_settings = controller.get_all_extended_settings()
            print(f"✅ Retrieved {len(all_settings)} settings categories")
        except Exception as e:
            print(f"❌ Failed to get all settings: {e}")
            return False
        
        # Test getting settings summary
        try:
            summary = service.get_settings_summary()
            print("✅ Retrieved settings summary")
        except Exception as e:
            print(f"❌ Failed to get settings summary: {e}")
            return False
        
        # Test updating company profile
        try:
            test_data = {
                'company_name': 'Hands on Labor Test',
                'company_email': 'test@handsonlabor.com'
            }
            updated = controller.update_company_profile_settings(test_data)
            print("✅ Updated company profile settings")
        except Exception as e:
            print(f"❌ Failed to update company profile: {e}")
            return False
        
        # Test bulk settings update
        try:
            bulk_data = {
                'company_profile': {
                    'company_name': 'Hands on Labor',
                    'company_email': 'info@handsonlabor.com'
                }
            }
            bulk_updated = service.update_settings_bulk(bulk_data)
            print("✅ Bulk settings update successful")
        except Exception as e:
            print(f"❌ Failed bulk settings update: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Extended Settings test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        if 'session' in locals():
            session.close()

def test_workplace_settings():
    """Test WorkplaceSettings functionality without workplace_id."""
    print("\n🧪 Testing WorkplaceSettings without workplace_id...")
    
    try:
        db, session = initialize_database_and_session()
        
        # Test WorkplaceSettings Controller
        controller = WorkplaceSettingsController(session)
        
        print("✅ WorkplaceSettings controller initialized successfully")
        
        # Test getting settings (should work without workplace_id)
        try:
            settings = controller.get_settings()
            print("✅ Retrieved workplace settings")
        except Exception as e:
            print(f"❌ Failed to get workplace settings: {e}")
            return False
        
        # Test getting settings as dict
        try:
            settings_dict = controller.get_settings_dict()
            print("✅ Retrieved workplace settings as dict")
        except Exception as e:
            print(f"❌ Failed to get workplace settings dict: {e}")
            return False
        
        # Test updating notification settings
        try:
            notification_data = {
                'email_notifications_enabled': True,
                'notify_on_shift_requests': True
            }
            updated = controller.update_notification_settings(notification_data)
            print("✅ Updated notification settings")
        except Exception as e:
            print(f"❌ Failed to update notification settings: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ WorkplaceSettings test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        if 'session' in locals():
            session.close()

def test_export_import():
    """Test export/import functionality without workplace_id."""
    print("\n🧪 Testing export/import without workplace_id...")
    
    try:
        db, session = initialize_database_and_session()
        
        service = ExtendedSettingsService(session)
        
        # Test export
        try:
            export_data = service.export_settings_for_backup()
            print("✅ Settings export successful")
            
            # Verify export structure
            if 'export_metadata' in export_data:
                metadata = export_data['export_metadata']
                if 'company_name' in metadata and metadata['company_name'] == 'Hands on Labor':
                    print("✅ Export metadata contains correct company name")
                else:
                    print("❌ Export metadata missing or incorrect company name")
                    return False
            else:
                print("❌ Export data missing metadata")
                return False
                
        except Exception as e:
            print(f"❌ Failed to export settings: {e}")
            return False
        
        # Test import
        try:
            import_result = service.import_settings_from_backup(export_data)
            print("✅ Settings import successful")
        except Exception as e:
            print(f"❌ Failed to import settings: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Export/import test failed: {e}")
        traceback.print_exc()
        return False
    finally:
        if 'session' in locals():
            session.close()

def main():
    """Run all tests."""
    print("🎯 Testing Workplace ID Removal")
    print("=" * 50)
    
    tests = [
        ("Extended Settings", test_extended_settings),
        ("Workplace Settings", test_workplace_settings),
        ("Export/Import", test_export_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} tests...")
        if test_func():
            print(f"✅ {test_name} tests PASSED")
            passed += 1
        else:
            print(f"❌ {test_name} tests FAILED")
    
    print(f"\n🎉 Test Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎊 ALL TESTS PASSED! Workplace ID removal was successful!")
        return True
    else:
        print("💥 Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
