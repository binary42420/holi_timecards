#!/usr/bin/env python3
"""
Script to identify and fix remaining database session management issues
"""

import os
import re
from pathlib import Path

def find_db_session_issues():
    """Find files that still use global db instead of context managers"""
    backend_dir = Path(".")
    issues = []
    
    # Patterns to look for
    global_db_pattern = r'(?:from main import db|global db|db\s*=.*get_db|controller.*\(db\))'
    context_manager_pattern = r'with get_db_session\(\) as session:'
    
    for py_file in backend_dir.rglob("*.py"):
        if "migrations" in str(py_file) or "__pycache__" in str(py_file):
            continue
            
        try:
            content = py_file.read_text(encoding='utf-8')
            
            # Check for global db usage
            global_db_matches = re.findall(global_db_pattern, content, re.IGNORECASE)
            has_context_manager = bool(re.search(context_manager_pattern, content))
            
            if global_db_matches and not has_context_manager:
                issues.append({
                    'file': str(py_file),
                    'issues': global_db_matches,
                    'needs_migration': True
                })
                
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
    
    return issues

def generate_migration_report():
    """Generate a report of files needing database session migration"""
    issues = find_db_session_issues()
    
    print("🔍 Database Session Management Analysis")
    print("=" * 50)
    
    if not issues:
        print("✅ All files are using proper database session management!")
        return
    
    print(f"❌ Found {len(issues)} files with database session issues:")
    print()
    
    for issue in issues:
        print(f"📁 {issue['file']}")
        for problem in issue['issues']:
            print(f"   ⚠️  {problem}")
        print()
    
    print("🔧 Recommended Actions:")
    print("1. Replace 'from main import db' with 'from main import get_db_session'")
    print("2. Wrap database operations in 'with get_db_session() as session:'")
    print("3. Pass 'session' to controllers instead of 'db'")
    print("4. Test all affected endpoints after migration")

def check_error_handling():
    """Check for missing error handling in critical files"""
    critical_files = [
        "handlers/login.py",
        "handlers/manager_schedule.py", 
        "handlers/shift_management_handlers.py",
        "Server.py"
    ]
    
    print("\n🛡️ Error Handling Analysis")
    print("=" * 30)
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            try_catch_count = len(re.findall(r'try:', content))
            except_count = len(re.findall(r'except', content))
            function_count = len(re.findall(r'def\s+\w+', content))
            
            coverage = (try_catch_count / function_count * 100) if function_count > 0 else 0
            
            print(f"📁 {file_path}")
            print(f"   Functions: {function_count}")
            print(f"   Try blocks: {try_catch_count}")
            print(f"   Error coverage: {coverage:.1f}%")
            
            if coverage < 50:
                print(f"   ⚠️  Low error handling coverage!")
            else:
                print(f"   ✅ Good error handling coverage")
            print()

def check_security_issues():
    """Check for potential security issues"""
    print("\n🔒 Security Analysis")
    print("=" * 20)
    
    security_checks = [
        {
            'name': 'Password Storage',
            'pattern': r'password.*=.*["\'][^$]',
            'description': 'Plain text passwords found'
        },
        {
            'name': 'SQL Injection Risk',
            'pattern': r'\.execute\(["\'].*%.*["\']',
            'description': 'Potential SQL injection with string formatting'
        },
        {
            'name': 'Hardcoded Secrets',
            'pattern': r'(?:secret|key|token).*=.*["\'][^{]',
            'description': 'Hardcoded secrets found'
        }
    ]
    
    backend_dir = Path(".")
    
    for check in security_checks:
        print(f"🔍 Checking: {check['name']}")
        found_issues = False
        
        for py_file in backend_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
                
            try:
                content = py_file.read_text(encoding='utf-8')
                matches = re.findall(check['pattern'], content, re.IGNORECASE)
                
                if matches:
                    if not found_issues:
                        print(f"   ⚠️  {check['description']}")
                        found_issues = True
                    print(f"      📁 {py_file}: {len(matches)} instances")
                    
            except Exception as e:
                continue
        
        if not found_issues:
            print(f"   ✅ No issues found")
        print()

if __name__ == "__main__":
    print("🚀 EasyShifts Backend Analysis")
    print("=" * 35)
    
    generate_migration_report()
    check_error_handling()
    check_security_issues()
    
    print("\n📋 Summary Recommendations:")
    print("1. Complete database session migration for remaining files")
    print("2. Add comprehensive error handling to low-coverage functions")
    print("3. Review and fix any security issues found")
    print("4. Add unit tests for critical functions")
    print("5. Implement health checks for all external dependencies")
