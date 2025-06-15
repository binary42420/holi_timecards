#!/usr/bin/env python3
"""
Deploy Cloud Run service with updated environment variables to fix Redis connection
"""

import os
import subprocess
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.production')

def get_env_vars():
    """Get environment variables for Cloud Run deployment"""
    env_vars = {
        # Database Configuration
        'DB_HOST': os.getenv('DB_HOST'),
        'DB_PORT': os.getenv('DB_PORT'),
        'DB_USER': os.getenv('DB_USER'),
        'DB_NAME': os.getenv('DB_NAME'),
        'DB_PASSWORD': os.getenv('DB_PASSWORD'),
        
        # Redis Configuration
        'REDIS_HOST': os.getenv('REDIS_HOST'),
        'REDIS_PORT': os.getenv('REDIS_PORT'),
        'REDIS_PASSWORD': os.getenv('REDIS_PASSWORD'),
        'REDIS_DB': os.getenv('REDIS_DB', '0'),
        'REDIS_MAX_CONNECTIONS': os.getenv('REDIS_MAX_CONNECTIONS', '20'),
        'REDIS_SOCKET_TIMEOUT': os.getenv('REDIS_SOCKET_TIMEOUT', '5'),
        'REDIS_CONNECT_TIMEOUT': os.getenv('REDIS_CONNECT_TIMEOUT', '5'),
        
        # Session Configuration
        'SESSION_SECRET_KEY': os.getenv('SESSION_SECRET_KEY'),
        'CSRF_SECRET_KEY': os.getenv('CSRF_SECRET_KEY'),
        'SESSION_TIMEOUT_MINUTES': os.getenv('SESSION_TIMEOUT_MINUTES', '480'),
        
        # Security Configuration
        'VALIDATE_SESSION_IP': os.getenv('VALIDATE_SESSION_IP', 'false'),
        'PASSWORD_MIN_LENGTH': os.getenv('PASSWORD_MIN_LENGTH', '8'),
        'REQUIRE_PASSWORD_COMPLEXITY': os.getenv('REQUIRE_PASSWORD_COMPLEXITY', 'true'),
        
        # Server Configuration
        'HOST': os.getenv('HOST', '0.0.0.0'),
        'PORT': os.getenv('PORT', '8080'),  # Cloud Run default port
        'ENVIRONMENT': os.getenv('ENVIRONMENT', 'production'),
        
        # Google OAuth
        'GOOGLE_CLIENT_ID': os.getenv('GOOGLE_CLIENT_ID')
    }
    
    # Filter out None values
    return {k: v for k, v in env_vars.items() if v is not None}

def create_env_vars_command(env_vars):
    """Create the environment variables command for gcloud"""
    env_args = []
    for key, value in env_vars.items():
        env_args.append(f"{key}={value}")
    
    return ",".join(env_args)

def deploy_to_cloud_run():
    """Deploy the updated service to Cloud Run"""
    print("🚀 Deploying EasyShifts Backend to Cloud Run")
    print("=" * 45)
    
    # Get environment variables
    env_vars = get_env_vars()
    
    print("📋 Environment Variables to Deploy:")
    for key, value in env_vars.items():
        if 'PASSWORD' in key or 'SECRET' in key or 'TOKEN' in key:
            display_value = '*' * 10
        else:
            display_value = value
        print(f"   {key}: {display_value}")
    
    # Create the gcloud command
    service_name = "easyshifts-backend"
    region = "us-central1"
    project_id = "easyshifts"  # Update this if different
    
    env_vars_str = create_env_vars_command(env_vars)
    
    # Build the gcloud command
    cmd = [
        "gcloud", "run", "services", "update", service_name,
        "--region", region,
        "--project", project_id,
        "--set-env-vars", env_vars_str,
        "--format", "json"
    ]
    
    print(f"\n🔧 Updating Cloud Run service: {service_name}")
    print(f"📍 Region: {region}")
    print(f"🏗️ Project: {project_id}")
    
    try:
        print("\n⏳ Executing gcloud command...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("✅ Cloud Run service updated successfully!")
        
        # Parse the result
        service_info = json.loads(result.stdout)
        service_url = service_info.get('status', {}).get('url', 'Unknown')
        
        print(f"🌐 Service URL: {service_url}")
        print(f"🔌 WebSocket URL: {service_url.replace('https://', 'wss://')}/ws")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Cloud Run deployment failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse gcloud output: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def verify_deployment():
    """Verify the deployment by testing the health endpoint"""
    print("\n🧪 Verifying Deployment")
    print("=" * 25)
    
    try:
        import requests
        
        health_url = "https://easyshifts-backend-794306818447.us-central1.run.app/health"
        print(f"🔍 Testing health endpoint: {health_url}")
        
        response = requests.get(health_url, timeout=10)
        
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
    print("🚀 EasyShifts Cloud Run Deployment Fix")
    print("=" * 40)
    
    # Check if gcloud is installed
    try:
        subprocess.run(["gcloud", "--version"], capture_output=True, check=True)
        print("✅ gcloud CLI is available")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ gcloud CLI not found. Please install Google Cloud SDK.")
        return False
    
    # Deploy to Cloud Run
    deployment_success = deploy_to_cloud_run()
    
    if deployment_success:
        print("\n⏳ Waiting for deployment to propagate...")
        import time
        time.sleep(10)  # Wait for deployment to propagate
        
        # Verify deployment
        verification_success = verify_deployment()
        
        if verification_success:
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("The Redis connection issue should now be resolved.")
            print("\nNext steps:")
            print("1. Test the frontend login")
            print("2. Verify WebSocket connection")
            print("3. Check session creation")
        else:
            print("\n⚠️ Deployment completed but verification failed")
            print("Check the Cloud Run logs for more details.")
    else:
        print("\n❌ DEPLOYMENT FAILED")
        print("Please check the error messages above.")
    
    return deployment_success

if __name__ == "__main__":
    main()
