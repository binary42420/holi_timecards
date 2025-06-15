#!/bin/bash

# EasyShifts Docker Testing Script
# Test your Docker containers locally before deploying to Cloud Run

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🐳 EasyShifts Docker Testing${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Load environment variables
if [ -f Backend/.env ]; then
    export $(cat Backend/.env | grep -v '^#' | xargs)
fi

# Set database password for testing
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}🔐 Please enter your database password for testing:${NC}"
    read -s -p "Database Password: " DB_PASSWORD
    echo
    export DB_PASSWORD
fi

echo -e "${YELLOW}🏗️  Building Docker images...${NC}"

# Build backend image
echo -e "${BLUE}Building backend image...${NC}"
cd Backend
docker build -t easyshifts-backend:test .
cd ..

# Build frontend image
echo -e "${BLUE}Building frontend image...${NC}"
cd app
docker build -t easyshifts-frontend:test .
cd ..

echo -e "${GREEN}✅ Images built successfully${NC}"

# Test backend container
echo -e "${YELLOW}🧪 Testing backend container...${NC}"
docker run --rm -d \
    --name easyshifts-backend-test \
    -p 8080:8080 \
    -e GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" \
    -e DB_HOST="$DB_HOST" \
    -e DB_PORT="$DB_PORT" \
    -e DB_USER="$DB_USER" \
    -e DB_NAME="$DB_NAME" \
    -e DB_PASSWORD="$DB_PASSWORD" \
    easyshifts-backend:test

# Wait for backend to start
echo -e "${BLUE}Waiting for backend to start...${NC}"
sleep 10

# Check if backend is running
if docker ps | grep -q easyshifts-backend-test; then
    echo -e "${GREEN}✅ Backend container is running${NC}"
else
    echo -e "${RED}❌ Backend container failed to start${NC}"
    docker logs easyshifts-backend-test
    exit 1
fi

# Test frontend container
echo -e "${YELLOW}🧪 Testing frontend container...${NC}"
docker run --rm -d \
    --name easyshifts-frontend-test \
    -p 3000:80 \
    -e REACT_APP_GOOGLE_CLIENT_ID="$GOOGLE_CLIENT_ID" \
    -e REACT_APP_API_URL="ws://localhost:8080" \
    -e REACT_APP_ENV="development" \
    easyshifts-frontend:test

# Wait for frontend to start
echo -e "${BLUE}Waiting for frontend to start...${NC}"
sleep 5

# Check if frontend is running
if docker ps | grep -q easyshifts-frontend-test; then
    echo -e "${GREEN}✅ Frontend container is running${NC}"
else
    echo -e "${RED}❌ Frontend container failed to start${NC}"
    docker logs easyshifts-frontend-test
    docker stop easyshifts-backend-test
    exit 1
fi

echo -e "${GREEN}🎉 Both containers are running successfully!${NC}"
echo -e "${BLUE}Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}Backend: ws://localhost:8080${NC}"
echo ""
echo -e "${YELLOW}📋 Test your application, then press Enter to stop containers...${NC}"
read

# Stop containers
echo -e "${YELLOW}🛑 Stopping test containers...${NC}"
docker stop easyshifts-frontend-test easyshifts-backend-test

echo -e "${GREEN}✅ Testing completed${NC}"
echo -e "${BLUE}Your Docker images are ready for deployment!${NC}"
