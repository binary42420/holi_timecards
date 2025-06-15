# Multi-stage build for React app with Windows Docker Desktop optimization
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies with better error handling
RUN npm ci --only=production=false \
    && npm cache clean --force

# Copy source code
COPY . .

# Create optimized production build
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built app from build stage with proper permissions
COPY --from=build --chown=nginx:nginx /app/build /usr/share/nginx/html

# Copy environment script with proper permissions
COPY env.sh /docker-entrypoint.d/10-env.sh
RUN chmod +x /docker-entrypoint.d/10-env.sh \
    && chown nginx:nginx /docker-entrypoint.d/10-env.sh

# Create nginx user directories with proper permissions
RUN mkdir -p /var/cache/nginx/client_temp \
    && mkdir -p /var/cache/nginx/proxy_temp \
    && mkdir -p /var/cache/nginx/fastcgi_temp \
    && mkdir -p /var/cache/nginx/uwsgi_temp \
    && mkdir -p /var/cache/nginx/scgi_temp \
    && chown -R nginx:nginx /var/cache/nginx \
    && chown -R nginx:nginx /usr/share/nginx/html \
    && chmod -R 755 /usr/share/nginx/html

# Set environment variables
ENV PORT=8080
ENV NGINX_ENVSUBST_OUTPUT_DIR=/etc/nginx/conf.d

# Expose port
EXPOSE $PORT

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:$PORT/ || exit 1

# Start nginx with proper signal handling
CMD ["nginx", "-g", "daemon off;"]
