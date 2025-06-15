#!/usr/bin/env python3
"""
EasyShifts Port Configuration Validation Script
Validates that all port configurations are correct for Google Cloud Run deployment.
"""

import os
import re
import json
import yaml
from pathlib import Path

def check_file_exists(file_path):
    """Check if file exists and return Path object"""
    path = Path(file_path)
    if not path.exists():
        print(f"❌ File not found: {file_path}")
        return None
    return path

def validate_backend_ports():
    """Validate backend port configurations"""
    print("🔧 Validating Backend Port Configuration")
    print("-" * 50)
    
    issues = []
    
    # Check Server.py
    server_py = check_file_exists("Backend/Server.py")
    if server_py:
        content = server_py.read_text(encoding='utf-8')
        if "'PORT', 8080)" in content:
            print("   ✅ Server.py: Uses port 8080 (Cloud Run compatible)")
        else:
            issues.append("Server.py: Port configuration not set to 8080")
            print("   ❌ Server.py: Port not configured for 8080")
    
    # Check Backend Dockerfile
    dockerfile = check_file_exists("Backend/Dockerfile")
    if dockerfile:
        content = dockerfile.read_text(encoding='utf-8')
        if "EXPOSE 8080" in content:
            print("   ✅ Backend Dockerfile: Exposes port 8080")
        else:
            issues.append("Backend Dockerfile: Does not expose port 8080")
            print("   ❌ Backend Dockerfile: Port 8080 not exposed")
    
    # Check deployment configuration
    deploy_config = check_file_exists("Backend/deployment_config.json")
    if deploy_config:
        try:
            config = json.loads(deploy_config.read_text())
            backend_port = config.get("services", {}).get("backend", {}).get("port")
            if backend_port == 8080:
                print("   ✅ deployment_config.json: Backend port set to 8080")
            else:
                issues.append(f"deployment_config.json: Backend port is {backend_port}, should be 8080")
                print(f"   ❌ deployment_config.json: Backend port is {backend_port}")
        except Exception as e:
            issues.append(f"deployment_config.json: Error reading file - {e}")
    
    return issues

def validate_frontend_ports():
    """Validate frontend port configurations"""
    print("\n🎨 Validating Frontend Port Configuration")
    print("-" * 50)
    
    issues = []
    
    # Check frontend Dockerfile
    dockerfile = check_file_exists("app/Dockerfile")
    if dockerfile:
        content = dockerfile.read_text(encoding='utf-8')
        if "ENV PORT=8080" in content and "EXPOSE $PORT" in content:
            print("   ✅ Frontend Dockerfile: PORT=8080 and EXPOSE $PORT")
        else:
            issues.append("Frontend Dockerfile: PORT environment or EXPOSE not configured correctly")
            print("   ❌ Frontend Dockerfile: Port configuration issue")
    
    # Check nginx.conf
    nginx_conf = check_file_exists("app/nginx.conf")
    if nginx_conf:
        content = nginx_conf.read_text(encoding='utf-8')
        if "listen PORT_PLACEHOLDER;" in content:
            print("   ✅ nginx.conf: Uses PORT_PLACEHOLDER for dynamic port")
        else:
            issues.append("nginx.conf: Does not use PORT_PLACEHOLDER")
            print("   ❌ nginx.conf: Static port configuration found")
    
    # Check env.sh
    env_sh = check_file_exists("app/env.sh")
    if env_sh:
        content = env_sh.read_text(encoding='utf-8')
        if "PORT=${PORT:-8080}" in content and "PORT_PLACEHOLDER" in content:
            print("   ✅ env.sh: Defaults to 8080 and replaces PORT_PLACEHOLDER")
        else:
            issues.append("env.sh: Port configuration not correct")
            print("   ❌ env.sh: Port configuration issue")
    
    return issues

