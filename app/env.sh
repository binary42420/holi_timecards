#!/bin/sh

# Replace environment variables in built files and nginx config
# This allows runtime configuration of the React app

echo "=== HOLI Timesheets Environment Configuration ==="
echo "PORT: ${PORT:-8080}"
echo "REACT_APP_GOOGLE_CLIENT_ID: ${REACT_APP_GOOGLE_CLIENT_ID}"
echo "REACT_APP_API_URL: ${REACT_APP_API_URL}"
echo "REACT_APP_ENV: ${REACT_APP_ENV}"

# Set default PORT if not provided
PORT=${PORT:-8080}

# Replace PORT in nginx config
echo "Configuring nginx to listen on port $PORT"
sed -i "s/PORT_PLACEHOLDER/$PORT/g" /etc/nginx/conf.d/default.conf

# Verify the nginx config was updated
echo "Nginx configuration:"
cat /etc/nginx/conf.d/default.conf | head -5

# Create a temporary file with environment variables
cat <<EOF > /tmp/env-config.js
// Runtime environment configuration for HOLI Timesheets
// This file is loaded by index.html and provides environment variables at runtime
window._env_ = {
  REACT_APP_GOOGLE_CLIENT_ID: "${REACT_APP_GOOGLE_CLIENT_ID}",
  REACT_APP_API_URL: "${REACT_APP_API_URL}",
  REACT_APP_ENV: "${REACT_APP_ENV}"
};

// Global logging fallback to prevent "logError is not defined" errors
if (typeof window !== 'undefined' && !window.logError) {
  window.logError = function(component, message, error) {
    const timestamp = new Date().toISOString();
    const logMessage = '[' + timestamp + '] [ERROR] [' + component + '] ' + message;
    console.error(logMessage, error || '');
  };

  window.logDebug = function(component, message, data) {
    const timestamp = new Date().toISOString();
    const logMessage = '[' + timestamp + '] [DEBUG] [' + component + '] ' + message;
    console.log(logMessage, data || '');
  };

  window.logWarning = function(component, message, data) {
    const timestamp = new Date().toISOString();
    const logMessage = '[' + timestamp + '] [WARNING] [' + component + '] ' + message;
    console.warn(logMessage, data || '');
  };

  window.logInfo = function(component, message, data) {
    const timestamp = new Date().toISOString();
    const logMessage = '[' + timestamp + '] [INFO] [' + component + '] ' + message;
    console.info(logMessage, data || '');
  };
}

// Debug logging
console.log('env-config.js loaded:', window._env_);
EOF

# Copy the environment config to the nginx html directory
cp /tmp/env-config.js /usr/share/nginx/html/env-config.js

echo "Runtime environment configuration updated:"
cat /usr/share/nginx/html/env-config.js | head -10

echo "Environment variables configured for runtime"
echo "Nginx configured to listen on port $PORT"
