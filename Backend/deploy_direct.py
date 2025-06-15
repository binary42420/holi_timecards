#!/usr/bin/env python3
"""
Deploy EasyShifts backend directly to Cloud Run with environment variables
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def deploy_to_cloud_run():
    """Deploy directly to Cloud Run with source code"""
    print("🚀 Deploying EasyShifts Backend to Cloud Run")
    print("=" * 45)
    
    # Environment variables for Cloud Run
    env_vars = {
        'DB_HOST': 'miano.h.filess.io',
        'DB_PORT': '3305',
        'DB_USER': 'easyshiftsdb_danceshall',
        'DB_NAME': 'easyshiftsdb_danceshall',
        'DB_PASSWORD': 'a61d15d9b4f2671739338d1082cc7b75c0084e21',
        'REDIS_HOST': 'redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com',
        'REDIS_PORT': '12649',
        'REDIS_PASSWORD': 'AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa',
        'REDIS_DB': '0',
        'REDIS_MAX_CONNECTIONS': '20',
        'REDIS_SOCKET_TIMEOUT': '5',
        'REDIS_CONNECT_TIMEOUT': '5',
        'SESSION_SECRET_KEY': 'K8mP9vN2xQ7wE5tR1yU6iO3pA8sD4fG9hJ2kL5nM7bV0cX1zQ6wE9rT3yU8iO5pA',
        'CSRF_SECRET_KEY': 'X9mN2bV5cQ8wE1rT4yU7iO0pA3sD6fG2hJ5kL8nM1bV4cX7zQ0wE3rT6yU9iO2pA',
        'SESSION_TIMEOUT_MINUTES': '480',
        'VALIDATE_SESSION_IP': 'false',
        'PASSWORD_MIN_LENGTH': '8',
        'REQUIRE_PASSWORD_COMPLEXITY': 'true',
        'HOST': '0.0.0.0',
        'PORT': '8080',
        'ENVIRONMENT': 'production',
        'GOOGLE_CLIENT_ID': '794306818447-4prnpg1p13a4smvnnfs7tfvkesrld9ms.apps.googleusercontent.com'
    }
    
    # Create environment variables string
    env_vars_str = ','.join([f"{k}={v}" for k, v in env_vars.items()])
    
    print("📋 Environment Variables:")
    for key, value in env_vars.items():
        if 'PASSWORD' in key or 'SECRET' in key:
            display_value = '*' * 10
        else:
            display_value = value
        print(f"   {key}: {display_value}")
    
    # Build the gcloud command
    cmd = [
        'gcloud', 'run', 'deploy', 'easyshifts-backend',
        '--source', '.',
        '--region', 'us-central1',
        '--platform', 'managed',
        '--allow-unauthenticated',
        '--port', '8080',
        '--memory', '1Gi',
        '--cpu', '1',
        '--max-instances', '10',
        '--set-env-vars', env_vars_str,
        '--quiet'
    ]
    
    print(f"\n🔧 Deploying to Cloud Run...")
    print(f"📍 Region: us-central1")
    print(f"🏗️ Service: easyshifts-backend")
    
    try:
        print("\n⏳ Starting deployment (this may take several minutes)...")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            print("✅ Deployment successful!")
            
            # Extract service URL from output
            lines = result.stderr.split('\n')
            service_url = None
            for line in lines:
                if 'Service URL:' in line:
                    service_url = line.split('Service URL:')[1].strip()
                    break
            
            if service_url:
                print(f"🌐 Service URL: {service_url}")
                print(f"🔌 WebSocket URL: {service_url.replace('https://', 'wss://')}/ws")
            
            return True
        else:
            print(f"❌ Deployment failed!")
            print(f"Error: {result.stderr}")
            print(f"Output: {result.stdout}")
            return False
            
    except Exception as e:
        print(f"❌ Deployment error: {e}")
        return False

def test_deployment():
    """Test the deployed service"""
    print("\n🧪 Testing Deployed Service")
    print("=" * 30)
    
    try:
        import requests
        
        health_url = "https://easyshifts-backend-s5b2sxgpsa-uc.a.run.app/health"
        print(f"🔍 Testing: {health_url}")
        
        response = requests.get(health_url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed:")
            print(f"   Status: {data.get('status')}")
            print(f"   Service: {data.get('service')}")
            print(f"   Timestamp: {data.get('timestamp')}")
            return True
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def main():
    """Main deployment function"""
    print("🚀 EasyShifts Cloud Run Deployment")
    print("=" * 40)
    
    # Deploy to Cloud Run
    deployment_success = deploy_to_cloud_run()
    
    if deployment_success:
        print("\n⏳ Waiting for deployment to propagate...")
        import time
        time.sleep(15)  # Wait for deployment to propagate
        
        # Test deployment
        test_success = test_deployment()
        
        if test_success:
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("The backend is now deployed with updated environment variables.")
            print("\nNext steps:")
            print("1. Test the frontend WebSocket connection")
            print("2. Try logging in with admin/Hdfatboy1!")
            print("3. Verify session creation is working")
        else:
            print("\n⚠️ Deployment completed but health check failed")
            print("Check the Cloud Run logs for more details.")
    else:
        print("\n❌ DEPLOYMENT FAILED")
        print("Please check the error messages above.")
    
    return deployment_success

if __name__ == "__main__":
    main()
