#!/bin/bash

# Update Cloud Run environment variables to fix Redis connection
echo "🚀 Updating EasyShifts Cloud Run Environment Variables"
echo "=================================================="

# Service configuration
PROJECT_ID="holitimecards"
REGION="us-central1"
SERVICE_NAME="holi-timesheets-backend"

echo "📋 Service: $SERVICE_NAME"
echo "📍 Region: $REGION"
echo "🏗️ Project: $PROJECT_ID"

# Load environment variables from .env.production
if [ -f ".env.production" ]; then
    echo "✅ Loading environment variables from .env.production"
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo "❌ .env.production file not found"
    exit 1
fi

echo ""
echo "🔧 Updating Cloud Run service with environment variables..."

# Update the Cloud Run service with environment variables
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --set-env-vars="DB_HOST=$DB_HOST,DB_PORT=$DB_PORT,DB_USER=$DB_USER,DB_NAME=$DB_NAME,DB_PASSWORD=$DB_PASSWORD,REDIS_HOST=$REDIS_HOST,REDIS_PORT=$REDIS_PORT,REDIS_PASSWORD=$REDIS_PASSWORD,REDIS_DB=$REDIS_DB,REDIS_MAX_CONNECTIONS=$REDIS_MAX_CONNECTIONS,REDIS_SOCKET_TIMEOUT=$REDIS_SOCKET_TIMEOUT,REDIS_CONNECT_TIMEOUT=$REDIS_CONNECT_TIMEOUT,SESSION_SECRET_KEY=$SESSION_SECRET_KEY,CSRF_SECRET_KEY=$CSRF_SECRET_KEY,SESSION_TIMEOUT_MINUTES=$SESSION_TIMEOUT_MINUTES,VALIDATE_SESSION_IP=$VALIDATE_SESSION_IP,PASSWORD_MIN_LENGTH=$PASSWORD_MIN_LENGTH,REQUIRE_PASSWORD_COMPLEXITY=$REQUIRE_PASSWORD_COMPLEXITY,HOST=$HOST,PORT=8080,ENVIRONMENT=$ENVIRONMENT,GOOGLE_CLIENT_ID=$GOOGLE_CLIENT_ID" \
    --quiet

if [ $? -eq 0 ]; then
    echo "✅ Cloud Run service updated successfully!"
    echo ""
    echo "⏳ Waiting for deployment to propagate..."
    sleep 10
    
    echo "🧪 Testing health endpoint..."
    HEALTH_URL="https://easyshifts-backend-794306818447.us-central1.run.app/health"
    
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$HEALTH_URL")
    
    if [ "$HTTP_STATUS" -eq 200 ]; then
        echo "✅ Health check passed!"
        echo ""
        echo "🎉 DEPLOYMENT SUCCESSFUL!"
        echo "The Redis connection issue should now be resolved."
        echo ""
        echo "🔌 WebSocket URL: wss://easyshifts-backend-794306818447.us-central1.run.app/ws"
        echo ""
        echo "Next steps:"
        echo "1. Test the frontend login"
        echo "2. Verify WebSocket connection"
        echo "3. Check session creation"
    else
        echo "❌ Health check failed (HTTP $HTTP_STATUS)"
        echo "Check the Cloud Run logs for more details."
    fi
else
    echo "❌ Cloud Run service update failed"
    exit 1
fi



