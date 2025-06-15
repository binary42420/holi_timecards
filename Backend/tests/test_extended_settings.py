"""
Comprehensive tests for the extended settings functionality.
Tests all new settings categories, validation, and API endpoints.
"""

import unittest
import json
import sys
import os
from datetime import datetime, time

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.models import Base, User, CompanyProfile, UserManagementSettings, CertificationsSettings, ClientManagementSettings
from db.extended_settings_models import JobConfigurationSettings, TimesheetAdvancedSettings, GoogleIntegrationSettings
from db.additional_settings_models import ReportingSettings, MobileAccessibilitySettings, SystemAdminSettings
from db.controllers.extended_settings_controller import ExtendedSettingsController
from handlers.enhanced_settings_handlers import (
    handle_update_company_profile_settings,
    handle_update_user_management_settings,
    handle_get_extended_settings,
    handle_test_google_connection,
    handle_system_health_check
)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from user_session import UserSession


class TestExtendedSettings(unittest.TestCase):
    """Test cases for extended settings functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test database and session."""
        # Create in-memory SQLite database for testing
        cls.engine = create_engine('sqlite:///:memory:', echo=False)
        Base.metadata.create_all(cls.engine)
        
        Session = sessionmaker(bind=cls.engine)
        cls.session = Session()
        
        # Create test workplace user
        cls.test_workplace = User(
            id=1,
            email='test@handsonlabor.com',
            password_hash='test_hash',
            first_name='Test',
            last_name='Manager',
            role='manager',
            is_active=True
        )
        cls.session.add(cls.test_workplace)
        cls.session.commit()
        
        # Create controller instance
        cls.controller = ExtendedSettingsController(cls.session)

    @classmethod
    def tearDownClass(cls):
        """Clean up test database."""
        cls.session.close()

    def setUp(self):
        """Set up for each test."""
        # Create mock user session
        self.user_session = UserSession(
            user_id=1,
            email='test@handsonlabor.com',
            role='manager',
            first_name='Test',
            last_name='Manager'
        )

    def test_company_profile_settings_creation(self):
        """Test creating company profile settings."""
        test_data = {
            'company_name': 'Hands on Labor Test',
            'company_tagline': 'Professional Labor Solutions',
            'company_email': 'info@handsonlabor.com',
            'company_phone': '(619) 555-0123',
            'default_hourly_rate': 28.50,
            'operating_hours_start': '06:00',
            'operating_hours_end': '22:00',
            'time_zone': 'America/Los_Angeles'
        }
        
        result = self.controller.update_company_profile_settings(1, test_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.company_name, 'Hands on Labor Test')
        self.assertEqual(result.company_email, 'info@handsonlabor.com')
        self.assertEqual(result.default_hourly_rate, 28.50)

    def test_user_management_settings_creation(self):
        """Test creating user management settings."""
        test_data = {
            'auto_approve_employees': False,
            'require_manager_approval': True,
            'password_min_length': 10,
            'session_timeout_minutes': 480,
            'crew_chief_premium_rate': 5.00,
            'forklift_operators_premium_rate': 3.00,
            'truck_drivers_premium_rate': 4.00
        }
        
        result = self.controller.update_user_management_settings(1, test_data)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.password_min_length, 10)
        self.assertEqual(result.crew_chief_premium_rate, 5.00)
        self.assertFalse(result.auto_approve_employees)

    def test_certifications_settings_creation(self):
        """Test creating certifications settings."""
        test_data = {
            'require_crew_chief_certification': True,
            'require_forklift_certification': True,
            'crew_chief_cert_validity_months': 24,
            'forklift_cert_validity_months': 36,
            'auto_notify_expiring_certs': True,
            'cert_expiry_warning_days': 30,
            'custom_certifications': [
                {
                    'name': 'Rigging Certification',
                    'validity_months': 12,
                    'required': True
                }
            ]
        }
        
        result = self.controller.update_certifications_settings(1, test_data)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.require_crew_chief_certification)
        self.assertEqual(result.crew_chief_cert_validity_months, 24)
        self.assertEqual(len(result.custom_certifications), 1)

    def test_job_configuration_settings_creation(self):
        """Test creating job configuration settings."""
        test_data = {
            'enable_job_templates': True,
            'default_job_duration_hours': 8,
            'require_crew_chief_per_shift': True,
            'max_workers_per_crew_chief': 8,
            'require_job_location': True,
            'min_notice_hours_new_jobs': 24,
            'job_templates': [
                {
                    'id': 1,
                    'name': 'Stage Setup',
                    'duration_hours': 8,
                    'required_roles': {
                        'crew_chief': 1,
                        'stagehand': 6,
                        'forklift_operator': 1
                    }
                }
            ]
        }
        
        result = self.controller.update_job_configuration_settings(1, test_data)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.enable_job_templates)
        self.assertEqual(result.max_workers_per_crew_chief, 8)
        self.assertEqual(len(result.job_templates), 1)

    def test_timesheet_advanced_settings_creation(self):
        """Test creating advanced timesheet settings."""
        test_data = {
            'require_location_verification': True,
            'location_verification_radius_feet': 100,
            'max_clock_pairs_per_shift': 3,
            'overtime_threshold_daily': 8,
            'overtime_rate_multiplier': 1.5,
            'crew_chiefs_can_edit_team_times': True,
            'clients_can_view_timesheets': True,
            'round_time_to_nearest_minutes': 15
        }
        
        result = self.controller.update_timesheet_advanced_settings(1, test_data)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.require_location_verification)
        self.assertEqual(result.overtime_rate_multiplier, 1.5)
        self.assertEqual(result.max_clock_pairs_per_shift, 3)

    def test_google_integration_settings_creation(self):
        """Test creating Google integration settings."""
        test_data = {
            'google_oauth_enabled': True,
            'google_client_id': 'test_client_id',
            'google_client_secret': 'test_client_secret',
            'google_calendar_sync_enabled': True,
            'calendar_sync_direction': 'both',
            'gmail_notifications_enabled': False,
            'google_maps_enabled': True,
            'sync_frequency_minutes': 15
        }
        
        result = self.controller.update_google_integration_settings(1, test_data)
        
        self.assertIsNotNone(result)
        self.assertTrue(result.google_oauth_enabled)
        self.assertEqual(result.google_client_id, 'test_client_id')
        self.assertTrue(result.google_calendar_sync_enabled)

    def test_validation_errors(self):
        """Test validation error handling."""
        # Test invalid company profile data
        invalid_data = {
            'company_name': '',  # Empty name should fail
            'default_hourly_rate': -5.0,  # Negative rate should fail
            'company_email': 'invalid_email'  # Invalid email format
        }
        
        errors = self.controller.validate_company_profile_settings(invalid_data)
        self.assertGreater(len(errors), 0)
        self.assertIn('Company name is required', errors)
        self.assertIn('Hourly rate must be positive', errors)

    def test_get_all_extended_settings(self):
        """Test retrieving all extended settings."""
        # First create some settings
        self.controller.update_company_profile_settings(1, {'company_name': 'Test Company'})
        self.controller.update_user_management_settings(1, {'password_min_length': 8})
        
        # Get all settings
        all_settings = self.controller.get_all_extended_settings(1)
        
        self.assertIsInstance(all_settings, dict)
        self.assertIn('company_profile', all_settings)
        self.assertIn('user_management', all_settings)
        self.assertIn('certifications', all_settings)
        self.assertIn('job_configuration', all_settings)

    def test_reset_to_defaults(self):
        """Test resetting all settings to defaults."""
        # First create some custom settings
        self.controller.update_company_profile_settings(1, {'company_name': 'Custom Company'})
        
        # Reset to defaults
        reset_settings = self.controller.reset_all_to_defaults(1)
        
        self.assertIsInstance(reset_settings, dict)
        # Check that settings were reset (company name should be default)
        company_profile = self.session.query(CompanyProfile).filter_by(workplace_id=1).first()
        self.assertEqual(company_profile.company_name, 'Hands on Labor')

    def test_handler_functions(self):
        """Test the handler functions."""
        # Test company profile update handler
        test_data = {
            'company_name': 'Handler Test Company',
            'default_hourly_rate': 30.0
        }
        
        result = handle_update_company_profile_settings(test_data, self.user_session)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['company_name'], 'Handler Test Company')

    def test_google_connection_test(self):
        """Test Google connection testing."""
        test_data = {
            'google_client_id': 'test_id',
            'google_client_secret': 'test_secret'
        }
        
        result = handle_test_google_connection(test_data, self.user_session)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('connection_status', result['data'])

    def test_system_health_check(self):
        """Test system health check."""
        result = handle_system_health_check(self.user_session)
        
        self.assertTrue(result['success'])
        self.assertIn('data', result)
        self.assertIn('overall_status', result['data'])

    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access settings."""
        # Create employee user session (not manager)
        employee_session = UserSession(
            user_id=2,
            email='employee@test.com',
            role='employee',
            first_name='Test',
            last_name='Employee'
        )
        
        result = handle_update_company_profile_settings({}, employee_session)
        
        self.assertFalse(result['success'])
        self.assertIn('Unauthorized', result['error'])


class TestSettingsIntegration(unittest.TestCase):
    """Integration tests for settings functionality."""

    def test_settings_persistence(self):
        """Test that settings persist across sessions."""
        # This would test database persistence
        pass

    def test_settings_api_endpoints(self):
        """Test API endpoint integration."""
        # This would test the full API flow
        pass


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
