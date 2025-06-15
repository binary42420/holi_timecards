#!/usr/bin/env python3
"""
Pre-deployment validation for EasyShifts Backend
Checks all port, environment, and setup issues before Cloud Run deployment
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

def load_environment():
    """Load environment variables from .env file"""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        return True
    return False

def check_port_configuration():
    """Check port configuration consistency"""
    print("🔌 Port Configuration Check")
    print("-" * 30)
    
    issues = []
    
    # Check Server.py port configuration
    with open('Server.py', 'r', encoding='utf-8') as f:
        server_content = f.read()
    
    if "'PORT', 8080)" in server_content:
        print("   ✅ Server.py: Default port 8080 (Cloud Run compatible)")
    elif "'PORT', 8085)" in server_content:
        issues.append("Server.py still uses port 8085 instead of 8080")
    else:
        issues.append("Server.py port configuration unclear")
    
    # Check Dockerfile port
    with open('Dockerfile', 'r', encoding='utf-8') as f:
        dockerfile_content = f.read()
    
    if 'EXPOSE 8080' in dockerfile_content:
        print("   ✅ Dockerfile: Exposes port 8080")
    else:
        issues.append("Dockerfile doesn't expose port 8080")
    
    # Check startup script
    if 'start_server_with_env.py' in dockerfile_content:
        print("   ✅ Dockerfile: Uses environment-aware startup script")
    else:
        issues.append("Dockerfile doesn't use start_server_with_env.py")
    
    return issues

def check_environment_configuration():
    """Check environment variable configuration"""
    print("\n🌍 Environment Configuration Check")
    print("-" * 35)
    
    issues = []
    
    # Check .env file exists
    if not Path('.env').exists():
        issues.append(".env file missing")
        return issues
    
    print("   ✅ .env file exists")
    
    # Load and check required variables
    load_environment()
    
    required_vars = [
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
        'REDIS_HOST', 'REDIS_PORT', 'REDIS_PASSWORD',
        'SESSION_SECRET_KEY', 'CSRF_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            if 'PASSWORD' in var or 'SECRET' in var:
                print(f"   ✅ {var}: ***")
            else:
                print(f"   ✅ {var}: {os.getenv(var)}")
    
    if missing_vars:
        issues.append(f"Missing environment variables: {', '.join(missing_vars)}")
    
    return issues

def check_startup_script():
    """Check startup script configuration"""
    print("\n🚀 Startup Script Check")
    print("-" * 25)
    
    issues = []
    
    # Check if start_server_with_env.py exists
    if not Path('start_server_with_env.py').exists():
        issues.append("start_server_with_env.py missing")
        return issues
    
    print("   ✅ start_server_with_env.py exists")
    
    # Check if it loads environment properly
    with open('start_server_with_env.py', 'r', encoding='utf-8') as f:
        startup_content = f.read()
    
    if 'load_environment()' in startup_content:
        print("   ✅ Startup script loads environment")
    else:
        issues.append("Startup script doesn't load environment")
    
    if 'Server.start_combined_server()' in startup_content:
        print("   ✅ Startup script calls combined server")
    else:
        issues.append("Startup script doesn't call combined server")
    
    return issues

def test_local_server_startup():
    """Test local server startup"""
    print("\n🧪 Local Server Startup Test")
    print("-" * 30)
    
    issues = []
    
    try:
        # Test import of main modules
        print("   Testing module imports...")
        
        # Test Server.py import
        sys.path.insert(0, '.')
        import Server
        print("   ✅ Server.py imports successfully")
        
        # Test main.py import
        import main
        print("   ✅ main.py imports successfully")
        
        # Test environment loading
        load_environment()
        print("   ✅ Environment variables loaded")
        
        # Test database connection
        from main import get_db_session
        with get_db_session() as session:
            pass
        print("   ✅ Database connection working")
        
        # Test Redis connection
        from config.redis_config import redis_config
        redis_client = redis_config.get_sync_connection()
        redis_client.ping()
        print("   ✅ Redis connection working")
        
    except Exception as e:
        issues.append(f"Server startup test failed: {e}")
        print(f"   ❌ Server startup test failed: {e}")
    
    return issues

def check_cloud_run_requirements():
    """Check Cloud Run specific requirements"""
    print("\n☁️  Cloud Run Requirements Check")
    print("-" * 35)
    
    issues = []
    
    # Check requirements.txt
    if not Path('requirements.txt').exists():
        issues.append("requirements.txt missing")
    else:
        print("   ✅ requirements.txt exists")
        
        # Check for essential packages
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            requirements = f.read()
        
        essential_packages = ['aiohttp', 'websockets', 'sqlalchemy', 'redis', 'bcrypt']
        for package in essential_packages:
            if package.lower() in requirements.lower():
                print(f"   ✅ {package} in requirements")
            else:
                issues.append(f"Missing essential package: {package}")
    
    # Check Dockerfile health check
    with open('Dockerfile', 'r', encoding='utf-8') as f:
        dockerfile_content = f.read()
    
    if 'HEALTHCHECK' in dockerfile_content:
        print("   ✅ Dockerfile has health check")
    else:
        issues.append("Dockerfile missing health check")
    
    # Check for non-root user
    if 'USER app' in dockerfile_content:
        print("   ✅ Dockerfile uses non-root user")
    else:
        issues.append("Dockerfile should use non-root user")
    
    return issues

def create_deployment_script():
    """Create optimized deployment script"""
    deployment_script = f'''#!/bin/bash
# EasyShifts Backend Deployment Script
# Generated: {datetime.now().isoformat()}

set -e  # Exit on any error

echo "🚀 EasyShifts Backend Deployment to Cloud Run"
echo "=============================================="

# Configuration
PROJECT_ID="easyshifts-434822"
REGION="us-central1"
SERVICE_NAME="easyshifts-backend"

echo "📋 Deployment Configuration:"
echo "   Project: $PROJECT_ID"
echo "   Region: $REGION"
echo "   Service: $SERVICE_NAME"
echo ""

# Pre-deployment validation
echo "🔍 Running pre-deployment validation..."
python pre_deployment_validation.py
if [ $? -ne 0 ]; then
    echo "❌ Pre-deployment validation failed!"
    exit 1
fi
echo ""

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \\
    --source . \\
    --platform managed \\
    --region $REGION \\
    --allow-unauthenticated \\
    --memory 1Gi \\
    --cpu 1 \\
    --concurrency 100 \\
    --timeout 300 \\
    --port 8080 \\
    --set-env-vars DB_HOST=miano.h.filess.io \\
    --set-env-vars DB_PORT=3305 \\
    --set-env-vars DB_NAME=easyshiftsdb_danceshall \\
    --set-env-vars DB_USER=easyshiftsdb_danceshall \\
    --set-env-vars DB_PASSWORD=a61d15d9b4f2671739338d1082cc7b75c0084e21 \\
    --set-env-vars REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com \\
    --set-env-vars REDIS_PORT=12649 \\
    --set-env-vars REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa \\
    --set-env-vars REDIS_DB=0 \\
    --set-env-vars SESSION_SECRET_KEY=K8mP9vN2xQ7wE5tR1yU6iO3pA8sD4fG9hJ2kL5nM7bV0cX1zQ6wE9rT3yU8iO5pA \\
    --set-env-vars CSRF_SECRET_KEY=X9mN2bV5cQ8wE1rT4yU7iO0pA3sD6fG2hJ5kL8nM1bV4cX7zQ0wE3rT6yU9iO2pA \\
    --set-env-vars GOOGLE_CLIENT_ID=794306818447-4prnpg1p13a4smvnnfs7tfvkesrld9ms.apps.googleusercontent.com \\
    --set-env-vars ENVIRONMENT=production \\
    --set-env-vars DEBUG=false \\
    --set-env-vars SESSION_TIMEOUT=3600 \\
    --set-env-vars REDIS_MAX_CONNECTIONS=20

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "🧪 Testing deployed service..."
    
    # Get service URL
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")
    echo "🌐 Service URL: $SERVICE_URL"
    
    # Test health endpoint
    echo "🏥 Testing health endpoint..."
    curl -f "$SERVICE_URL/health" || echo "⚠️  Health check failed"
    
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo "📋 Next steps:"
    echo "   1. Test login functionality"
    echo "   2. Monitor service logs: gcloud run logs read $SERVICE_NAME --region=$REGION"
    echo "   3. Update frontend to use new backend URL if needed"
else
    echo "❌ Deployment failed!"
    exit 1
fi
'''
    
    with open('deploy_to_cloud_run.sh', 'w', encoding='utf-8') as f:
        f.write(deployment_script)
    
    # Make executable
    os.chmod('deploy_to_cloud_run.sh', 0o755)
    print("✅ Created deploy_to_cloud_run.sh")

def main():
    """Run comprehensive pre-deployment validation"""
    print("🔍 EasyShifts Pre-Deployment Validation")
    print("=" * 45)
    print(f"🕐 Validation Time: {datetime.now().isoformat()}")
    print()
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_port_configuration())
    all_issues.extend(check_environment_configuration())
    all_issues.extend(check_startup_script())
    all_issues.extend(test_local_server_startup())
    all_issues.extend(check_cloud_run_requirements())
    
    # Create deployment script
    create_deployment_script()
    
    # Summary
    print("\n" + "=" * 45)
    print("📊 VALIDATION SUMMARY")
    print("=" * 45)
    
    if all_issues:
        print("❌ Issues Found:")
        for issue in all_issues:
            print(f"   • {issue}")
        print("\n⚠️  Please fix these issues before deployment!")
        return False
    else:
        print("✅ All validation checks passed!")
        print("\n🎉 Ready for Cloud Run deployment!")
        print("\n📋 To deploy:")
        print("   ./deploy_to_cloud_run.sh")
        print("\n📋 Or manually:")
        print("   gcloud run deploy easyshifts-backend --source . --region us-central1")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
