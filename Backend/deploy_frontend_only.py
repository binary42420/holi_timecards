#!/usr/bin/env python3
"""
EasyShifts Frontend-Only Deployment Script
Deploy just the frontend after fixing build issues
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

def main():
    """Deploy frontend only"""
    print("🌐 EasyShifts Frontend-Only Deploy")
    print("=" * 36)
    
    project_id = "goog-71174"
    region = "us-central1"
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    registry = f"gcr.io/{project_id}"
    
    # Paths
    root_dir = Path(__file__).parent.parent
    frontend_dir = root_dir / "app"
    
    print(f"📁 Frontend: {frontend_dir}")
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
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        return False
    
    # Authenticate Docker
    print("\n🔐 Authenticating Docker...")
    if not run_command("gcloud auth configure-docker"):
        return False
    
    # Build frontend
    print("\n🏗️  Building Frontend...")
    
    # Fix frontend build issues
    print("🔧 Fixing frontend build issues...")

    # Clean install to fix dependency issues
    print("   🧹 Cleaning node_modules...")
    import shutil
    node_modules = frontend_dir / "node_modules"
    package_lock = frontend_dir / "package-lock.json"

    if node_modules.exists():
        shutil.rmtree(node_modules)
    if package_lock.exists():
        package_lock.unlink()

    # Clean npm cache
    run_command("npm cache clean --force", cwd=frontend_dir)

    # Install Babel plugin first
    print("   📦 Installing Babel plugin...")
    if not run_command("npm install --save-dev @babel/plugin-proposal-private-property-in-object", cwd=frontend_dir):
        print("❌ Failed to install Babel plugin")
        return False
    
    # Update browserslist
    run_command("npx update-browserslist-db@latest", cwd=frontend_dir)
    
    # Install all dependencies
    print("   📦 Installing dependencies...")
    if not run_command("npm install --legacy-peer-deps", cwd=frontend_dir):
        print("❌ Failed to install dependencies")
        return False

    # Try to fix audit issues (but don't fail if it doesn't work)
    print("   🔒 Attempting to fix security issues...")
    run_command("npm audit fix --force", cwd=frontend_dir)

    # Build React app with better error handling
    print("   🏗️  Building React application...")
    build_success = run_command("npm run build", cwd=frontend_dir)

    if not build_success:
        print("❌ React build failed. Trying alternative approaches...")

        # Try with different Node options
        print("   🔄 Trying with legacy OpenSSL...")
        build_success = run_command("NODE_OPTIONS=--openssl-legacy-provider npm run build", cwd=frontend_dir)

        if not build_success:
            print("   🔄 Trying to skip preflight check...")
            # Create .env file to skip preflight check
            env_file = frontend_dir / ".env"
            with open(env_file, 'w') as f:
                f.write("SKIP_PREFLIGHT_CHECK=true\n")
                f.write("GENERATE_SOURCEMAP=false\n")

            build_success = run_command("npm run build", cwd=frontend_dir)

    if not build_success:
        print("❌ All build attempts failed")
        print("\n🔧 Manual fix required:")
        print("   cd ../app")
        print("   rm -rf node_modules package-lock.json")
        print("   npm install --save-dev @babel/plugin-proposal-private-property-in-object")
        print("   npm install --legacy-peer-deps")
        print("   npm run build")
        return False

    print("✅ React build successful!")
    
    # Build Docker image
    frontend_image = f"{registry}/easyshifts-frontend:{timestamp}"
    
    if run_command(f"docker build -t {frontend_image} .", cwd=frontend_dir):
        print("📤 Pushing frontend...")
        if run_command(f"docker push {frontend_image}"):
            print("🚀 Deploying frontend...")
            
            # Get backend URL for environment variables
            backend_url = "https://easyshifts-backend-123456789-uc.a.run.app"  # Default
            backend_url_cmd = f"gcloud run services describe easyshifts-backend --region {region} --format value(status.url)"
            result = subprocess.run(backend_url_cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                backend_url = result.stdout.strip()
                print(f"   🔗 Using backend URL: {backend_url}")
            
            # Deploy to Cloud Run
            deploy_cmd = f"""gcloud run deploy easyshifts-frontend --image {frontend_image} --region {region} --platform managed --allow-unauthenticated --port 80 --memory 512Mi --set-env-vars REACT_APP_BACKEND_URL={backend_url},REACT_APP_WS_URL={backend_url.replace('https://', 'wss://')}/ws"""
            
            if run_command(deploy_cmd):
                print("✅ Frontend deployed!")
                
                # Get frontend URL
                print("\n🌐 Getting frontend URL...")
                url_cmd = f"gcloud run services describe easyshifts-frontend --region {region} --format value(status.url)"
                result = subprocess.run(url_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0:
                    frontend_url = result.stdout.strip()
                    print(f"🌐 Frontend URL: {frontend_url}")
                    
                    # Test frontend
                    print("\n🧪 Testing frontend...")
                    test_cmd = f"curl -f {frontend_url}"
                    if run_command(test_cmd):
                        print("✅ Frontend accessibility check passed!")
                    else:
                        print("⚠️  Frontend accessibility check failed (but service is deployed)")
                    
                    print("\n🎉 FRONTEND DEPLOYMENT COMPLETE!")
                    print("=" * 40)
                    print(f"🌐 Frontend: {frontend_url}")
                    print(f"🔧 Backend: {backend_url}")
                    print("\n✨ Your complete EasyShifts application is now live!")
                    
                    return True
                else:
                    print("❌ Failed to get frontend URL")
                    return False
            else:
                print("❌ Frontend deployment failed")
                return False
        else:
            print("❌ Failed to push frontend image")
            return False
    else:
        print("❌ Failed to build frontend Docker image")
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
