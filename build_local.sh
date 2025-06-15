#!/bin/bash
# Comprehensive script to build both frontend and backend Docker images locally with Docker Desktop
# Usage: bash build_local.sh

set -e

# Paths
FRONTEND_DIR="app"
BACKEND_DIR="Backend"
FRONTEND_IMAGE="holi-timecards-app:local"
BACKEND_IMAGE="holi-timecards-backend:local"

# Build Frontend
if [ -f "$FRONTEND_DIR/Dockerfile" ]; then
  echo "\n==== Building Frontend Docker Image ===="
  docker build -t $FRONTEND_IMAGE $FRONTEND_DIR
else
  echo "[ERROR] No Dockerfile found in $FRONTEND_DIR."
  exit 1
fi

# Build Backend
if [ -f "$BACKEND_DIR/Dockerfile" ]; then
  echo "\n==== Building Backend Docker Image ===="
  docker build -t $BACKEND_IMAGE $BACKEND_DIR
else
  echo "[ERROR] No Dockerfile found in $BACKEND_DIR."
  exit 1
fi

# Show built images

echo "\n==== Built Docker Images ===="
docker images | grep 'holi-timecards-'

echo "\n==== To run containers locally: ===="
echo "docker run --rm -p 3000:3000 $FRONTEND_IMAGE" # Adjust port as needed
echo "docker run --rm -p 8000:8000 $BACKEND_IMAGE"   # Adjust port as needed
