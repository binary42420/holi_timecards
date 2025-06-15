#!/usr/bin/env python3
"""
Cleanup script to remove old and unnecessary files from the EasyShifts codebase
including all build artifacts
"""

import os
import shutil
from pathlib import Path
import re
from datetime import datetime

def create_backup(files_to_backup):
    """Create backups of files before removal"""
    backup_dir = Path(f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_dir.mkdir(exist_ok=True)
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = backup_dir / Path(file_path).name
            shutil.copy2(file_path, backup_path)
            print(f"✅ Backed up {file_path} to {backup_path}")
    
    return backup_dir

def cleanup_backend():
    """Clean up backend directory"""
    print("\n🧹 Cleaning up Backend directory")
    print("=" * 30)
    
    # Patterns for files to remove
    patterns_to_remove = [
        r'.*\.backup_\d+',
        r'.*\.specific_fix_\d+',
        r'.*_backup_\d+',
        r'backups_\d+',
        r'__pycache__',
        r'.*\.pyc$',
        r'.*\.pyo$',
        r'.*\.pyd$',
        r'.*\.log$',
        r'.*\.tmp$'
    ]
    
    # Build-related directories to remove
    build_dirs = [
        'build',
        'dist',
        '*.egg-info',
        '.pytest_cache',
        '.coverage',
        'htmlcov'
    ]
    
    backend_dir = Path("Backend")
    removed_count = 0
    
    # Remove pattern-matched files
    for pattern in patterns_to_remove:
        for path in backend_dir.glob("**/*"):
            if re.match(pattern, str(path)):
                if path.is_file():
                    path.unlink()
                    print(f"   🗑️  Removed file: {path}")
                    removed_count += 1
                elif path.is_dir():
                    shutil.rmtree(path)
                    print(f"   🗑️  Removed directory: {path}")
                    removed_count += 1
    
    # Remove build directories
    for build_dir in build_dirs:
        for path in backend_dir.glob(f"**/{build_dir}"):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   🗑️  Removed build directory: {path}")
                removed_count += 1
            elif path.is_file():
                path.unlink()
                print(f"   🗑️  Removed build file: {path}")
                removed_count += 1
    
    print(f"   ✅ Removed {removed_count} items from Backend")

def cleanup_frontend():
    """Clean up frontend directory"""
    print("\n🧹 Cleaning up Frontend directory")
    print("=" * 30)
    
    frontend_dir = Path("app")
    
    # Directories to clean
    dirs_to_clean = [
        "build",
        "dist",
        "coverage",
        ".cache",
        ".eslintcache",
        "node_modules/.cache",
        ".parcel-cache",
        ".next",
        "out",
        ".nuxt",
        ".output",
        ".vite",
        ".webpack"
    ]
    
    # Files to clean
    file_patterns = [
        "*.log",
        "npm-debug.log*",
        "yarn-debug.log*",
        "yarn-error.log*",
        "*.tmp",
        ".DS_Store",
        "Thumbs.db"
    ]
    
    removed_count = 0
    
    # Clean directories
    for dir_name in dirs_to_clean:
        for dir_path in frontend_dir.glob(f"**/{dir_name}"):
            if dir_path.is_dir():
                shutil.rmtree(dir_path)
                print(f"   🗑️  Removed directory: {dir_path}")
                removed_count += 1
    
    # Clean files
    for pattern in file_patterns:
        for file_path in frontend_dir.glob(f"**/{pattern}"):
            if file_path.is_file():
                file_path.unlink()
                print(f"   🗑️  Removed file: {file_path}")
                removed_count += 1
    
    print(f"   ✅ Removed {removed_count} items from Frontend")

def cleanup_docker_artifacts():
    """Clean up Docker build artifacts"""
    print("\n🧹 Cleaning up Docker artifacts")
    print("=" * 30)
    
    # Look for Docker-related build artifacts
    docker_artifacts = [
        ".docker",
        "docker-compose.override.yml"
    ]
    
    removed_count = 0
    root_dir = Path(".")
    
    for artifact in docker_artifacts:
        for path in root_dir.glob(f"**/{artifact}"):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   🗑️  Removed Docker directory: {path}")
                removed_count += 1
            elif path.is_file():
                path.unlink()
                print(f"   🗑️  Removed Docker file: {path}")
                removed_count += 1
    
    print(f"   ✅ Removed {removed_count} Docker artifacts")

def main():
    """Run cleanup operations"""
    print("🚀 EasyShifts Codebase Cleanup")
    print("=" * 40)
    
    # Create backups of critical files
    critical_files = [
        'Backend/handlers/enhanced_schedule_handlers.py',
        'Backend/handlers/manager_schedule.py',
        'Backend/handlers/timesheet_management_handlers.py'
    ]
    
    backup_dir = create_backup(critical_files)
    print(f"📦 Backups created in: {backup_dir}")
    
    # Run cleanup operations
    cleanup_backend()
    cleanup_frontend()
    cleanup_docker_artifacts()
    
    print("\n🎉 Codebase cleanup completed!")
    print("   All build artifacts and temporary files have been removed.")

if __name__ == "__main__":
    main()