# EasyShifts Cloud Run Deployment Guide

This guide provides comprehensive instructions for deploying EasyShifts frontend and backend to Google Cloud Run using locally built containers.

## 📋 Prerequisites

### Required Tools
- **Docker** - For building containers
- **Google Cloud CLI** - For deployment
- **Node.js & NPM** - For frontend build
- **Python 3.7+** - For deployment scripts

### Installation Commands
```bash
# Install Google Cloud CLI (Ubuntu/Debian)
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Install Docker (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install docker.io
sudo usermod -aG docker $USER

# Install Node.js (Ubuntu/Debian)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

## 🔧 Setup

### 1. Google Cloud Authentication
```bash
# Login to Google Cloud
gcloud auth login

# Set your project ID
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Configure Docker for GCR
```bash
gcloud auth configure-docker
```

### 3. Update Configuration
Edit `deployment_config.json` with your project details:
```json
{
  "project_id": "your-actual-project-id",
  "region": "us-central1"
}
```

## 🚀 Deployment Options

### Option 1: Full Deployment Script (Recommended)
```bash
cd Backend
python deploy_holi_full.py
```

**Features:**
- ✅ Comprehensive error checking
- ✅ Prerequisites validation
- ✅ Build both frontend and backend
- ✅ Push to Google Container Registry
- ✅ Deploy to Cloud Run
- ✅ Health checks
- ✅ Deployment report generation
- ✅ Optional cleanup

### Option 2: Quick Deployment
```bash
cd Backend
python quick_deploy.py
```

**Features:**
- ✅ Simplified deployment process
- ✅ Faster execution
- ✅ Basic error handling
- ✅ Essential functionality only

### Option 3: Manual Deployment

#### Backend Deployment
```bash
cd Backend

# Build container
docker build -t gcr.io/YOUR_PROJECT_ID/easyshifts-backend:latest .

# Push to registry
docker push gcr.io/YOUR_PROJECT_ID/easyshifts-backend:latest

# Deploy to Cloud Run
gcloud run deploy easyshifts-backend \
  --image gcr.io/YOUR_PROJECT_ID/easyshifts-backend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 1Gi \
  --set-env-vars DB_HOST=miano.h.filess.io,DB_PORT=3305,DB_NAME=easyshiftsdb_danceshall,DB_USER=easyshiftsdb_danceshall,DB_PASSWORD=a61d15d9b4f2671739338d1082cc7b75c0084e21,REDIS_HOST=redis-12649.c328.europe-west3-1.gce.redns.redis-cloud.com,REDIS_PORT=12649,REDIS_PASSWORD=AtpYvgs0JUs0KvuZm93yvTEzkXEg4fNa
```

#### Frontend Deployment
```bash
cd app

# Build React app
npm install
npm run build

# Build container
docker build -t gcr.io/YOUR_PROJECT_ID/easyshifts-frontend:latest .

# Push to registry
docker push gcr.io/YOUR_PROJECT_ID/easyshifts-frontend:latest

# Deploy to Cloud Run
gcloud run deploy easyshifts-frontend \
  --image gcr.io/YOUR_PROJECT_ID/easyshifts-frontend:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 80 \
  --memory 512Mi
```

## 🔍 Verification

### Health Checks
```bash
# Test backend health
curl https://YOUR_BACKEND_URL/health

# Test frontend accessibility
curl https://YOUR_FRONTEND_URL
```

### Service Status
```bash
# Check backend service
gcloud run services describe easyshifts-backend --region us-central1

# Check frontend service
gcloud run services describe easyshifts-frontend --region us-central1
```

## 🛠️ Configuration

### Environment Variables

#### Backend
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `DB_NAME` - Database name
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `REDIS_HOST` - Redis host
- `REDIS_PORT` - Redis port
- `REDIS_PASSWORD` - Redis password
- `SESSION_SECRET_KEY` - Session encryption key
- `CSRF_SECRET_KEY` - CSRF protection key

