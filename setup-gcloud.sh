#!/bin/bash

# EasyShifts Google Cloud Setup Script
# This script sets up your Google Cloud environment for EasyShifts deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 EasyShifts Google Cloud Setup${NC}"
echo -e "${BLUE}This script will help you set up Google Cloud for EasyShifts deployment${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed.${NC}"
    echo -e "${YELLOW}Please install it from: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# Get project ID
echo -e "${YELLOW}📋 Please enter your Google Cloud Project ID:${NC}"
read -p "Project ID: " PROJECT_ID

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Project ID cannot be empty${NC}"
    exit 1
fi

# Get region
echo -e "${YELLOW}🌍 Please enter your preferred region (default: us-central1):${NC}"
read -p "Region: " REGION
REGION=${REGION:-us-central1}

# Get database password
echo -e "${YELLOW}🔐 Please enter your database password:${NC}"
read -s -p "Database Password: " DB_PASSWORD
echo

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}❌ Database password cannot be empty${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Configuration collected${NC}"
echo -e "${BLUE}Project ID: ${PROJECT_ID}${NC}"
echo -e "${BLUE}Region: ${REGION}${NC}"

# Authenticate with gcloud
echo -e "${YELLOW}🔐 Authenticating with Google Cloud...${NC}"
gcloud auth login

# Set the project
echo -e "${YELLOW}📋 Setting project to ${PROJECT_ID}${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create database password secret
echo -e "${YELLOW}🔐 Creating database password secret...${NC}"
echo -n "$DB_PASSWORD" | gcloud secrets create db-password --data-file=-

# Create service account
echo -e "${YELLOW}👤 Creating service account...${NC}"
gcloud iam service-accounts create easyshifts-sa \
    --display-name="EasyShifts Service Account" \
    --description="Service account for EasyShifts application" || true

# Grant necessary permissions
SERVICE_ACCOUNT="easyshifts-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo -e "${YELLOW}🔑 Granting permissions...${NC}"
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/cloudsql.client"

# Update deployment script with project details
echo -e "${YELLOW}📝 Updating deployment script...${NC}"
sed -i.bak "s/PROJECT_ID=\"your-project-id\"/PROJECT_ID=\"${PROJECT_ID}\"/" deploy.sh
sed -i.bak "s/REGION=\"us-central1\"/REGION=\"${REGION}\"/" deploy.sh

# Update Cloud Run YAML files
echo -e "${YELLOW}📝 Updating Cloud Run configurations...${NC}"
sed -i.bak "s/PROJECT_ID/${PROJECT_ID}/g" cloudrun-backend.yaml
sed -i.bak "s/PROJECT_ID/${PROJECT_ID}/g" cloudrun-frontend.yaml

echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
echo -e "${GREEN}✅ APIs enabled${NC}"
echo -e "${GREEN}✅ Service account created${NC}"
echo -e "${GREEN}✅ Database password stored in Secret Manager${NC}"
echo -e "${GREEN}✅ Deployment scripts updated${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo -e "${BLUE}1. Make sure your Google OAuth settings include your Cloud Run URLs${NC}"
echo -e "${BLUE}2. Run: chmod +x deploy.sh${NC}"
echo -e "${BLUE}3. Run: ./deploy.sh${NC}"
echo ""
echo -e "${YELLOW}🔗 Important URLs to add to Google OAuth:${NC}"
echo -e "${BLUE}   - https://easyshifts-frontend-HASH-uc.a.run.app${NC}"
echo -e "${BLUE}   - https://easyshifts-backend-HASH-uc.a.run.app${NC}"
