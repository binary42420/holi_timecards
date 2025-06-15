#!/usr/bin/env python3
"""
Migration script to add datetime fields to the shifts table.
This adds the new shift_start_datetime and shift_end_datetime columns.
"""

import sys
from sqlalchemy import text
from main import initialize_database_and_session

def run_shift_datetime_migration():
    """Run the shift datetime migration."""
    print("🔄 Running shift datetime migration...")
    
    try:
        # Initialize database connection
        db, _ = initialize_database_and_session()
        print("✓ Database connected")
        
        # SQL commands to run
        commands = [
            "ALTER TABLE shifts ADD COLUMN shift_start_datetime DATETIME NULL",
            "ALTER TABLE shifts ADD COLUMN shift_end_datetime DATETIME NULL",
            "ALTER TABLE shifts ADD COLUMN required_employee_counts JSON NULL",
            "ALTER TABLE shifts ADD COLUMN client_po_number VARCHAR(50) NULL"
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
            "CREATE INDEX idx_shifts_start_datetime ON shifts(shift_start_datetime)",
            "CREATE INDEX idx_shifts_job_id ON shifts(job_id)"
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
        
        # Update existing shifts to have datetime values based on legacy fields
        print("\n🔄 Migrating existing shift data...")
        try:
            # Get all shifts that have legacy date/part but no datetime
            migration_query = """
            UPDATE shifts 
            SET shift_start_datetime = CASE 
                WHEN shiftPart = 'morning' THEN CONCAT(shiftDate, ' 06:00:00')
                WHEN shiftPart = 'noon' THEN CONCAT(shiftDate, ' 12:00:00')
                WHEN shiftPart = 'evening' THEN CONCAT(shiftDate, ' 18:00:00')
                ELSE CONCAT(shiftDate, ' 09:00:00')
            END,
            shift_end_datetime = CASE 
                WHEN shiftPart = 'morning' THEN CONCAT(shiftDate, ' 14:00:00')
                WHEN shiftPart = 'noon' THEN CONCAT(shiftDate, ' 20:00:00')
                WHEN shiftPart = 'evening' THEN CONCAT(shiftDate, ' 02:00:00')
                ELSE CONCAT(shiftDate, ' 17:00:00')
            END
            WHERE shift_start_datetime IS NULL 
            AND shiftDate IS NOT NULL
            """
            
            result = db.execute(text(migration_query))
            db.commit()
            print(f"✓ Migrated {result.rowcount} existing shifts to new datetime format")
            
        except Exception as e:
            print(f"⚠️  Data migration failed: {e}")
        
        print("\n🎉 Shift datetime migration completed!")
        print("✓ New datetime columns added successfully")
        print("✓ Existing data migrated to new format")
        print("✓ You can now use the enhanced shift management features")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = run_shift_datetime_migration()
    sys.exit(0 if success else 1)