#### Frontend
- `REACT_APP_BACKEND_URL` - Backend API URL
- `REACT_APP_WS_URL` - WebSocket URL

### Resource Allocation

#### Backend
- **Memory**: 1Gi
- **CPU**: 1 vCPU
- **Port**: 8080
- **Timeout**: 300 seconds
- **Concurrency**: 100 requests
- **Max Instances**: 10

#### Frontend
- **Memory**: 512Mi
- **CPU**: 1 vCPU
- **Port**: 80
- **Timeout**: 300 seconds
- **Concurrency**: 100 requests
- **Max Instances**: 5

## 🐛 Troubleshooting

### Common Issues

#### Build Failures
```bash
# Check Docker daemon
sudo systemctl status docker

# Check disk space
df -h

# Clean Docker cache
docker system prune -f
```

#### Authentication Issues
```bash
# Re-authenticate
gcloud auth login
gcloud auth configure-docker

# Check current project
gcloud config get-value project
```

#### Deployment Failures
```bash
# Check service logs
gcloud logs read --service=easyshifts-backend --limit=50

# Check service status
gcloud run services list
```

### Debug Commands
```bash
# View deployment logs
gcloud run services describe easyshifts-backend --region us-central1

# Stream live logs
gcloud logs tail --service=easyshifts-backend

# Check container registry
gcloud container images list --repository=gcr.io/YOUR_PROJECT_ID
```

## 📊 Monitoring

### Cloud Run Metrics
- Request count
- Request latency
- Error rate
- Memory usage
- CPU utilization

### Custom Monitoring
```bash
# Set up log-based metrics
gcloud logging metrics create error_rate \
  --description="Error rate metric" \
  --log-filter='resource.type="cloud_run_revision" AND severity>=ERROR'
```

## 🔄 Updates

### Rolling Updates
```bash
# Deploy new version
python deploy_holi_full.py

# Rollback if needed
gcloud run services replace-traffic easyshifts-backend --to-revisions=PREVIOUS_REVISION=100
```

### Blue-Green Deployment
```bash
# Deploy to new revision without traffic
gcloud run deploy easyshifts-backend-staging --image NEW_IMAGE --no-traffic

# Gradually shift traffic
gcloud run services update-traffic easyshifts-backend --to-revisions=NEW_REVISION=50,OLD_REVISION=50
```

## 📈 Scaling

### Auto Scaling
Cloud Run automatically scales based on:
- Request volume
- CPU usage
- Memory usage

### Manual Scaling
```bash
# Set minimum instances
gcloud run services update easyshifts-backend --min-instances=1

# Set maximum instances
gcloud run services update easyshifts-backend --max-instances=20
```

## 🔒 Security

### IAM Permissions
```bash
# Allow unauthenticated access (public)
gcloud run services add-iam-policy-binding easyshifts-frontend \
  --member="allUsers" \
  --role="roles/run.invoker"

# Restrict to authenticated users
gcloud run services remove-iam-policy-binding easyshifts-frontend \
  --member="allUsers" \
  --role="roles/run.invoker"
```

### Custom Domains
```bash
# Map custom domain
gcloud run domain-mappings create --service easyshifts-frontend --domain your-domain.com
```

## 💰 Cost Optimization

### Tips
- Use minimum instances sparingly
- Monitor request patterns
- Optimize container size
- Use appropriate memory allocation
- Enable CPU throttling for cost savings

### Cost Monitoring
```bash
# Set up billing alerts
gcloud alpha billing budgets create \
  --billing-account=BILLING_ACCOUNT_ID \
  --display-name="Cloud Run Budget" \
  --budget-amount=100USD
```

---

## 🎉 Success!

After successful deployment, your EasyShifts application will be available at:
- **Frontend**: `https://easyshifts-frontend-[hash]-uc.a.run.app`
- **Backend**: `https://easyshifts-backend-[hash]-uc.a.run.app`

The deployment scripts will provide the exact URLs upon completion.
