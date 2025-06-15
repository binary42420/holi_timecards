#!/usr/bin/env python3
"""
Fixed Simple Deployment for EasyShifts Backend
"""

import subprocess
from datetime import datetime

def run_command(command):
    """Run command and return success status"""
    try:
        print(f"🔄 Running command...")
        print(f"   {command[:100]}{'...' if len(command) > 100 else ''}")
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print(f"✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}{'...' if len(result.stdout.strip()) > 200 else ''}")
            return True
        else:
            print(f"❌ Failed (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def main():
    """Deploy with fixed commands"""
    print("🔧 EasyShifts Fixed Simple Deploy")
    print("=" * 35)
    
    project_id = "goog-71174"
    region = "us-central1"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    registry = f"gcr.io/{project_id}"
    
    # Test current service first
    print("🧪 Testing current service...")
    test_cmd = "curl -f https://easyshifts-backend-794306818447.us-central1.run.app/health"
    if run_command(test_cmd):
        print("✅ Current service is working!")
        print("🎉 Your backend is already deployed and functional!")
        print("\n🌐 URLs:")
        print("   Health: https://easyshifts-backend-794306818447.us-central1.run.app/health")
        print("   Root: https://easyshifts-backend-794306818447.us-central1.run.app/")
        return True
    else:
        print("⚠️  Current service not responding, deploying new version...")
    
    # Build new image
    backend_image = f"{registry}/easyshifts-backend:{timestamp}"
    
    print("\n🏗️  Building new backend image...")
    if not run_command(f"docker build -t {backend_image} ."):
        return False
    
    print("\n📤 Pushing image...")
    if not run_command(f"docker push {backend_image}"):
        return False
    
    print("\n🚀 Deploying to Cloud Run...")
    
    # Single line deploy command
    deploy_cmd = f"gcloud run deploy easyshifts-backend --image {backend_image} --region {region} --platform managed --allow-unauthenticated --port 8080 --memory 1Gi --timeout 900 --set-env-vars DB_HOST=miano.h.filess.io,DB_PORT=3305,DB_NAME=easyshiftsdb_danceshall,DB_USER=easyshiftsdb_danceshall,DB_PASSWORD=a61d15d9b4f2671739338d1082cc7b75c0084e21,REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com,REDIS_PORT=12649,REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa"
    
    if run_command(deploy_cmd):
        print("✅ Deployment successful!")
        
        print("\n⏳ Waiting for service to start...")
        import time
        time.sleep(30)
        
        print("\n🧪 Testing deployed service...")
        if run_command("curl -f https://easyshifts-backend-794306818447.us-central1.run.app/health"):
            print("✅ Service is working!")
        else:
            print("⚠️  Service deployed but not responding")
            
            # Check logs
            print("\n📋 Checking logs...")
            logs_cmd = "gcloud logging read \"resource.type=cloud_run_revision AND resource.labels.service_name=easyshifts-backend\" --limit=10 --format=\"value(textPayload)\""
            run_command(logs_cmd)
        
        print("\n🎉 DEPLOYMENT COMPLETE!")
        print("🌐 Backend URL: https://easyshifts-backend-794306818447.us-central1.run.app")
        return True
    else:
        print("❌ Deployment failed")
        return False

if __name__ == "__main__":
    main()
