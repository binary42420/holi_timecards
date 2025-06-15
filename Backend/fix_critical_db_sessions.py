#!/usr/bin/env python3
"""
Targeted fixes for critical database session issues
Focuses on the most important handler files
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Create backup of file"""
    backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    if os.path.exists(file_path):
        shutil.copy2(file_path, backup_path)
        return backup_path
    return None

def fix_manager_schedule():
    """Fix handlers/manager_schedule.py"""
    file_path = "handlers/manager_schedule.py"
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found")
        return False
    
    print(f"🔧 Fixing {file_path}")
    
    # Create backup
    backup_path = backup_file(file_path)
    print(f"   📦 Backup: {backup_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already fixed
        if 'with get_db_session() as session:' in content:
            print("   ✅ Already using context managers")
            return True
        
        # Fix imports
        if 'from main import db' in content:
            content = content.replace('from main import db', 'from main import get_db_session')
        elif 'get_db_session' not in content:
            # Add import
            content = re.sub(
                r'(from main import[^\n]*)',
                r'\1, get_db_session',
                content
            )
        
        # Fix specific patterns in manager_schedule.py
        
        # Pattern 1: handle_get_schedule_data
        old_pattern1 = r'''def handle_get_schedule_data\(data, user_session\):
    """Get schedule data for the manager interface"""
    try:
        shifts_controller = ShiftsController\(db\)'''
        
        new_pattern1 = '''def handle_get_schedule_data(data, user_session):
    """Get schedule data for the manager interface"""
    try:
        with get_db_session() as session:
            shifts_controller = ShiftsController(session)'''
        
        content = re.sub(old_pattern1, new_pattern1, content, flags=re.MULTILINE)
        
        # Pattern 2: handle_create_shift
        old_pattern2 = r'''def handle_create_shift\(data, user_session\):
    """Create a new shift"""
    try:
        shifts_controller = ShiftsController\(db\)'''
        
        new_pattern2 = '''def handle_create_shift(data, user_session):
    """Create a new shift"""
    try:
        with get_db_session() as session:
            shifts_controller = ShiftsController(session)'''
        
        content = re.sub(old_pattern2, new_pattern2, content, flags=re.MULTILINE)
        
        # Pattern 3: handle_update_shift
        old_pattern3 = r'''def handle_update_shift\(data, user_session\):
    """Update an existing shift"""
    try:
        shifts_controller = ShiftsController\(db\)'''
        
        new_pattern3 = '''def handle_update_shift(data, user_session):
    """Update an existing shift"""
    try:
        with get_db_session() as session:
            shifts_controller = ShiftsController(session)'''
        
        content = re.sub(old_pattern3, new_pattern3, content, flags=re.MULTILINE)
        
        # Pattern 4: handle_delete_shift
        old_pattern4 = r'''def handle_delete_shift\(data, user_session\):
    """Delete a shift"""
    try:
        shifts_controller = ShiftsController\(db\)'''
        
        new_pattern4 = '''def handle_delete_shift(data, user_session):
    """Delete a shift"""
    try:
        with get_db_session() as session:
            shifts_controller = ShiftsController(session)'''
        
        content = re.sub(old_pattern4, new_pattern4, content, flags=re.MULTILINE)
        
        # Generic pattern for any remaining controller instantiations
        content = re.sub(
            r'(\s+)(\w+_controller)\s*=\s*(\w+Controller)\(db\)',
            r'\1with get_db_session() as session:\n\1    \2 = \3(session)',
            content
        )
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Fixed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        # Restore backup
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
        return False

def fix_timesheet_handlers():
    """Fix handlers/timesheet_management_handlers.py"""
    file_path = "handlers/timesheet_management_handlers.py"
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found")
        return False
    
    print(f"🔧 Fixing {file_path}")
    
    backup_path = backup_file(file_path)
    print(f"   📦 Backup: {backup_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'with get_db_session() as session:' in content:
            print("   ✅ Already using context managers")
            return True
        
        # Fix imports
        if 'from main import db' in content:
            content = content.replace('from main import db', 'from main import get_db_session')
        elif 'get_db_session' not in content:
            content = re.sub(
                r'(from main import[^\n]*)',
                r'\1, get_db_session',
                content
            )
        
        # Fix controller instantiations
        content = re.sub(
            r'(\s+)(\w+_controller)\s*=\s*(\w+Controller)\(db\)',
            r'\1with get_db_session() as session:\n\1    \2 = \3(session)',
            content
        )
        
        # Fix direct controller usage
        content = re.sub(
            r'(\s+)(\w+Controller)\(db\)\.(\w+)\(',
            r'\1with get_db_session() as session:\n\1    result = \2(session).\3(',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Fixed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
        return False

def fix_client_directory_handlers():
    """Fix handlers/client_directory_handlers.py"""
    file_path = "handlers/client_directory_handlers.py"
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found")
        return False
    
    print(f"🔧 Fixing {file_path}")
    
    backup_path = backup_file(file_path)
    print(f"   📦 Backup: {backup_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'with get_db_session() as session:' in content:
            print("   ✅ Already using context managers")
            return True
        
        # Fix imports
        if 'from main import db' in content:
            content = content.replace('from main import db', 'from main import get_db_session')
        elif 'get_db_session' not in content:
            content = re.sub(
                r'(from main import[^\n]*)',
                r'\1, get_db_session',
                content
            )
        
        # Fix controller instantiations
        content = re.sub(
            r'(\s+)(\w+_controller)\s*=\s*(\w+Controller)\(db\)',
            r'\1with get_db_session() as session:\n\1    \2 = \3(session)',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Fixed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
        return False

def fix_enhanced_schedule_handlers():
    """Fix handlers/enhanced_schedule_handlers.py"""
    file_path = "handlers/enhanced_schedule_handlers.py"
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found")
        return False
    
    print(f"🔧 Fixing {file_path}")
    
    backup_path = backup_file(file_path)
    print(f"   📦 Backup: {backup_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'with get_db_session() as session:' in content:
            print("   ✅ Already using context managers")
            return True
        
        # Fix imports
        if 'from main import db' in content:
            content = content.replace('from main import db', 'from main import get_db_session')
        elif 'get_db_session' not in content:
            content = re.sub(
                r'(from main import[^\n]*)',
                r'\1, get_db_session',
                content
            )
        
        # Fix controller instantiations
        content = re.sub(
            r'(\s+)(\w+_controller)\s*=\s*(\w+Controller)\(db\)',
            r'\1with get_db_session() as session:\n\1    \2 = \3(session)',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ Fixed successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
        return False

def validate_fixes():
    """Validate that fixes were applied correctly"""
    print("\n🧪 Validating fixes...")
    
    critical_files = [
        "handlers/manager_schedule.py",
        "handlers/timesheet_management_handlers.py", 
        "handlers/client_directory_handlers.py",
        "handlers/enhanced_schedule_handlers.py"
    ]
    
    all_good = True
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_context_manager = 'with get_db_session() as session:' in content
            has_global_db = bool(re.search(r'controller.*\(db\)', content))
            
            if has_context_manager and not has_global_db:
                print(f"   ✅ {file_path} - Properly migrated")
            elif has_context_manager and has_global_db:
                print(f"   ⚠️  {file_path} - Partially migrated (mixed patterns)")
                all_good = False
            else:
                print(f"   ❌ {file_path} - Still needs migration")
                all_good = False
        else:
            print(f"   ❓ {file_path} - File not found")
    
    return all_good

def main():
    """Run critical database session fixes"""
    print("🚀 Critical Database Session Fixes")
    print("=" * 40)
    
    # Fix critical handler files
    fixes = [
        fix_manager_schedule,
        fix_timesheet_handlers,
        fix_client_directory_handlers,
        fix_enhanced_schedule_handlers
    ]
    
    success_count = 0
    for fix_func in fixes:
        if fix_func():
            success_count += 1
        print()
    
    # Validate fixes
    all_validated = validate_fixes()
    
    print("\n" + "=" * 40)
    print("📊 SUMMARY")
    print("=" * 40)
    print(f"✅ Successfully fixed: {success_count}/{len(fixes)} files")
    
    if all_validated:
        print("🎉 All critical files properly migrated!")
    else:
        print("⚠️  Some files need manual review")
    
    print("\n🧪 NEXT STEPS:")
    print("1. Test the application: python test_critical_functionality.py")
    print("2. Deploy and test in production")
    print("3. Monitor for database connection leaks")
    print("4. Run full migration: python migrate_database_sessions.py")

if __name__ == "__main__":
    main()
