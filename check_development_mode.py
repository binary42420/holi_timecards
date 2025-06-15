#!/usr/bin/env python3
"""
EasyShifts Development Mode Configuration Checker
Validates and updates all environment settings to development mode.
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

def check_frontend_env_configs():
    """Check frontend environment configurations"""
    print("🎨 Frontend Environment Configuration")
    print("-" * 50)
    
    issues = []
    
    # Check app/public/env-config.js
    env_config = check_file_exists("app/public/env-config.js")
    if env_config:
        content = env_config.read_text(encoding='utf-8')
        if 'REACT_APP_ENV: "development"' in content:
            print("   ✅ app/public/env-config.js: REACT_APP_ENV = development")
        elif 'REACT_APP_ENV: "production"' in content:
            print("   ❌ app/public/env-config.js: REACT_APP_ENV = production (should be development)")
            issues.append("app/public/env-config.js: Set to production mode")
        else:
            print("   ⚠️  app/public/env-config.js: REACT_APP_ENV not found")
            issues.append("app/public/env-config.js: REACT_APP_ENV not configured")
    
    # Check app/build/env-config.js
    build_env_config = check_file_exists("app/build/env-config.js")
    if build_env_config:
        content = build_env_config.read_text(encoding='utf-8')
        if 'REACT_APP_ENV: "development"' in content:
            print("   ✅ app/build/env-config.js: REACT_APP_ENV = development")
        elif 'REACT_APP_ENV: "production"' in content:
            print("   ❌ app/build/env-config.js: REACT_APP_ENV = production (should be development)")
            issues.append("app/build/env-config.js: Set to production mode")
        else:
            print("   ⚠️  app/build/env-config.js: REACT_APP_ENV not found")
    
    # Check app/.env.production
    env_prod = check_file_exists("app/.env.production")
    if env_prod:
        content = env_prod.read_text(encoding='utf-8')
        if 'REACT_APP_ENV=development' in content:
            print("   ✅ app/.env.production: REACT_APP_ENV = development")
        elif 'REACT_APP_ENV=production' in content:
            print("   ❌ app/.env.production: REACT_APP_ENV = production (should be development)")
            issues.append("app/.env.production: Set to production mode")
    
    # Check app/src/utils/env.js default
    env_js = check_file_exists("app/src/utils/env.js")
    if env_js:
        content = env_js.read_text(encoding='utf-8')
        if "getEnvVar('REACT_APP_ENV', 'development')" in content:
            print("   ✅ app/src/utils/env.js: Default environment = development")
        elif "getEnvVar('REACT_APP_ENV', 'production')" in content:
            print("   ❌ app/src/utils/env.js: Default environment = production (should be development)")
            issues.append("app/src/utils/env.js: Default set to production")
    
    return issues

def check_deployment_configs():
    """Check deployment configuration files"""
    print("\n☁️ Deployment Configuration")
    print("-" * 50)
    
    issues = []
    
    # Check cloudrun-frontend.yaml
    frontend_yaml = check_file_exists("cloudrun-frontend.yaml")
    if frontend_yaml:
        try:
            config = yaml.safe_load(frontend_yaml.read_text())
            env_vars = config["spec"]["template"]["spec"]["containers"][0]["env"]
            react_env = None
            for var in env_vars:
                if var["name"] == "REACT_APP_ENV":
                    react_env = var["value"]
                    break
            
            if react_env == "development":
                print("   ✅ cloudrun-frontend.yaml: REACT_APP_ENV = development")
            elif react_env == "production":
                print("   ❌ cloudrun-frontend.yaml: REACT_APP_ENV = production (should be development)")
                issues.append("cloudrun-frontend.yaml: Set to production mode")
            else:
                print("   ⚠️  cloudrun-frontend.yaml: REACT_APP_ENV not found")
                issues.append("cloudrun-frontend.yaml: REACT_APP_ENV not configured")
        except Exception as e:
            issues.append(f"cloudrun-frontend.yaml: Error reading - {e}")
    
    # Check deploy.ps1
    deploy_ps1 = check_file_exists("deploy.ps1")
    if deploy_ps1:
        content = deploy_ps1.read_text(encoding='utf-8')
        if 'REACT_APP_ENV=development' in content:
            print("   ✅ deploy.ps1: REACT_APP_ENV = development")
        elif 'REACT_APP_ENV=production' in content:
            print("   ❌ deploy.ps1: REACT_APP_ENV = production (should be development)")
            issues.append("deploy.ps1: Set to production mode")
        else:
            print("   ⚠️  deploy.ps1: REACT_APP_ENV not found")
    
    # Check docker-compose.yml
    docker_compose = check_file_exists("docker-compose.yml")
    if docker_compose:
        try:
            config = yaml.safe_load(docker_compose.read_text())
            frontend_env = config.get("services", {}).get("frontend", {}).get("environment", [])
            react_env_found = False
            for env_var in frontend_env:
                if "REACT_APP_ENV=" in env_var:
                    if "REACT_APP_ENV=development" in env_var:
                        print("   ✅ docker-compose.yml: REACT_APP_ENV = development")
                        react_env_found = True
                    elif "REACT_APP_ENV=production" in env_var:
                        print("   ❌ docker-compose.yml: REACT_APP_ENV = production (should be development)")
                        issues.append("docker-compose.yml: Set to production mode")
                        react_env_found = True
                    break
            
            if not react_env_found:
                print("   ⚠️  docker-compose.yml: REACT_APP_ENV not found")
        except Exception as e:
            issues.append(f"docker-compose.yml: Error reading - {e}")
    
    return issues

def check_backend_env_configs():
    """Check backend environment configurations"""
    print("\n🔧 Backend Environment Configuration")
    print("-" * 50)
    
    issues = []
    
    # Check Backend/.env.template
    env_template = check_file_exists("Backend/.env.template")
    if env_template:
        content = env_template.read_text(encoding='utf-8')
        if 'ENVIRONMENT=development' in content:
            print("   ✅ Backend/.env.template: ENVIRONMENT = development")
        elif 'ENVIRONMENT=production' in content:
            print("   ❌ Backend/.env.template: ENVIRONMENT = production (should be development)")
            issues.append("Backend/.env.template: Set to production mode")
    
    # Check deployment scripts for backend environment
    deploy_scripts = [
        "Backend/deploy_direct.py",
        "Backend/deploy_cloud_run_fix.py",
        "deploy-local-containers.ps1"
    ]
    
    for script_path in deploy_scripts:
        script_file = check_file_exists(script_path)
        if script_file:
            content = script_file.read_text(encoding='utf-8')
            if 'ENVIRONMENT=development' in content or '"ENVIRONMENT": "development"' in content:
                print(f"   ✅ {script_path}: ENVIRONMENT = development")
            elif 'ENVIRONMENT=production' in content or '"ENVIRONMENT": "production"' in content:
                print(f"   ❌ {script_path}: ENVIRONMENT = production (should be development)")
                issues.append(f"{script_path}: Set to production mode")
    
    return issues

def generate_fixes(all_issues):
    """Generate fix commands for identified issues"""
    if not all_issues:
        return
    
    print("\n🔧 Recommended Fixes")
    print("-" * 50)
    
    for issue in all_issues:
        if "app/public/env-config.js" in issue:
            print("   Fix: Update app/public/env-config.js")
            print('   sed -i \'s/REACT_APP_ENV: "production"/REACT_APP_ENV: "development"/g\' app/public/env-config.js')
        
        elif "app/build/env-config.js" in issue:
            print("   Fix: Update app/build/env-config.js")
            print('   sed -i \'s/REACT_APP_ENV: "production"/REACT_APP_ENV: "development"/g\' app/build/env-config.js')
        
        elif "app/.env.production" in issue:
            print("   Fix: Update app/.env.production")
            print('   sed -i \'s/REACT_APP_ENV=production/REACT_APP_ENV=development/g\' app/.env.production')
        
        elif "cloudrun-frontend.yaml" in issue:
            print("   Fix: Update cloudrun-frontend.yaml")
            print('   sed -i \'s/value: "production"/value: "development"/g\' cloudrun-frontend.yaml')
        
        elif "deploy.ps1" in issue:
            print("   Fix: Update deploy.ps1")
            print('   sed -i \'s/REACT_APP_ENV=production/REACT_APP_ENV=development/g\' deploy.ps1')
        
        elif "docker-compose.yml" in issue:
            print("   Fix: Update docker-compose.yml")
            print('   sed -i \'s/REACT_APP_ENV=production/REACT_APP_ENV=development/g\' docker-compose.yml')

def main():
    """Main validation function"""
    print("🔍 EasyShifts Development Mode Configuration Check")
    print("=" * 60)
    
    all_issues = []
    
    # Run all checks
    all_issues.extend(check_frontend_env_configs())
    all_issues.extend(check_deployment_configs())
    all_issues.extend(check_backend_env_configs())
    
    # Summary
    print("\n📋 Development Mode Check Summary")
    print("=" * 60)
    
    if not all_issues:
        print("✅ All configurations are set to development mode!")
        print("\n🎯 Current Development Settings:")
        print("   • Frontend: REACT_APP_ENV = development")
        print("   • Backend: ENVIRONMENT = development")
        print("   • Deployment: All scripts use development mode")
        print("   • Docker: Development environment variables")
        return True
    else:
        print(f"❌ Found {len(all_issues)} configuration issues:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        
        generate_fixes(all_issues)
        
        print("\n🔧 Next Steps:")
        print("   1. Apply the fixes shown above")
        print("   2. Re-run this validation script")
        print("   3. Rebuild and redeploy if necessary")
        print("   4. Verify development mode is active")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
