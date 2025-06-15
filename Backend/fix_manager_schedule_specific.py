#!/usr/bin/env python3
"""
Specific fix for manager_schedule.py database session issues
"""

import os
import re
import shutil
from datetime import datetime

def fix_manager_schedule_db_sessions():
    """Fix all database session issues in manager_schedule.py"""
    
    file_path = "handlers/manager_schedule.py"
    
    if not os.path.exists(file_path):
        print(f"❌ {file_path} not found")
        return False
    
    print(f"🔧 Fixing all database sessions in {file_path}")
    
    # Create backup
    backup_path = f"{file_path}.specific_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(file_path, backup_path)
    print(f"   📦 Backup: {backup_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Ensure proper import
        if 'from main import db' in content:
            content = content.replace('from main import db', 'from main import get_db_session')
        elif 'get_db_session' not in content and 'from main import' in content:
            content = re.sub(
                r'(from main import[^\n]*)',
                r'\1, get_db_session',
                content
            )
        
        # Fix each function individually with proper context management
        
        # Function 1: handle_get_board
        content = re.sub(
            r'def handle_get_board\(user_session: UserSession\) -> dict:\s*\n\s*# Get the last shift board\s*\n\s*shift_board_controller = ShiftBoardController\(db\)',
            '''def handle_get_board(user_session: UserSession) -> dict:
    # Get the last shift board
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)''',
            content,
            flags=re.MULTILINE
        )
        
        # Function 2: handle_get_start_date
        content = re.sub(
            r'def handle_get_start_date\(user_session: UserSession\) -> dict:\s*\n\s*# Get the last shift board\s*\n\s*shift_board_controller = ShiftBoardController\(db\)',
            '''def handle_get_start_date(user_session: UserSession) -> dict:
    # Get the last shift board
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)''',
            content,
            flags=re.MULTILINE
        )
        
        # Function 3: handle_update_board
        content = re.sub(
            r'(\s+)# Update the shift board\s*\n\s*shift_board_controller = ShiftBoardController\(db\)',
            r'\1# Update the shift board\n\1with get_db_session() as session:\n\1    shift_board_controller = ShiftBoardController(session)',
            content
        )
        
        # Function 4: handle_reset_board
        content = re.sub(
            r'def handle_reset_board\(user_session: UserSession\) -> ShiftBoard:\s*\n\s*# Get the last shift board.*?\n\s*shift_board_controller = ShiftBoardController\(db\)',
            '''def handle_reset_board(user_session: UserSession) -> ShiftBoard:
    # Get the last shift board (Assuming it is the last shift board, the others are published)
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)''',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Function 5: handle_publish_board
        content = re.sub(
            r'def handle_publish_board\(user_session: UserSession\) -> bool:\s*\n\s*# Publish the shift board.*?\n\s*shift_board_controller = ShiftBoardController\(db\)',
            '''def handle_publish_board(user_session: UserSession) -> bool:
    # Publish the shift board (Assuming it is the last shift board, the others are published)
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)''',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Function 6: handle_unpublish_board
        content = re.sub(
            r'def handle_unpublish_board\(user_session: UserSession\) -> bool:\s*\n\s*# Unpublish the shift board.*?\n\s*shift_board_controller = ShiftBoardController\(db\)',
            '''def handle_unpublish_board(user_session: UserSession) -> bool:
    # Unpublish the shift board (Assuming it is the last shift board, the others are published)
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)''',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Function 7: handle_get_board_content
        content = re.sub(
            r'def handle_get_board_content\(user_session: UserSession\) -> dict:\s*\n\s*# Get the last shift board.*?\n\s*shift_board_controller = ShiftBoardController\(db\)',
            '''def handle_get_board_content(user_session: UserSession) -> dict:
    # Get the last shift board (Assuming it is the last shift board, the others are published)
    with get_db_session() as session:
        shift_board_controller = ShiftBoardController(session)''',
            content,
            flags=re.MULTILINE | re.DOTALL
        )
        
        # Generic fix for remaining controller instantiations
        # This will catch any remaining patterns
        content = re.sub(
            r'(\s+)(\w+_controller) = (\w+Controller)\(db\)',
            r'\1with get_db_session() as session:\n\1    \2 = \3(session)',
            content
        )
        
        # Fix direct controller usage patterns
        content = re.sub(
            r'(\s+)(\w+Controller)\(db\)\.(\w+)\(',
            r'\1with get_db_session() as session:\n\1    result = \2(session).\3(',
            content
        )
        
        # Fix any remaining standalone controller instantiations
        content = re.sub(
            r'(\s*)(\w+_controller) = (\w+Controller)\(db\)',
            r'\1with get_db_session() as session:\n\1    \2 = \3(session)',
            content
        )
        
        # Write the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("   ✅ All database sessions fixed")
        
        # Validate the fix
        with open(file_path, 'r', encoding='utf-8') as f:
            fixed_content = f.read()
        
        remaining_db_usage = len(re.findall(r'controller.*\(db\)', fixed_content))
        context_managers = len(re.findall(r'with get_db_session\(\) as session:', fixed_content))
        
        print(f"   📊 Remaining db usage: {remaining_db_usage}")
        print(f"   📊 Context managers: {context_managers}")
        
        if remaining_db_usage == 0:
            print("   🎉 All database sessions properly migrated!")
            return True
        else:
            print("   ⚠️  Some database sessions still need manual review")
            return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        # Restore backup
        shutil.copy2(backup_path, file_path)
        return False

def main():
    """Run the specific fix for manager_schedule.py"""
    print("🚀 Manager Schedule Database Session Fix")
    print("=" * 45)
    
    success = fix_manager_schedule_db_sessions()
    
    if success:
        print("\n✅ manager_schedule.py successfully migrated!")
        print("\n🧪 Next steps:")
        print("1. Test the application: python test_critical_functionality.py")
        print("2. Run full migration: python migrate_database_sessions.py")
    else:
        print("\n❌ Migration failed - check backup and try manual fixes")

if __name__ == "__main__":
    main()
