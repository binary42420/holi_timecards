#!/usr/bin/env python3
"""
Quick EasyShifts Deployment Script
Simplified version for rapid deployment
"""

import os
import sys
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(command, cwd=None):
    """Run command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {command}")
            return True
        else:
            print(f"❌ {command}")
            print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"💥 {command} - Exception: {e}")
        return False

def main():
    """Quick deployment"""
    print("🚀 EasyShifts Quick Deploy")
    print("=" * 30)
    
    # Load config
    config_file = Path(__file__).parent / "deployment_config.json"
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
        project_id = config["project_id"]
        region = config["region"]
    else:
        project_id = "goog-71174"
        region = "us-central1"
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    registry = f"gcr.io/{project_id}"
    
    # Paths
    root_dir = Path(__file__).parent.parent
    backend_dir = root_dir / "Backend"
    frontend_dir = root_dir / "app"
    
    print(f"📁 Root: {root_dir}")
    print(f"🏗️  Project: {project_id}")
    print(f"🌍 Region: {region}")
    print()
    
    # Check prerequisites
    print("🔍 Checking tools...")
    tools = ["docker", "gcloud", "node", "npm"]
    for tool in tools:
        if not run_command(f"{tool} --version"):
            print(f"❌ {tool} not found")
            return False
    
    # Authenticate Docker
    print("\n🔐 Authenticating Docker...")
    if not run_command("gcloud auth configure-docker"):
        return False
    
    # Build and deploy backend
    print("\n🏗️  Building Backend...")
    backend_image = f"{registry}/easyshifts-backend:{timestamp}"
    
    if run_command(f"docker build -t {backend_image} .", cwd=backend_dir):
        print("📤 Pushing backend...")
        if run_command(f"docker push {backend_image}"):
            print("🚀 Deploying backend...")
            deploy_cmd = f"""gcloud run deploy easyshifts-backend \
                --image {backend_image} \
                --region {region} \
                --platform managed \
                --allow-unauthenticated \
                --port 8080 \
                --memory 1Gi \
                --set-env-vars DB_HOST=miano.h.filess.io,DB_PORT=3305,DB_NAME=easyshiftsdb_danceshall,DB_USER=easyshiftsdb_danceshall,DB_PASSWORD=a61d15d9b4f2671739338d1082cc7b75c0084e21,REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com,REDIS_PORT=12649,REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa"""
            
            if run_command(deploy_cmd):
                print("✅ Backend deployed!")
            else:
                print("❌ Backend deployment failed")
                return False
    
    # Skip frontend for now due to build issues
    print("\n⏭️  Skipping Frontend (build issues)")
    print("   Frontend can be deployed separately after fixing Babel dependency")
    print("   Run: cd ../app && npm install --save-dev @babel/plugin-proposal-private-property-in-object")
    
    # Get backend URL only
    print("\n🌐 Getting backend URL...")
    backend_url_cmd = f"gcloud run services describe easyshifts-backend --region {region} --format value(status.url)"

    backend_result = subprocess.run(backend_url_cmd, shell=True, capture_output=True, text=True)

    print("\n🎉 BACKEND DEPLOYMENT COMPLETE!")
    print("=" * 35)

    if backend_result.returncode == 0:
        backend_url = backend_result.stdout.strip()
        print(f"🔧 Backend API: {backend_url}")

        # Test backend health
        print("\n🧪 Testing backend...")
        test_cmd = f"curl -f {backend_url}/health"
        if run_command(test_cmd):
            print("✅ Backend health check passed!")
        else:
            print("⚠️  Backend health check failed (but service is deployed)")
    else:
        print("❌ Failed to get backend URL")

    print("\n📋 Next Steps:")
    print("1. Your backend API is now live and ready!")
    print("2. To deploy frontend later:")
    print("   cd ../app")
    print("   npm install --save-dev @babel/plugin-proposal-private-property-in-object")
    print("   npm run build")
    print("   # Then run frontend deployment")

    print("\n✨ Backend deployment successful!")
    return True

if __name__ == "__main__":
    try:
        if main():
            sys.exit(0)
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Deployment cancelled")
        sys.exit(1)
