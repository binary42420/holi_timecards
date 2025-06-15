#!/usr/bin/env python3
"""
Simple EasyShifts Backend Deployment
Deploy backend without complex health checks for debugging
"""

import os
import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_command(command, cwd=None):
    """Run command and return success status"""
    try:
        print(f"🔄 {command}")
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True, timeout=600)
        if result.returncode == 0:
            print(f"✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ Failed (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

def create_simple_dockerfile():
    """Create a simplified Dockerfile for debugging"""
    dockerfile_content = '''# Simple Dockerfile for debugging
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    default-libmysqlclient-dev \\
    pkg-config \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Environment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8080

# No health check for now - let Cloud Run handle it
# CMD with better error output
CMD ["python", "-u", "start_server_with_env.py"]
'''
    
    with open('Dockerfile.simple', 'w') as f:
        f.write(dockerfile_content)
    
    print("✅ Created simplified Dockerfile")

def main():
    """Deploy backend with simple configuration"""
    print("🔧 EasyShifts Simple Backend Deploy")
    print("=" * 38)
    
    project_id = "goog-71174"
    region = "us-central1"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    registry = f"gcr.io/{project_id}"
    
    # Paths
    root_dir = Path(__file__).parent.parent
    backend_dir = root_dir / "Backend"
    
    print(f"📁 Backend: {backend_dir}")
    print(f"🏗️  Project: {project_id}")
    print(f"🌍 Region: {region}")
    print()
    
    # Create simple Dockerfile
    os.chdir(backend_dir)
    create_simple_dockerfile()
    
    # Check prerequisites
    print("🔍 Checking tools...")
    if not run_command("docker --version"):
        return False
    if not run_command("gcloud --version"):
        return False
    
    # Authenticate Docker
    print("\n🔐 Authenticating Docker...")
    if not run_command("gcloud auth configure-docker"):
        return False
    
    # Build with simple Dockerfile
    print("\n🏗️  Building Backend (Simple)...")
    backend_image = f"{registry}/easyshifts-backend:{timestamp}"
    
    if run_command(f"docker build -f Dockerfile.simple -t {backend_image} .", cwd=backend_dir):
        print("📤 Pushing backend...")
        if run_command(f"docker push {backend_image}"):
            print("🚀 Deploying backend...")
            
            # Deploy with minimal configuration
            deploy_cmd = f"""gcloud run deploy easyshifts-backend \\
                --image {backend_image} \\
                --region {region} \\
                --platform managed \\
                --allow-unauthenticated \\
                --port 8080 \\
                --memory 1Gi \\
                --cpu 1 \\
                --timeout 900 \\
                --concurrency 100 \\
                --max-instances 10 \\
                --no-cpu-throttling \\
                --set-env-vars DB_HOST=miano.h.filess.io,DB_PORT=3305,DB_NAME=easyshiftsdb_danceshall,DB_USER=easyshiftsdb_danceshall,DB_PASSWORD=a61d15d9b4f2671739338d1082cc7b75c0084e21,REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com,REDIS_PORT=12649,REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa,SESSION_SECRET_KEY=your-session-secret-key-here,CSRF_SECRET_KEY=your-csrf-secret-key-here"""
            
            if run_command(deploy_cmd):
                print("✅ Backend deployed!")
                
                # Get URL
                print("\n🌐 Getting backend URL...")
                url_cmd = f"gcloud run services describe easyshifts-backend --region {region} --format value(status.url)"
                result = subprocess.run(url_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    backend_url = result.stdout.strip()
                    print(f"🔧 Backend URL: {backend_url}")
                    
                    # Wait a bit for startup
                    print("\n⏳ Waiting for service to start...")
                    import time
                    time.sleep(30)
                    
                    # Test health endpoint
                    print("🧪 Testing backend...")
                    test_cmd = f"curl -f {backend_url}/health"
                    if run_command(test_cmd):
                        print("✅ Backend health check passed!")
                    else:
                        print("⚠️  Health check failed, but service is deployed")
                        print("   Try accessing the URL directly in browser")
                    
                    # Check logs
                    print("\n📋 Recent logs:")
                    logs_cmd = f"gcloud logs read --service=easyshifts-backend --limit=10"
                    run_command(logs_cmd)
                    
                    print("\n🎉 BACKEND DEPLOYMENT COMPLETE!")
                    print("=" * 40)
                    print(f"🔧 Backend API: {backend_url}")
                    print(f"🔍 Health: {backend_url}/health")
                    print(f"🔌 WebSocket: {backend_url.replace('https://', 'wss://')}/ws")
                    
                    print("\n📋 Debugging Commands:")
                    print(f"   gcloud logs tail --service=easyshifts-backend")
                    print(f"   gcloud run services describe easyshifts-backend --region {region}")
                    
                    return True
                else:
                    print("❌ Failed to get backend URL")
                    return False
            else:
                print("❌ Backend deployment failed")
                
                # Show logs for debugging
                print("\n📋 Deployment logs:")
                logs_cmd = f"gcloud logs read --service=easyshifts-backend --limit=20"
                run_command(logs_cmd)
                
                return False
        else:
            print("❌ Failed to push backend image")
            return False
    else:
        print("❌ Failed to build backend")
        return False

if __name__ == "__main__":
    try:
        if main():
            exit(0)
        else:
            exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Deployment cancelled")
        exit(1)
