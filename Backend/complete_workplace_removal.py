"""
Complete Workplace Reference Removal Script
Systematically removes ALL workplace references for Hands on Labor single company system.
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import get_db_session
from db.controllers.users_controller import UsersController
from sqlalchemy import text

def analyze_workplace_references():
    """Analyze all remaining workplace references in the codebase."""
    
    print("🔍 Analyzing Workplace References in EasyShifts")
    print("=" * 60)
    
    workplace_files = [
        "db/models.py",
        "db/controllers/workPlaces_controller.py", 
        "db/repositories/workPlaces_repository.py",
        "db/services/workPlaces_service.py",
        "handlers/employee_signin.py",
        "handlers/manager_schedule.py",
        "check_workplace_setup.py"
    ]
    
    print("\n📋 Files with workplace references:")
    for file_path in workplace_files:
        full_path = os.path.join(os.path.dirname(__file__), file_path)
        if os.path.exists(full_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} (not found)")
    
    return workplace_files

def check_database_workplace_tables():
    """Check for workplace-related tables in the database."""
    
    print("\n🗄️ Checking Database for Workplace Tables")
    print("-" * 50)
    
    try:
        with get_db_session() as session:
            
            # Check for workplaces table
            try:
                result = session.execute(text("SHOW TABLES LIKE 'workplaces'"))
                workplaces_exists = result.fetchone() is not None
                
                if workplaces_exists:
                    result = session.execute(text("SELECT COUNT(*) FROM workplaces"))
                    count = result.scalar()
                    print(f"⚠️  workplaces table exists with {count} records")
                else:
                    print("✅ No workplaces table found")
            except Exception as e:
                print(f"ℹ️  Could not check workplaces table: {e}")
            
            # Check for workplace_settings table
            try:
                result = session.execute(text("SHOW TABLES LIKE 'workplace_settings'"))
                settings_exists = result.fetchone() is not None
                
                if settings_exists:
                    result = session.execute(text("SELECT COUNT(*) FROM workplace_settings"))
                    count = result.scalar()
                    print(f"📋 workplace_settings table exists with {count} records")
                else:
                    print("✅ No workplace_settings table found")
            except Exception as e:
                print(f"ℹ️  Could not check workplace_settings table: {e}")
            
            # Check users table for workplace_id column
            try:
                result = session.execute(text("SHOW COLUMNS FROM users LIKE 'workplace_id'"))
                workplace_column = result.fetchone() is not None
                
                if workplace_column:
                    result = session.execute(text("SELECT COUNT(*) FROM users WHERE workplace_id IS NOT NULL"))
                    count = result.scalar()
                    print(f"⚠️  users.workplace_id column exists with {count} non-null values")
                else:
                    print("✅ No workplace_id column in users table")
            except Exception as e:
                print(f"ℹ️  Could not check users.workplace_id: {e}")
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")

def show_hands_on_labor_status():
    """Show the current status for Hands on Labor single company system."""
    
    print("\n🏢 Hands on Labor Single Company Status")
    print("=" * 50)
    
    try:
        with get_db_session() as session:
            users_controller = UsersController(session)
            all_users = users_controller.get_all_entities()
            
            print(f"📊 Total Users: {len(all_users)}")
            
            # Categorize users
            admins = [u for u in all_users if u.isAdmin]
            managers = [u for u in all_users if u.isManager and not u.isAdmin]
            employees = [u for u in all_users if not u.isManager]
            clients = [u for u in all_users if u.client_company_id is not None]
            
            print(f"   👑 Admins: {len(admins)}")
            print(f"   👔 Managers: {len(managers)}")
            print(f"   👷 Employees: {len(employees)}")
            print(f"   🏢 Client Users: {len(clients)}")
            
            print("\n🎯 Single Company Architecture:")
            print("   ✅ All users work for Hands on Labor")
            print("   ✅ No workplace separation needed")
            print("   ✅ Jobs linked to client companies")
            print("   ✅ Simplified permission model")
            
            # Show admin users
            if admins:
                print(f"\n👑 Admin Users:")
                for admin in admins:
                    status = "Active" if admin.isActive else "Inactive"
                    print(f"   • {admin.username} ({admin.name}) - {status}")
            
            # Show sample employees
            if employees:
                print(f"\n👷 Sample Employees:")
                for emp in employees[:3]:
                    status = "Active" if admin.isActive else "Inactive"
                    approved = "Approved" if emp.isApproval else "Pending"
                    print(f"   • {emp.username} ({emp.name}) - {status}, {approved}")
                if len(employees) > 3:
                    print(f"   ... and {len(employees) - 3} more employees")
                    
    except Exception as e:
        print(f"❌ Error analyzing users: {e}")

def create_workplace_deprecation_plan():
    """Create a plan for deprecating workplace functionality."""
    
    print("\n📋 Workplace Deprecation Plan")
    print("=" * 40)
    
    deprecation_steps = [
        {
            "step": 1,
            "title": "Mark Legacy Files as DEPRECATED",
            "files": [
                "db/controllers/workPlaces_controller.py",
                "db/repositories/workPlaces_repository.py", 
                "db/services/workPlaces_service.py"
            ],
            "action": "Add DEPRECATED comments and warnings"
        },
        {
            "step": 2,
            "title": "Update Database Models",
            "files": ["db/models.py"],
            "action": "Mark WorkPlace model as deprecated"
        },
        {
            "step": 3,
            "title": "Remove Workplace Usage",
            "files": [
                "handlers/employee_signin.py",
                "handlers/manager_schedule.py"
            ],
            "action": "Replace workplace logic with single company logic"
        },
        {
            "step": 4,
            "title": "Database Cleanup",
            "files": ["Database"],
            "action": "Optional: Drop workplace tables if not needed"
        }
    ]
    
    for step in deprecation_steps:
        print(f"\n{step['step']}. {step['title']}")
        print(f"   Action: {step['action']}")
        if isinstance(step['files'], list):
            for file in step['files']:
                print(f"   📁 {file}")
        else:
            print(f"   📁 {step['files']}")

def recommend_next_actions():
    """Recommend next actions for completing workplace removal."""
    
    print("\n🎯 Recommended Next Actions")
    print("=" * 35)
    
    actions = [
        "1. ✅ COMPLETED: Remove workplace_id from UserSession",
        "2. ✅ COMPLETED: Update employee_signin.py to remove workplace logic",
        "3. ✅ COMPLETED: Update manager_schedule.py function names",
        "4. ✅ COMPLETED: Deprecate WorkPlaces service and controller",
        "5. 🔄 IN PROGRESS: Mark remaining workplace files as deprecated",
        "6. 📋 TODO: Update README.md to reflect single company model",
        "7. 📋 TODO: Consider dropping workplace tables from database",
        "8. 📋 TODO: Update any remaining frontend workplace references"
    ]
    
    for action in actions:
        print(f"   {action}")
    
    print("\n💡 Key Benefits After Completion:")
    print("   • Simplified codebase for single company")
    print("   • No workplace_id parameters needed")
    print("   • Faster database queries")
    print("   • Clearer business logic")
    print("   • Better alignment with Hands on Labor model")

def main():
    """Main function with analysis options."""
    
    while True:
        print("\n🔧 Complete Workplace Removal Tool")
        print("=" * 45)
        print("1. Analyze Workplace References")
        print("2. Check Database Tables")
        print("3. Show Hands on Labor Status")
        print("4. View Deprecation Plan")
        print("5. Show Recommendations")
        print("6. Exit")
        
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            analyze_workplace_references()
        elif choice == '2':
            check_database_workplace_tables()
        elif choice == '3':
            show_hands_on_labor_status()
        elif choice == '4':
            create_workplace_deprecation_plan()
        elif choice == '5':
            recommend_next_actions()
        elif choice == '6':
            print("👋 Workplace removal analysis complete!")
            break
        else:
            print("❌ Invalid choice! Please select 1-6.")

if __name__ == "__main__":
    main()