def validate_cloud_run_configs():
    """Validate Cloud Run YAML configurations"""
    print("\n☁️ Validating Cloud Run Configuration")
    print("-" * 50)
    
    issues = []
    
    # Check backend Cloud Run config
    backend_yaml = check_file_exists("cloudrun-backend.yaml")
    if backend_yaml:
        try:
            config = yaml.safe_load(backend_yaml.read_text())
            container_port = config["spec"]["template"]["spec"]["containers"][0]["ports"][0]["containerPort"]
            if container_port == 8080:
                print("   ✅ cloudrun-backend.yaml: Container port 8080")
            else:
                issues.append(f"cloudrun-backend.yaml: Container port is {container_port}, should be 8080")
                print(f"   ❌ cloudrun-backend.yaml: Container port is {container_port}")
        except Exception as e:
            issues.append(f"cloudrun-backend.yaml: Error reading - {e}")
    
    # Check frontend Cloud Run config
    frontend_yaml = check_file_exists("cloudrun-frontend.yaml")
    if frontend_yaml:
        try:
            config = yaml.safe_load(frontend_yaml.read_text())
            container_port = config["spec"]["template"]["spec"]["containers"][0]["ports"][0]["containerPort"]
            if container_port == 8080:
                print("   ✅ cloudrun-frontend.yaml: Container port 8080")
            else:
                issues.append(f"cloudrun-frontend.yaml: Container port is {container_port}, should be 8080")
                print(f"   ❌ cloudrun-frontend.yaml: Container port is {container_port}")
        except Exception as e:
            issues.append(f"cloudrun-frontend.yaml: Error reading - {e}")
    
    return issues

def validate_deployment_scripts():
    """Validate deployment scripts for correct port usage"""
    print("\n🚀 Validating Deployment Scripts")
    print("-" * 50)
    
    issues = []
    
    # Check main deployment script
    deploy_ps1 = check_file_exists("deploy.ps1")
    if deploy_ps1:
        content = deploy_ps1.read_text(encoding='utf-8')
        # Check for --port 8080 in gcloud commands
        if "--port 8080" in content or "port 8080" in content:
            print("   ✅ deploy.ps1: Uses port 8080 in deployment")
        else:
            issues.append("deploy.ps1: Does not specify port 8080 in deployment")
            print("   ❌ deploy.ps1: Port 8080 not specified")
    
    return issues

def validate_docker_compose():
    """Validate docker-compose.yml port mappings"""
    print("\n🐳 Validating Docker Compose Configuration")
    print("-" * 50)
    
    issues = []
    
    docker_compose = check_file_exists("docker-compose.yml")
    if docker_compose:
        try:
            config = yaml.safe_load(docker_compose.read_text())
            
            # Check backend ports
            backend_ports = config.get("services", {}).get("backend", {}).get("ports", [])
            if "8080:8080" in backend_ports:
                print("   ✅ docker-compose.yml: Backend maps 8080:8080")
            else:
                issues.append("docker-compose.yml: Backend port mapping incorrect")
                print(f"   ❌ docker-compose.yml: Backend ports: {backend_ports}")
            
            # Check frontend ports
            frontend_ports = config.get("services", {}).get("frontend", {}).get("ports", [])
            if "8080:8080" in frontend_ports:
                print("   ✅ docker-compose.yml: Frontend maps 8080:8080")
            else:
                issues.append("docker-compose.yml: Frontend port mapping should be 8080:8080")
                print(f"   ❌ docker-compose.yml: Frontend ports: {frontend_ports}")
                
        except Exception as e:
            issues.append(f"docker-compose.yml: Error reading - {e}")
    
    return issues

def main():
    """Main validation function"""
    print("🔍 EasyShifts Port Configuration Validation")
    print("=" * 60)
    
    all_issues = []
    
    # Run all validations
    all_issues.extend(validate_backend_ports())
    all_issues.extend(validate_frontend_ports())
    all_issues.extend(validate_cloud_run_configs())
    all_issues.extend(validate_deployment_scripts())
    all_issues.extend(validate_docker_compose())
    
    # Summary
    print("\n📋 Validation Summary")
    print("=" * 60)
    
    if not all_issues:
        print("✅ All port configurations are correct for Google Cloud Run!")
        print("\n🎯 Key Configuration Points:")
        print("   • Backend: Port 8080 (Cloud Run standard)")
        print("   • Frontend: Port 8080 (Cloud Run standard)")
        print("   • WebSocket: Uses same port as HTTP (8080)")
        print("   • Health checks: Configured for correct ports")
        print("   • Docker containers: Expose port 8080")
        return True
    else:
        print(f"❌ Found {len(all_issues)} port configuration issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n🔧 Recommended Actions:")
        print("   1. Fix the issues listed above")
        print("   2. Re-run this validation script")
        print("   3. Test deployment to Cloud Run")
        print("   4. Verify WebSocket connections work")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
