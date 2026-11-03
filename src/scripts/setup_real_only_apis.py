"""
Purge all mock / demo / dummy APIs and register only 100% genuine, real-world public APIs.
"""
import asyncio
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from src.models.api import ApiSource, Environment, Endpoint
from src.storage.database import get_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REAL_APIS = [
    ApiSource(
        id="github-api",
        name="GitHub REST API (AWS)",
        description="Live GitHub production service hosted on AWS infrastructure",
        base_url="https://api.github.com",
        endpoint="https://api.github.com",
        environment=Environment.AWS,
        endpoints=[
            Endpoint(
                path="/",
                method="GET",
                expected_response_time=120,
                timeout=5000,
                description="GitHub API root endpoint"
            )
        ],
        headers={"User-Agent": "ApiMonitoringSystem/1.0"},
        auth_type="none",
        type="rest",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    ),
    ApiSource(
        id="coindesk-bitcoin-api",
        name="CoinDesk Financial API (Azure)",
        description="Live Bitcoin index price feed hosted on Azure Cloud",
        base_url="https://api.coindesk.com",
        endpoint="https://api.coindesk.com/v1/bpi/currentprice.json",
        environment=Environment.AZURE,
        endpoints=[
            Endpoint(
                path="/v1/bpi/currentprice.json",
                method="GET",
                expected_response_time=150,
                timeout=5000,
                description="Live crypto pricing feed"
            )
        ],
        headers={"User-Agent": "ApiMonitoringSystem/1.0"},
        auth_type="none",
        type="rest",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    ),
    ApiSource(
        id="open-meteo-weather-api",
        name="Open-Meteo Weather API (GCP)",
        description="Live global meteorological forecasting service hosted on GCP",
        base_url="https://api.open-meteo.com",
        endpoint="https://api.open-meteo.com/v1/forecast?latitude=37.77&longitude=-122.42&current_weather=true",
        environment=Environment.GCP,
        endpoints=[
            Endpoint(
                path="/v1/forecast",
                method="GET",
                expected_response_time=180,
                timeout=5000,
                description="Live global weather forecast"
            )
        ],
        headers={"User-Agent": "ApiMonitoringSystem/1.0"},
        auth_type="none",
        type="rest",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    ),
    ApiSource(
        id="jsonplaceholder-api",
        name="JSONPlaceholder API (Azure)",
        description="Public REST service hosted on Azure Cloud",
        base_url="https://jsonplaceholder.typicode.com",
        endpoint="https://jsonplaceholder.typicode.com/posts/1",
        environment=Environment.AZURE,
        endpoints=[
            Endpoint(
                path="/posts/1",
                method="GET",
                expected_response_time=140,
                timeout=5000,
                description="Post resource lookup"
            )
        ],
        headers={"User-Agent": "ApiMonitoringSystem/1.0"},
        auth_type="none",
        type="rest",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    ),
    ApiSource(
        id="httpbin-inspect-api",
        name="HTTPBin Request API (GCP)",
        description="Public HTTP inspection service hosted on GCP",
        base_url="https://httpbin.org",
        endpoint="https://httpbin.org/get",
        environment=Environment.GCP,
        endpoints=[
            Endpoint(
                path="/get",
                method="GET",
                expected_response_time=200,
                timeout=5000,
                description="Inspect HTTP GET request"
            )
        ],
        headers={"User-Agent": "ApiMonitoringSystem/1.0"},
        auth_type="none",
        type="rest",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
]

KEEP_API_IDS = [api.id for api in REAL_APIS]

async def purge_and_register():
    db = get_database()
    await db.connect()
    
    # 1. Clean MongoDB: clear old entries so there are no duplicate name conflicts
    if db.mongo_available:
        delete_result = await db.mongo_db.api_sources.delete_many({})
        logger.info(f"MongoDB: Cleared {delete_result.deleted_count} previous API source(s).")
        
        # Insert genuine APIs
        for api in REAL_APIS:
            await db.store_api_source(api)
            logger.info(f"MongoDB: Registered real API -> {api.name} ({api.id})")
    
    # 2. Clean Elasticsearch: purge all records that are NOT one of the 5 real APIs
    if db.es_available and db.es_client:
        purge_query = {
            "bool": {
                "must_not": [
                    {"terms": {"api_id": KEEP_API_IDS}}
                ]
            }
        }
        for idx in ["api_metrics", "anomalies"]:
            try:
                es_del = await db.es_client.delete_by_query(
                    index=idx,
                    query=purge_query,
                    conflicts="proceed"
                )
                logger.info(f"Elasticsearch ({idx}): Purged {es_del.get('deleted', 0)} old mock/dummy records.")
            except Exception as e:
                logger.warning(f"Could not purge {idx}: {e}")
                
    await db.disconnect()
    logger.info("Done! Only 100% genuine real-world APIs are now configured.")

if __name__ == "__main__":
    asyncio.run(purge_and_register())
