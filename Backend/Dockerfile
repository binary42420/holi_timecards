# Use Python 3.11 slim image for better compatibility
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies with proper cleanup
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Fix permissions for Windows Docker Desktop compatibility
# Create app user with proper permissions
RUN groupadd -r app && useradd -r -g app -d /app -s /bin/bash app \
    && chown -R app:app /app \
    && chmod -R 755 /app \
    && chmod +x /app/*.py

# Switch to non-root user for security
USER app

# Expose the port that the app runs on
EXPOSE 8080

# Environment variables for better Python behavior
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1

# Health check with better error handling
HEALTHCHECK --interval=30s --timeout=15s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run the application with proper signal handling
CMD ["python", "-u", "start_server_with_env.py"]
