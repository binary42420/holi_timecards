"""
Database migration to add extended settings tables for EasyShifts.
This migration adds all the new settings tables to support the expanded settings functionality.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add the parent directory to the path so we can import our models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Base, CompanyProfile, UserManagementSettings, CertificationsSettings, ClientManagementSettings
from extended_settings_models import JobConfigurationSettings, TimesheetAdvancedSettings, GoogleIntegrationSettings
from additional_settings_models import ReportingSettings, MobileAccessibilitySettings, SystemAdminSettings


def run_migration(database_url=None):
    """
    Run the migration to create all extended settings tables.
    
    Args:
        database_url (str): Database connection URL. If None, uses environment variable.
    """
    
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///easyshifts.db')
    
    print(f"Running migration on database: {database_url}")
    
    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Create all new tables
        print("Creating extended settings tables...")
        
        # Create tables for all new settings models
        tables_to_create = [
            CompanyProfile.__table__,
            UserManagementSettings.__table__,
            CertificationsSettings.__table__,
            ClientManagementSettings.__table__,
            JobConfigurationSettings.__table__,
            TimesheetAdvancedSettings.__table__,
            GoogleIntegrationSettings.__table__,
            ReportingSettings.__table__,
            MobileAccessibilitySettings.__table__,
            SystemAdminSettings.__table__,
        ]
        
        for table in tables_to_create:
            try:
                table.create(engine, checkfirst=True)
                print(f"✓ Created table: {table.name}")
            except Exception as e:
                print(f"✗ Error creating table {table.name}: {str(e)}")
        
        # Commit the transaction
        session.commit()
        print("✓ Migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration failed: {str(e)}")
        session.rollback()
        raise
    
    finally:
        session.close()


def rollback_migration(database_url=None):
    """
    Rollback the migration by dropping all extended settings tables.
    
    Args:
        database_url (str): Database connection URL. If None, uses environment variable.
    """
    
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///easyshifts.db')
    
    print(f"Rolling back migration on database: {database_url}")
    
    # Create engine
    engine = create_engine(database_url)
    
    try:
        # Drop all new tables in reverse order
        tables_to_drop = [
            'system_admin_settings',
            'mobile_accessibility_settings',
            'reporting_settings',
            'google_integration_settings',
            'timesheet_advanced_settings',
            'job_configuration_settings',
            'client_management_settings',
            'certifications_settings',
            'user_management_settings',
            'company_profile',
        ]
        
        for table_name in tables_to_drop:
            try:
                engine.execute(f"DROP TABLE IF EXISTS {table_name}")
                print(f"✓ Dropped table: {table_name}")
            except Exception as e:
                print(f"✗ Error dropping table {table_name}: {str(e)}")
        
        print("✓ Rollback completed successfully!")
        
    except Exception as e:
        print(f"✗ Rollback failed: {str(e)}")
        raise


def create_default_settings(database_url=None):
    """
    Create default settings records for Hands on Labor.
    Since this is a single company system, we only need one set of settings.

    Args:
        database_url (str): Database connection URL. If None, uses environment variable.
    """

    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///easyshifts.db')

    print("Creating default settings for Hands on Labor")

    # Create engine and session
    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create default settings for each category
        settings_models = [
            CompanyProfile,
            UserManagementSettings,
            CertificationsSettings,
            ClientManagementSettings,
            JobConfigurationSettings,
            TimesheetAdvancedSettings,
            GoogleIntegrationSettings,
            ReportingSettings,
            MobileAccessibilitySettings,
            SystemAdminSettings,
        ]

        for model_class in settings_models:
            # Check if settings already exist
            existing = session.query(model_class).first()

            if not existing:
                # Create new default settings
                new_settings = model_class()
                session.add(new_settings)
                print(f"✓ Created default {model_class.__name__}")
            else:
                print(f"- {model_class.__name__} already exists")

        # Commit the transaction
        session.commit()
        print("✓ Default settings created successfully!")

    except Exception as e:
        print(f"✗ Failed to create default settings: {str(e)}")
        session.rollback()
        raise

    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='EasyShifts Extended Settings Migration')
    parser.add_argument('action', choices=['migrate', 'rollback', 'create-defaults'], 
                       help='Action to perform')
    parser.add_argument('--database-url', help='Database connection URL')
    parser.add_argument('--workplace-id', type=int, default=1, 
                       help='Workplace ID for creating default settings')
    
    args = parser.parse_args()
    
    if args.action == 'migrate':
        run_migration(args.database_url)
    elif args.action == 'rollback':
        rollback_migration(args.database_url)
    elif args.action == 'create-defaults':
        create_default_settings(args.database_url)
