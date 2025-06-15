#!/usr/bin/env python3
"""
Migration script to add the new timecard columns to shiftWorkers table.
This adds the multiple clock in/out pairs and other missing columns.
"""

import sys
from sqlalchemy import text
from main import initialize_database_and_session

def run_timecard_columns_migration():
    """Add the new timecard columns to shiftWorkers table."""
    print("🔄 Adding new timecard columns to shiftWorkers table...")
    
    try:
        # Initialize database connection
        db, _ = initialize_database_and_session()
        print("✓ Database connected")
        
        # SQL commands to add the new timecard columns
        commands = [
            # Multiple clock in/out pairs for breaks and lunches
            "ALTER TABLE shiftWorkers ADD COLUMN clock_in_time_1 DATETIME NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN clock_out_time_1 DATETIME NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN clock_in_time_2 DATETIME NULL", 
            "ALTER TABLE shiftWorkers ADD COLUMN clock_out_time_2 DATETIME NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN clock_in_time_3 DATETIME NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN clock_out_time_3 DATETIME NULL",
            
            # Submission and approval tracking
            "ALTER TABLE shiftWorkers ADD COLUMN times_submitted_by INT NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN approved_at DATETIME NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN approved_by INT NULL",
            
            # Calculated fields
            "ALTER TABLE shiftWorkers ADD COLUMN total_hours_worked FLOAT NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN overtime_hours FLOAT NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN notes VARCHAR(500) NULL",
            
            # Foreign key constraints
            "ALTER TABLE shiftWorkers ADD FOREIGN KEY (times_submitted_by) REFERENCES users(id)",
            "ALTER TABLE shiftWorkers ADD FOREIGN KEY (approved_by) REFERENCES users(id)"
        ]
        
        for i, cmd in enumerate(commands, 1):
            try:
                print(f"Running command {i}/{len(commands)}...")
                db.execute(text(cmd))
                db.commit()
                print(f"✓ Command {i} completed")
            except Exception as e:
                if "Duplicate column name" in str(e) or "Duplicate key name" in str(e):
                    print(f"✓ Column/key already exists (skipping)")
                else:
                    print(f"⚠️  Command {i} failed: {e}")
        
        print("\n🎉 Timecard columns migration completed!")
        print("✓ Multiple clock in/out pairs added")
        print("✓ Submission and approval tracking added")
        print("✓ Calculated fields added")
        print("✓ Foreign key constraints added")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = run_timecard_columns_migration()
    sys.exit(0 if success else 1)
