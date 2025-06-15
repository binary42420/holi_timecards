#!/usr/bin/env python3
"""
Script to replace all remaining user_session references with current_session in Server.py
"""

import re

def fix_user_session_references():
    """Replace user_session with current_session in Server.py"""
    
    file_path = "Server.py"
    
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count original occurrences
        original_count = content.count('user_session')
        print(f"Found {original_count} occurrences of 'user_session'")
        
        # Replace patterns - be more specific to avoid breaking legitimate uses
        replacements = [
            # Replace user_session in function parameters and checks
            (r'return handle_\w+\(data, user_session\)', lambda m: m.group(0).replace('user_session', 'current_session')),
            (r'if not user_session:', 'if not current_session:'),
            (r'manager_schedule\.handle_save_preferences\(user_session\.get_id', 'manager_schedule.handle_save_preferences(current_session.get_id'),
            (r'manager_schedule\.open_requests_windows\(user_session\.get_id', 'manager_schedule.open_requests_windows(current_session.get_id'),
            (r'manager_schedule\.handle_get_board\(user_session\)', 'manager_schedule.handle_get_board(current_session)'),
            # Replace user_session in handler calls but preserve 'user_session' in response data keys
            (r'(?<![\'"]\w*)user_session(?!\w*[\'"])', 'current_session'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Count remaining occurrences
        remaining_count = content.count('user_session')
        print(f"Remaining {remaining_count} occurrences of 'user_session'")
        print(f"Replaced {original_count - remaining_count} occurrences")
        
        # Write the file back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Successfully updated Server.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_user_session_references()
