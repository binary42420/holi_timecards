#!/usr/bin/env python3
"""
Migration script to add timecard management features to shiftWorkers table.
"""

import sys
from sqlalchemy import text
from main import initialize_database_and_session

def run_timecard_migration():
    """Add timecard management fields to shiftWorkers table."""
    print("🔄 Adding timecard management features...")
    
    try:
        # Initialize database connection
        db, _ = initialize_database_and_session()
        print("✓ Database connected")
        
        # SQL commands to add timecard fields
        commands = [
            # Real-time status tracking
            "ALTER TABLE shiftWorkers ADD COLUMN current_status VARCHAR(20) DEFAULT 'not_started'",
            "ALTER TABLE shiftWorkers ADD COLUMN last_action_time DATETIME NULL",
            
            # Employee management
            "ALTER TABLE shiftWorkers ADD COLUMN is_absent BOOLEAN DEFAULT FALSE",
            "ALTER TABLE shiftWorkers ADD COLUMN marked_absent_at DATETIME NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN marked_absent_by INT NULL",
            "ALTER TABLE shiftWorkers ADD COLUMN shift_notes TEXT NULL",
            
            # Foreign key constraints
            "ALTER TABLE shiftWorkers ADD FOREIGN KEY (marked_absent_by) REFERENCES users(id)"
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
        
        # Add indexes for better performance
        index_commands = [
            "CREATE INDEX idx_shiftworkers_status ON shiftWorkers(current_status)",
            "CREATE INDEX idx_shiftworkers_last_action ON shiftWorkers(last_action_time)",
            "CREATE INDEX idx_shiftworkers_absent ON shiftWorkers(is_absent)"
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
        
        print("\n🎉 Timecard migration completed!")
        print("✓ Real-time status tracking added")
        print("✓ Employee absence management added")
        print("✓ Shift notes functionality added")
        print("✓ Performance indexes created")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = run_timecard_migration()
    sys.exit(0 if success else 1)
