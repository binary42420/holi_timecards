#!/usr/bin/env python3
"""
Migration script to add location fields to jobs table.
Each job now represents a specific project at a specific venue.
"""

import sys
from sqlalchemy import text
from main import initialize_database_and_session

def run_job_location_migration():
    """Add location fields to jobs table."""
    print("🔄 Adding location fields to jobs table...")
    
    try:
        # Initialize database connection
        db, _ = initialize_database_and_session()
        print("✓ Database connected")
        
        # SQL commands to add location fields to jobs
        commands = [
            "ALTER TABLE jobs ADD COLUMN venue_name VARCHAR(200) NULL",
            "ALTER TABLE jobs ADD COLUMN venue_address VARCHAR(500) NULL", 
            "ALTER TABLE jobs ADD COLUMN venue_contact_info VARCHAR(300) NULL",
            "ALTER TABLE jobs ADD COLUMN estimated_start_date DATE NULL",
            "ALTER TABLE jobs ADD COLUMN estimated_end_date DATE NULL",
            "ALTER TABLE shifts ADD COLUMN shift_description VARCHAR(200) NULL"
        ]
        
        for i, cmd in enumerate(commands, 1):
            try:
                print(f"Running command {i}/{len(commands)}...")
                db.execute(text(cmd))
                db.commit()
                print(f"✓ Command {i} completed")
            except Exception as e:
                if "Duplicate column name" in str(e):
                    print(f"✓ Column already exists (skipping)")
                else:
                    print(f"⚠️  Command {i} failed: {e}")
        
        # Add indexes for better performance
        index_commands = [
            "CREATE INDEX idx_jobs_venue_name ON jobs(venue_name)",
            "CREATE INDEX idx_jobs_estimated_dates ON jobs(estimated_start_date, estimated_end_date)"
        ]
        
        for cmd in index_commands:
            try:
                db.execute(text(cmd))
                db.commit()
                print("✓ Index created")
            except Exception as e:
                if "Duplicate key name" in str(e):
                    print("✓ Index already exists")
                else:
                    print(f"⚠️  Index creation failed: {e}")
        
        # Update existing jobs with placeholder location data
        print("\n🔄 Updating existing jobs with placeholder location data...")
        try:
            update_query = """
            UPDATE jobs 
            SET venue_name = COALESCE(venue_name, 'TBD - Update Required'),
                venue_address = COALESCE(venue_address, 'Address TBD - Update Required')
            WHERE venue_name IS NULL OR venue_address IS NULL
            """
            
            result = db.execute(text(update_query))
            db.commit()
            print(f"✓ Updated {result.rowcount} existing jobs with placeholder location data")
            
        except Exception as e:
            print(f"⚠️  Data update failed: {e}")
        
        print("\n🎉 Job location migration completed!")
        print("✓ Location fields added to jobs table")
        print("✓ Each job now represents a specific project at a specific venue")
        print("✓ All shifts for a job inherit the job's location")
        print("⚠️  Please update existing jobs with actual venue information")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = run_job_location_migration()
    sys.exit(0 if success else 1)
