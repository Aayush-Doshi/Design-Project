"""
Script to create API sources for different environments.
"""
import asyncio
import logging
import os
from datetime import datetime
from typing import List, Dict

from src.models.api import ApiSource, Environment, Endpoint
from src.storage.database import get_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_api_sources() -> None:
    """Create API sources for different environments."""
    # Load environment variables from .env instead of hardcoding credentials
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded configuration from .env")
    
    # Get database instance
    db = get_database()
    # Connect to the database
    await db.connect()
    
    # Define API sources
    api_sources: List[ApiSource] = [
        ApiSource(
            id="aws-api-1",
            name="AWS Payment API",
            description="Payment processing service hosted on AWS",
            base_url="https://api.aws.example.com",
            endpoint="https://api.aws.example.com/health",
            environment=Environment.AWS,
            endpoints=[
                Endpoint(
                    path="/api/v1/payments",
                    method="POST",
                    expected_response_time=200,
                    timeout=5000,
                    description="Process payment transaction"
                ),
                Endpoint(
                    path="/api/v1/payments/{id}",
                    method="GET",
                    expected_response_time=100,
                    timeout=3000,
                    description="Get payment status"
                )
            ],
            headers={"Content-Type": "application/json"},
            auth_type="bearer",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ApiSource(
            id="azure-api-1",
            name="Azure User Service",
            description="User management service hosted on Azure",
            base_url="https://api.azure.example.com",
            endpoint="https://api.azure.example.com/health",
            environment=Environment.AZURE,
            endpoints=[
                Endpoint(
                    path="/api/v1/users",
                    method="GET",
                    expected_response_time=150,
                    timeout=3000,
                    description="Get user list"
                ),
                Endpoint(
                    path="/api/v1/users/{id}",
                    method="PUT",
                    expected_response_time=250,
                    timeout=5000,
                    description="Update user profile"
                )
            ],
            headers={"Content-Type": "application/json"},
            auth_type="bearer",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ApiSource(
            id="gcp-api-1",
            name="GCP Analytics API",
            description="Analytics service hosted on GCP",
            base_url="https://api.gcp.example.com",
            endpoint="https://api.gcp.example.com/health",
            environment=Environment.GCP,
            endpoints=[
                Endpoint(
                    path="/api/v1/metrics",
                    method="GET",
                    expected_response_time=300,
                    timeout=5000,
                    description="Get analytics metrics"
                ),
                Endpoint(
                    path="/api/v1/reports",
                    method="POST",
                    expected_response_time=400,
                    timeout=8000,
                    description="Generate analytics report"
                )
            ],
            headers={"Content-Type": "application/json"},
            auth_type="bearer",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    # Insert API sources into database
    for api_source in api_sources:
        try:
            await db.store_api_source(api_source)
            logger.info(f"Created API source: {api_source.name}")
        except Exception as e:
            logger.error(f"Failed to create API source {api_source.name}: {str(e)}")
            raise

async def main():
    """Main function to create API sources."""
    try:
        await create_api_sources()
        logger.info("Successfully created all API sources")
    except Exception as e:
        logger.error(f"Failed to create API sources: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 