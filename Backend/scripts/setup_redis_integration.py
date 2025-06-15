#!/usr/bin/env python3
"""
Setup script for Redis integration in EasyShifts
Configures Redis, validates environment, and prepares the application for deployment
"""

import os
import sys
import json
import secrets
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisIntegrationSetup:
    """Setup and configuration for Redis integration"""
    
    def __init__(self):
        self.config = {}
        self.required_env_vars = [
            'REDIS_HOST',
            'REDIS_PORT',
            'REDIS_PASSWORD',
            'SESSION_SECRET_KEY',
            'CSRF_SECRET_KEY'
        ]
        
    def generate_secure_keys(self) -> Dict[str, str]:
        """Generate secure keys for session management"""
        keys = {
            'SESSION_SECRET_KEY': secrets.token_urlsafe(32),
            'CSRF_SECRET_KEY': secrets.token_urlsafe(32),
            'ENCRYPTION_KEY': secrets.token_urlsafe(32)
        }
        
        logger.info("✅ Generated secure keys for session management")
        return keys
    
    def validate_redis_config(self) -> bool:
        """Validate Redis configuration"""
        try:
            redis_host = os.getenv('REDIS_HOST', 'redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com')
            redis_port = int(os.getenv('REDIS_PORT', '12649'))
            redis_password = os.getenv('REDIS_PASSWORD')
            
            if not redis_host or not redis_port:
                logger.error("❌ Redis host and port must be configured")
                return False
            
            if not redis_password:
                logger.warning("⚠️ Redis password not set - this is recommended for production")
            
            # Test Redis connection
            try:
                import redis
                redis_client = redis.Redis(
                    host=redis_host,
                    port=redis_port,
                    password=redis_password,
                    decode_responses=True,
                    socket_timeout=5
                )
                
                result = redis_client.ping()
                if result:
                    logger.info(f"✅ Redis connection successful to {redis_host}:{redis_port}")
                    return True
                else:
                    logger.error("❌ Redis ping failed")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Redis connection failed: {e}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Redis configuration validation failed: {e}")
            return False
    
    def create_env_file(self, environment: str = 'production') -> bool:
        """Create environment file with Redis configuration"""
        try:
            env_file = f".env.{environment}"
            
            # Generate secure keys
            secure_keys = self.generate_secure_keys()
            
            env_content = f"""# EasyShifts {environment.title()} Environment Configuration
# Generated on {datetime.now().isoformat()}

# Google OAuth Configuration
GOOGLE_CLIENT_ID=444854334434-fqapk7semoggrnj247bv8auqe4n32ldl.apps.googleusercontent.com

# Database Configuration
DB_HOST=miano.h.filess.io
DB_PORT=3305
DB_USER=easyshiftsdb_danceshall
DB_NAME=easyshiftsdb_danceshall
# DB_PASSWORD should be set via Cloud Run environment variables

# Redis Configuration
REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com
REDIS_PORT=12649
# REDIS_PASSWORD should be set via Cloud Run environment variables
REDIS_DB=0
REDIS_MAX_CONNECTIONS=20
REDIS_SOCKET_TIMEOUT=5
REDIS_CONNECT_TIMEOUT=5

# Session Configuration
SESSION_TIMEOUT_MINUTES=480
SESSION_SECRET_KEY={secure_keys['SESSION_SECRET_KEY']}
CSRF_SECRET_KEY={secure_keys['CSRF_SECRET_KEY']}

# Security Configuration
VALIDATE_SESSION_IP=false
PASSWORD_MIN_LENGTH=8
REQUIRE_PASSWORD_COMPLEXITY=true

# Cache Configuration
CACHE_DEFAULT_TTL=3600
CACHE_USER_PROFILE_TTL=1800
CACHE_SHIFT_DATA_TTL=900

# Server Configuration
HOST=0.0.0.0
PORT=8080

# Environment
ENVIRONMENT={environment}

# Logging
LOG_LEVEL=INFO
"""
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            logger.info(f"✅ Created environment file: {env_file}")
            
            # Create secrets file for Cloud Run
            secrets_content = f"""# Secrets for Cloud Run deployment
# These should be stored as Cloud Run secrets, not in version control

REDIS_PASSWORD=your_redis_password_here
DB_PASSWORD=a61d15d9b4f2671739338d1082cc7b75c0084e21
SESSION_SECRET_KEY={secure_keys['SESSION_SECRET_KEY']}
CSRF_SECRET_KEY={secure_keys['CSRF_SECRET_KEY']}
ENCRYPTION_KEY={secure_keys['ENCRYPTION_KEY']}
"""
            
            with open(f"secrets.{environment}.env", 'w') as f:
                f.write(secrets_content)
            
            logger.info(f"✅ Created secrets file: secrets.{environment}.env")
            logger.warning("⚠️ Remember to set these secrets in Cloud Run and delete the secrets file")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create environment file: {e}")
            return False
    
    def create_docker_config(self) -> bool:
        """Create Docker configuration for Redis integration"""
        try:
            dockerfile_additions = """
# Redis Integration Dependencies
RUN pip install redis aioredis hiredis bcrypt

# Copy Redis configuration files
COPY config/redis_config.py /app/config/
COPY security/secure_session.py /app/security/
COPY cache/redis_cache.py /app/cache/
COPY websocket/redis_websocket_manager.py /app/websocket/

# Copy monitoring scripts
COPY monitoring/redis_health_check.py /app/monitoring/

# Set up Redis health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD python /app/monitoring/redis_health_check.py || exit 1
"""
            
            with open("Dockerfile.redis", 'w') as f:
                f.write(dockerfile_additions)
            
            logger.info("✅ Created Docker configuration for Redis integration")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create Docker configuration: {e}")
            return False
    
    def create_cloud_run_config(self) -> bool:
        """Create Cloud Run deployment configuration"""
        try:
            cloud_run_config = {
                "apiVersion": "serving.knative.dev/v1",
                "kind": "Service",
                "metadata": {
                    "name": "easyshifts-backend",
                    "annotations": {
                        "run.googleapis.com/ingress": "all"
                    }
                },
                "spec": {
                    "template": {
                        "metadata": {
                            "annotations": {
                                "run.googleapis.com/execution-environment": "gen2",
                                "run.googleapis.com/memory": "1Gi",
                                "run.googleapis.com/cpu": "1000m"
                            }
                        },
                        "spec": {
                            "containerConcurrency": 100,
                            "timeoutSeconds": 300,
                            "containers": [{
                                "image": "gcr.io/PROJECT_ID/easyshifts-backend",
                                "ports": [{"containerPort": 8080}],
                                "env": [
                                    {"name": "REDIS_HOST", "value": "redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com"},
                                    {"name": "REDIS_PORT", "value": "12649"},
                                    {"name": "REDIS_DB", "value": "0"},
                                    {"name": "SESSION_TIMEOUT_MINUTES", "value": "480"},
                                    {"name": "ENVIRONMENT", "value": "production"},
                                    {
                                        "name": "REDIS_PASSWORD",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": "redis-credentials",
                                                "key": "password"
                                            }
                                        }
                                    },
                                    {
                                        "name": "SESSION_SECRET_KEY",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": "session-secrets",
                                                "key": "session-key"
                                            }
                                        }
                                    },
                                    {
                                        "name": "CSRF_SECRET_KEY",
                                        "valueFrom": {
                                            "secretKeyRef": {
                                                "name": "session-secrets",
                                                "key": "csrf-key"
                                            }
                                        }
                                    }
                                ],
                                "resources": {
                                    "limits": {
                                        "memory": "1Gi",
                                        "cpu": "1000m"
                                    }
                                }
                            }]
                        }
                    }
                }
            }
            
            with open("cloud-run-service.yaml", 'w') as f:
                json.dump(cloud_run_config, f, indent=2)
            
            logger.info("✅ Created Cloud Run service configuration")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create Cloud Run configuration: {e}")
            return False
    
    def create_deployment_scripts(self) -> bool:
        """Create deployment scripts"""
        try:
            # Create deployment script
            deploy_script = """#!/bin/bash
# EasyShifts Redis Integration Deployment Script

set -e

echo "🚀 Starting EasyShifts Redis Integration Deployment..."

# Check if required environment variables are set
if [ -z "$REDIS_PASSWORD" ]; then
    echo "❌ REDIS_PASSWORD environment variable is required"
    exit 1
fi

# Create Cloud Run secrets
echo "📝 Creating Cloud Run secrets..."
echo -n "$REDIS_PASSWORD" | gcloud secrets create redis-credentials --data-file=-
echo -n "$SESSION_SECRET_KEY" | gcloud secrets create session-secrets --data-file=-

# Build and deploy
echo "🔨 Building Docker image..."
docker build -t gcr.io/$PROJECT_ID/easyshifts-backend .

echo "📤 Pushing Docker image..."
docker push gcr.io/$PROJECT_ID/easyshifts-backend

echo "🚀 Deploying to Cloud Run..."
gcloud run services replace cloud-run-service.yaml

echo "✅ Deployment completed successfully!"
echo "🔍 Run health check: python monitoring/redis_health_check.py"
"""
            
            with open("deploy-redis.sh", 'w') as f:
                f.write(deploy_script)
            
            os.chmod("deploy-redis.sh", 0o755)
            
            logger.info("✅ Created deployment script: deploy-redis.sh")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create deployment scripts: {e}")
            return False
    
    def run_setup(self, environment: str = 'production') -> bool:
        """Run complete Redis integration setup"""
        logger.info("🚀 Starting Redis integration setup...")
        
        try:
            # Step 1: Validate Redis configuration
            logger.info("Step 1: Validating Redis configuration...")
            if not self.validate_redis_config():
                logger.error("❌ Setup aborted: Redis configuration validation failed")
                return False
            
            # Step 2: Create environment files
            logger.info("Step 2: Creating environment configuration...")
            if not self.create_env_file(environment):
                logger.error("❌ Setup aborted: Environment file creation failed")
                return False
            
            # Step 3: Create Docker configuration
            logger.info("Step 3: Creating Docker configuration...")
            if not self.create_docker_config():
                logger.error("❌ Setup aborted: Docker configuration failed")
                return False
            
            # Step 4: Create Cloud Run configuration
            logger.info("Step 4: Creating Cloud Run configuration...")
            if not self.create_cloud_run_config():
                logger.error("❌ Setup aborted: Cloud Run configuration failed")
                return False
            
            # Step 5: Create deployment scripts
            logger.info("Step 5: Creating deployment scripts...")
            if not self.create_deployment_scripts():
                logger.error("❌ Setup aborted: Deployment script creation failed")
                return False
            
            logger.info("✅ Redis integration setup completed successfully!")
            self.print_next_steps()
            return True
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False
    
    def print_next_steps(self):
        """Print next steps for deployment"""
        print("\n" + "="*60)
        print("REDIS INTEGRATION SETUP COMPLETED")
        print("="*60)
        print("Next steps:")
        print("1. Set your Redis password:")
        print("   export REDIS_PASSWORD='your_redis_password'")
        print()
        print("2. Run the migration script:")
        print("   python migrations/migrate_to_redis_sessions.py")
        print()
        print("3. Test the Redis health check:")
        print("   python monitoring/redis_health_check.py")
        print()
        print("4. Deploy to Cloud Run:")
        print("   ./deploy-redis.sh")
        print()
        print("5. Monitor Redis performance:")
        print("   python monitoring/redis_health_check.py")
        print("="*60)

def main():
    """Main setup function"""
    print("EasyShifts Redis Integration Setup")
    print("=" * 35)
    
    environment = input("Enter environment (production/development) [production]: ").strip() or 'production'
    
    setup = RedisIntegrationSetup()
    success = setup.run_setup(environment)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
