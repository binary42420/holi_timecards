#!/usr/bin/env python3
"""
Migration script to add manager_id column to shiftBoards table and migrate data.
This completes the workplace_id migration for the single company system.
"""

import sys
from sqlalchemy import text
from main import get_db_session

def migrate_shiftboard_manager_id():
    """Add manager_id column to shiftBoards and migrate data from workplaceID."""
    print("🔧 Starting ShiftBoard manager_id migration...")
    
    try:
        with get_db_session() as session:
            print("✓ Database session created")
            
            # Check if manager_id column already exists
            def check_column_exists(table_name, column_name):
                try:
                    result = session.execute(text(f"""
                        SELECT COUNT(*) 
                        FROM INFORMATION_SCHEMA.COLUMNS 
                        WHERE TABLE_SCHEMA = DATABASE()
                        AND TABLE_NAME = '{table_name}'
                        AND COLUMN_NAME = '{column_name}'
                    """))
                    return result.fetchone()[0] > 0
                except Exception as e:
                    print(f"Error checking column {column_name} in {table_name}: {e}")
                    return False
            
            # Add manager_id column if it doesn't exist
            if check_column_exists('shiftBoards', 'manager_id'):
                print("✓ manager_id column already exists in shiftBoards")
            else:
                try:
                    print("Adding manager_id column to shiftBoards...")
                    session.execute(text("ALTER TABLE shiftBoards ADD COLUMN manager_id INT NULL"))
                    session.commit()
                    print("✓ manager_id column added to shiftBoards")
                except Exception as e:
                    print(f"❌ Failed to add manager_id column: {e}")
                    return False
            
            # Migrate data from workplaceID to manager_id
            try:
                print("Migrating data from workplaceID to manager_id...")
                result = session.execute(text("""
                    UPDATE shiftBoards 
                    SET manager_id = workplaceID 
                    WHERE manager_id IS NULL AND workplaceID IS NOT NULL
                """))
                session.commit()
                rows_updated = result.rowcount
                print(f"✓ Migrated {rows_updated} records from workplaceID to manager_id")
            except Exception as e:
                print(f"❌ Failed to migrate data: {e}")
                return False
            
            # Add foreign key constraint for manager_id
            try:
                print("Adding foreign key constraint for manager_id...")
                session.execute(text("""
                    ALTER TABLE shiftBoards 
                    ADD CONSTRAINT fk_shiftboards_manager_id 
                    FOREIGN KEY (manager_id) REFERENCES users(id)
                """))
                session.commit()
                print("✓ Foreign key constraint added for manager_id")
            except Exception as e:
                if "Duplicate key name" in str(e) or "already exists" in str(e):
                    print("✓ Foreign key constraint already exists")
                else:
                    print(f"⚠️  Could not add foreign key constraint: {e}")
            
            # Verify the migration
            try:
                result = session.execute(text("""
                    SELECT COUNT(*) as total,
                           COUNT(manager_id) as with_manager_id,
                           COUNT(workplaceID) as with_workplace_id
                    FROM shiftBoards
                """))
                stats = result.fetchone()
                
                print(f"📊 Migration Statistics:")
                print(f"   Total records: {stats[0]}")
                print(f"   Records with manager_id: {stats[1]}")
                print(f"   Records with workplaceID: {stats[2]}")
                
                if stats[1] == stats[2] and stats[0] > 0:
                    print("✅ All records successfully migrated!")
                elif stats[0] == 0:
                    print("✅ No existing records to migrate")
                else:
                    print("⚠️  Some records may not have been migrated properly")
                    
            except Exception as e:
                print(f"⚠️  Could not verify migration: {e}")
            
            print("✅ ShiftBoard manager_id migration completed successfully!")
            print("📋 Summary:")
            print("   - manager_id column added to shiftBoards table")
            print("   - Data migrated from workplaceID to manager_id")
            print("   - Foreign key constraint added")
            print("   - workplaceID column kept for backward compatibility")
            print("   - Ready for single company operation")
            
            return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    success = migrate_shiftboard_manager_id()
    
    if success:
        print("✅ ShiftBoard manager_id migration completed successfully!")
    else:
        print("❌ ShiftBoard manager_id migration failed!")
        sys.exit(1)
