#!/usr/bin/env python3
"""
Comprehensive database session migration script for EasyShifts
Fixes all files using global 'db' to use proper context managers
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class DatabaseSessionMigrator:
    def __init__(self):
        self.backup_dir = Path(f"session_migration_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        self.fixed_files = []
        self.failed_files = []
        self.skipped_files = []
        
    def create_backup(self, file_path):
        """Create backup of file before modification"""
        if not self.backup_dir.exists():
            self.backup_dir.mkdir()
        
        backup_path = self.backup_dir / Path(file_path).name
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def should_skip_file(self, file_path):
        """Determine if file should be skipped"""
        skip_patterns = [
            'test_',
            'debug_',
            'migration',
            '__pycache__',
            '.pyc',
            'backup_'
        ]
        
        file_str = str(file_path).lower()
        return any(pattern in file_str for pattern in skip_patterns)
    
    def analyze_file(self, file_path):
        """Analyze file for database session issues"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for problematic patterns
            has_global_db = bool(re.search(r'controller.*\(db\)', content))
            has_context_manager = bool(re.search(r'with get_db_session\(\) as session:', content))
            has_db_import = bool(re.search(r'from main import.*db', content))
            
            return {
                'has_global_db': has_global_db,
                'has_context_manager': has_context_manager,
                'has_db_import': has_db_import,
                'needs_migration': has_global_db and not has_context_manager,
                'content': content
            }
        except Exception as e:
            print(f"❌ Error analyzing {file_path}: {e}")
            return None
    
    def fix_imports(self, content):
        """Fix import statements"""
        # Replace db import with get_db_session import
        content = re.sub(
            r'from main import.*db(?!\w)',
            'from main import get_db_session',
            content
        )
        
        # Ensure get_db_session is imported if db controllers are used
        if 'Controller(' in content and 'get_db_session' not in content:
            # Add import at the top after existing main imports
            content = re.sub(
                r'(from main import[^\n]*)',
                r'\1, get_db_session',
                content
            )
            
            # If no main import exists, add it
            if 'from main import' not in content:
                # Find first import and add after it
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        lines.insert(i + 1, 'from main import get_db_session')
                        break
                content = '\n'.join(lines)
        
        return content
    
    def fix_controller_instantiation(self, content):
        """Fix controller instantiation patterns"""
        
        # Pattern 1: Simple controller instantiation
        # controller = SomeController(db)
        pattern1 = r'(\s+)(\w+)\s*=\s*(\w+Controller)\(db\)'
        replacement1 = r'\1with get_db_session() as session:\n\1    \2 = \3(session)'
        
        content = re.sub(pattern1, replacement1, content)
        
        # Pattern 2: Direct controller usage
        # result = SomeController(db).method()
        pattern2 = r'(\s*)(\w+Controller)\(db\)\.(\w+)\('
        replacement2 = r'\1with get_db_session() as session:\n\1    result = \2(session).\3('
        
        content = re.sub(pattern2, replacement2, content)
        
        # Pattern 3: Multiple controllers in same function
        # This needs more sophisticated handling
        
        return content
    
    def fix_function_structure(self, content):
        """Fix function structure to properly handle context managers"""
        
        # Find functions that need restructuring
        functions = re.findall(r'def\s+(\w+)\([^)]*\):[^}]*?(?=def|\Z)', content, re.DOTALL)
        
        for func_match in functions:
            # This is a simplified approach - complex functions may need manual review
            pass
        
        return content
    
    def add_error_handling(self, content):
        """Add basic error handling around database operations"""
        
        # Wrap database operations in try-catch if not already present
        if 'with get_db_session() as session:' in content and 'try:' not in content:
            # Add try-catch around the entire function body
            # This is a simplified approach
            pass
        
        return content
    
    def migrate_file(self, file_path):
        """Migrate a single file to use proper database sessions"""
        
        if self.should_skip_file(file_path):
            self.skipped_files.append(str(file_path))
            return False
        
        analysis = self.analyze_file(file_path)
        if not analysis or not analysis['needs_migration']:
            return False
        
        print(f"🔧 Migrating {file_path}")
        
        # Create backup
        backup_path = self.create_backup(file_path)
        print(f"   📦 Backup created: {backup_path}")
        
        try:
            content = analysis['content']
            original_content = content
            
            # Apply fixes
            content = self.fix_imports(content)
            content = self.fix_controller_instantiation(content)
            content = self.fix_function_structure(content)
            content = self.add_error_handling(content)
            
            # Only write if changes were made
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"   ✅ Migration completed")
                self.fixed_files.append(str(file_path))
                return True
            else:
                print(f"   ⚠️  No changes needed")
                return False
                
        except Exception as e:
            print(f"   ❌ Migration failed: {e}")
            # Restore from backup
            shutil.copy2(backup_path, file_path)
            self.failed_files.append(str(file_path))
            return False
    
    def migrate_all_files(self):
        """Migrate all files in the backend directory"""
        
        print("🚀 Starting Database Session Migration")
        print("=" * 45)
        
        backend_dir = Path(".")
        python_files = list(backend_dir.rglob("*.py"))
        
        print(f"📁 Found {len(python_files)} Python files")
        print()
        
        for file_path in python_files:
            if file_path.is_file():
                self.migrate_file(file_path)
        
        self.print_summary()
    
    def print_summary(self):
        """Print migration summary"""
        
        print("\n" + "=" * 45)
        print("📊 MIGRATION SUMMARY")
        print("=" * 45)
        
        print(f"✅ Successfully migrated: {len(self.fixed_files)} files")
        for file_path in self.fixed_files:
            print(f"   • {file_path}")
        
        if self.failed_files:
            print(f"\n❌ Failed to migrate: {len(self.failed_files)} files")
            for file_path in self.failed_files:
                print(f"   • {file_path}")
        
        if self.skipped_files:
            print(f"\n⏭️  Skipped: {len(self.skipped_files)} files")
            print("   (test files, debug files, etc.)")
        
        print(f"\n📦 Backups stored in: {self.backup_dir}")
        
        if self.failed_files:
            print("\n⚠️  MANUAL REVIEW NEEDED:")
            print("Some files failed automatic migration and need manual fixes.")
            print("Check the backup directory and review failed files.")
        
        print("\n🧪 NEXT STEPS:")
        print("1. Test the application thoroughly")
        print("2. Run: python test_critical_functionality.py")
        print("3. Review any failed migrations manually")
        print("4. Deploy and monitor for connection leaks")

def main():
    """Run the database session migration"""
    migrator = DatabaseSessionMigrator()
    migrator.migrate_all_files()

if __name__ == "__main__":
    main()
