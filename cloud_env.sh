#!/bin/bash
# Cloud environment configuration for API Monitoring System

# Debug and logging settings
export DEBUG=False
export LOG_LEVEL=INFO
export HOST=0.0.0.0
export PORT=8000

# Skip Kibana initialization
export SKIP_KIBANA_INIT=True



# Redis settings (default to localhost since we're focusing on MongoDB and Elasticsearch)
export REDIS_HOST=localhost
export REDIS_PORT=6379

echo "Environment variables set for cloud operation" 
# Credentials are loaded from the local .env file by the application.
