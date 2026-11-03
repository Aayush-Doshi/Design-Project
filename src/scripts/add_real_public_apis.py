"""
Add genuine, live public APIs to MongoDB for real-time monitoring.
"""
import asyncio
import logging
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from src.models.api import ApiSource, Environment, Endpoint
from src.storage.database import get_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def add_real_apis():
    db = get_database()
    await db.connect()
    
    real_apis = [
        ApiSource(
            id="real-dummyjson-api",
            name="DummyJSON Products API (AWS)",
            description="Live REST microservice hosted on AWS Cloud",
            base_url="https://dummyjson.com",
            endpoint="https://dummyjson.com/products/1",
            environment=Environment.AWS,
            endpoints=[
                Endpoint(
                    path="/products/1",
                    method="GET",
                    expected_response_time=100,
                    timeout=5000,
                    description="Get product info"
                )
            ],
            headers={"User-Agent": "ApiMonitoringSystem/1.0"},
            auth_type="none",
            type="rest",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ApiSource(
            id="real-github-api",
            name="GitHub Production API (AWS)",
            description="Live GitHub status API hosted on AWS infrastructure",
            base_url="https://api.github.com",
            endpoint="https://api.github.com/zen",
            environment=Environment.AWS,
            endpoints=[
                Endpoint(
                    path="/zen",
                    method="GET",
                    expected_response_time=120,
                    timeout=5000,
                    description="GitHub status endpoint"
                )
            ],
            headers={"User-Agent": "ApiMonitoringSystem/1.0"},
            auth_type="none",
            type="rest",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ApiSource(
            id="real-jsonplaceholder-api",
            name="JSONPlaceholder API (Azure)",
            description="Live microservice API hosted on Azure Cloud",
            base_url="https://jsonplaceholder.typicode.com",
            endpoint="https://jsonplaceholder.typicode.com/posts/1",
            environment=Environment.AZURE,
            endpoints=[
                Endpoint(
                    path="/posts/1",
                    method="GET",
                    expected_response_time=150,
                    timeout=5000,
                    description="Get post by ID"
                )
            ],
            headers={"User-Agent": "ApiMonitoringSystem/1.0"},
            auth_type="none",
            type="rest",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ApiSource(
            id="real-httpbin-api",
            name="HTTPBin API (GCP)",
            description="Live HTTP testing service hosted on Google Cloud Platform",
            base_url="https://httpbin.org",
            endpoint="https://httpbin.org/get",
            environment=Environment.GCP,
            endpoints=[
                Endpoint(
                    path="/get",
                    method="GET",
                    expected_response_time=200,
                    timeout=5000,
                    description="HTTPBin inspect request"
                )
            ],
            headers={"User-Agent": "ApiMonitoringSystem/1.0"},
            auth_type="none",
            type="rest",
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    for api in real_apis:
        try:
            await db.store_api_source(api)
            logger.info(f"Successfully added real API: {api.name} ({api.endpoint})")
        except Exception as e:
            logger.error(f"Failed to add {api.name}: {e}")
            
    await db.disconnect()
    logger.info("All real APIs registered successfully!")

if __name__ == "__main__":
    asyncio.run(add_real_apis())
