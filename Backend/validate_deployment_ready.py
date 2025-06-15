#!/usr/bin/env python3
"""
EasyShifts Deployment Readiness Validator
Checks if the application is ready for Cloud Run deployment
"""

import os
import subprocess
import json
from pathlib import Path

def check_command(command, description):
    """Check if a command exists and works"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0] if result.stdout else "unknown"
            print(f"   ✅ {description}: {version}")
            return True
        else:
            print(f"   ❌ {description}: Not found or not working")
            return False
    except Exception as e:
        print(f"   ❌ {description}: Error - {e}")
        return False

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if Path(file_path).exists():
        print(f"   ✅ {description}: Found")
        return True
    else:
        print(f"   ❌ {description}: Missing")
        return False

def check_docker_running():
    """Check if Docker daemon is running"""
    try:
        result = subprocess.run("docker ps", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("   ✅ Docker daemon: Running")
            return True
        else:
            print("   ❌ Docker daemon: Not running")
            return False
    except Exception:
        print("   ❌ Docker daemon: Not accessible")
        return False

def check_gcloud_auth():
    """Check Google Cloud authentication"""
    try:
        result = subprocess.run("gcloud auth list --filter=status:ACTIVE --format='value(account)'", 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            account = result.stdout.strip()
            print(f"   ✅ GCloud auth: {account}")
            return True
        else:
            print("   ❌ GCloud auth: Not authenticated")
            return False
    except Exception:
        print("   ❌ GCloud auth: Error checking")
        return False

def check_gcloud_project():
    """Check Google Cloud project configuration"""
    try:
        result = subprocess.run("gcloud config get-value project", 
                              shell=True, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            project = result.stdout.strip()
            print(f"   ✅ GCloud project: {project}")
            return True, project
        else:
            print("   ❌ GCloud project: Not set")
            return False, None
    except Exception:
        print("   ❌ GCloud project: Error checking")
        return False, None

def validate_backend():
    """Validate backend readiness"""
    print("\n🔧 Backend Validation")
    print("-" * 20)
    
    issues = []
    
    # Check Dockerfile
    if not check_file_exists("Backend/Dockerfile", "Backend Dockerfile"):
        issues.append("Backend Dockerfile missing")
    
    # Check main files
    if not check_file_exists("Backend/Server.py", "Server.py"):
        issues.append("Server.py missing")
    
    if not check_file_exists("Backend/main.py", "main.py"):
        issues.append("main.py missing")
    
    if not check_file_exists("Backend/requirements.txt", "requirements.txt"):
        issues.append("requirements.txt missing")
    
    # Check environment file
    if check_file_exists("Backend/.env", ".env file"):
        print("   ℹ️  Environment file found (will be used for local testing)")
    else:
        print("   ⚠️  .env file missing (environment variables will be set in Cloud Run)")
    
    # Check handlers
    handlers_dir = Path("Backend/handlers")
    if handlers_dir.exists():
        handler_count = len(list(handlers_dir.glob("*.py")))
        print(f"   ✅ Handlers directory: {handler_count} files")
    else:
        print("   ❌ Handlers directory: Missing")
        issues.append("Handlers directory missing")
    
    return issues

def validate_frontend():
    """Validate frontend readiness"""
    print("\n🌐 Frontend Validation")
    print("-" * 21)
    
    issues = []
    
    # Check Dockerfile
    if not check_file_exists("app/Dockerfile", "Frontend Dockerfile"):
        issues.append("Frontend Dockerfile missing")
    
    # Check package.json
    if not check_file_exists("app/package.json", "package.json"):
        issues.append("package.json missing")
    
    # Check src directory
    if not check_file_exists("app/src", "src directory"):
        issues.append("src directory missing")
    
    # Check public directory
    if not check_file_exists("app/public", "public directory"):
        issues.append("public directory missing")
    
    # Check if node_modules exists (optional)
    if Path("app/node_modules").exists():
        print("   ✅ node_modules: Found (dependencies installed)")
    else:
        print("   ⚠️  node_modules: Missing (will install during build)")
    
    # Check build directory (optional)
    if Path("app/build").exists():
        print("   ✅ build directory: Found (previous build exists)")
    else:
        print("   ℹ️  build directory: Missing (will create during build)")
    
    return issues

def main():
    """Main validation function"""
    print("🔍 EasyShifts Deployment Readiness Check")
    print("=" * 45)
    
    all_issues = []
    
    # Check prerequisites
    print("\n🛠️  Prerequisites Check")
    print("-" * 22)
    
    prereq_issues = []
    
    if not check_command("docker --version", "Docker"):
        prereq_issues.append("Docker not installed")
    elif not check_docker_running():
        prereq_issues.append("Docker daemon not running")
    
    if not check_command("gcloud --version", "Google Cloud CLI"):
        prereq_issues.append("Google Cloud CLI not installed")
    elif not check_gcloud_auth():
        prereq_issues.append("Google Cloud not authenticated")
    
    project_ok, project_id = check_gcloud_project()
    if not project_ok:
        prereq_issues.append("Google Cloud project not configured")
    
    if not check_command("node --version", "Node.js"):
        prereq_issues.append("Node.js not installed")
    
    if not check_command("npm --version", "NPM"):
        prereq_issues.append("NPM not installed")
    
    all_issues.extend(prereq_issues)
    
    # Validate backend
    backend_issues = validate_backend()
    all_issues.extend(backend_issues)
    
    # Validate frontend
    frontend_issues = validate_frontend()
    all_issues.extend(frontend_issues)
    
    # Check deployment scripts
    print("\n📜 Deployment Scripts")
    print("-" * 20)
    
    if check_file_exists("Backend/deploy_holi_full.py", "Full deployment script"):
        pass
    else:
        all_issues.append("Full deployment script missing")
    
    if check_file_exists("Backend/quick_deploy.py", "Quick deployment script"):
        pass
    else:
        all_issues.append("Quick deployment script missing")
    
    check_file_exists("Backend/deployment_config.json", "Deployment config")
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 VALIDATION SUMMARY")
    print("=" * 45)
    
    if not all_issues:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your EasyShifts application is ready for deployment!")
        print("\n🚀 To deploy, run:")
        print("   cd Backend")
        print("   python deploy_holi_full.py")
        print("\n   OR for quick deployment:")
        print("   python quick_deploy.py")
        return True
    else:
        print(f"⚠️  {len(all_issues)} ISSUES FOUND:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 NEXT STEPS:")
        if prereq_issues:
            print("   1. Install missing prerequisites")
            print("   2. Authenticate with Google Cloud")
            print("   3. Configure your project")
        
        if backend_issues or frontend_issues:
            print("   4. Fix missing files and directories")
            print("   5. Ensure all required components are present")
        
        print("   6. Run this validation script again")
        print("   7. Deploy when all checks pass")
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️  Validation interrupted")
        exit(1)
    except Exception as e:
        print(f"\n💥 Validation error: {e}")
        exit(1)
