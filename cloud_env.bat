@echo off
rem Cloud environment configuration for API Monitoring System

rem Debug and logging settings
set DEBUG=False
set LOG_LEVEL=INFO
set HOST=0.0.0.0
set PORT=8000

rem Skip Kibana initialization
set SKIP_KIBANA_INIT=True



rem Redis settings (default to localhost since we're focusing on MongoDB and Elasticsearch)
set REDIS_HOST=localhost
set REDIS_PORT=6379

echo Environment variables set for cloud operation 
rem Credentials are loaded from the local .env file by the application.
