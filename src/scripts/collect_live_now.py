"""
Live real-time public API metrics collector.
Pings ONLY genuine, production public APIs (GitHub, CoinDesk, Open-Meteo Weather, JSONPlaceholder, HTTPBin)
and indexes live telemetry directly into Elasticsearch.
"""
import asyncio
import logging
import aiohttp
import time
import uuid
import sys
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

from src.models.api import ApiMetric, Environment
from src.storage.database import get_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

TARGETS = [
    {
        "api_id": "github-api",
        "name": "GitHub Production API (AWS)",
        "url": "https://api.github.com",
        "environment": Environment.AWS
    },
    {
        "api_id": "coindesk-bitcoin-api",
        "name": "CoinDesk Bitcoin Price API (Azure)",
        "url": "https://api.coindesk.com/v1/bpi/currentprice.json",
        "environment": Environment.AZURE
    },
    {
        "api_id": "open-meteo-weather-api",
        "name": "Open-Meteo Global Weather API (GCP)",
        "url": "https://api.open-meteo.com/v1/forecast?latitude=37.77&longitude=-122.42&current_weather=true",
        "environment": Environment.GCP
    },
    {
        "api_id": "jsonplaceholder-api",
        "name": "JSONPlaceholder API (Azure)",
        "url": "https://jsonplaceholder.typicode.com/posts/1",
        "environment": Environment.AZURE
    },
    {
        "api_id": "httpbin-inspect-api",
        "name": "HTTPBin Request API (GCP)",
        "url": "https://httpbin.org/get",
        "environment": Environment.GCP
    }
]

async def collect_once(db, session):
    headers = {"User-Agent": "ApiMonitoringSystem/1.0"}
    metrics = []
    
    for target in TARGETS:
        start = time.time()
        try:
            async with session.get(target["url"], headers=headers) as resp:
                latency = (time.time() - start) * 1000
                status = resp.status
                success = (status < 400)
                logger.info(f"[{status} {'OK' if success else 'ERR'}] {target['name']}: {latency:.1f}ms")
        except Exception as e:
            latency = (time.time() - start) * 1000
            status = 503
            success = False
            logger.warning(f"[503 ERR] {target['name']}: {e}")
            
        metric = ApiMetric(
            id=f"metric-{uuid.uuid4()}",
            api_id=target["api_id"],
            endpoint=target["url"],
            method="GET",
            response_time=round(latency, 2),
            status_code=status,
            success=success,
            error=not success,
            environment=target["environment"],
            timestamp=datetime.now(timezone.utc)
        )
        metrics.append(metric)
        
    if metrics:
        await db.store_metrics(metrics)
        logger.info(f"Stored {len(metrics)} real live metrics into Elasticsearch (api_metrics).\n")

async def main():
    continuous = "--continuous" in sys.argv or "-c" in sys.argv
    db = get_database()
    await db.connect()
    
    logger.info("=" * 65)
    logger.info("Real API Live Monitor Initialized (Zero Mocks / Zero Dummies)")
    logger.info("Services: GitHub, CoinDesk Crypto, Open-Meteo Weather, JSONPlaceholder, HTTPBin")
    logger.info(f"Mode: {'CONTINUOUS (every 5 seconds, press Ctrl+C to stop)' if continuous else 'SINGLE RUN (use --continuous to loop)'}")
    logger.info("=" * 65)
    
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            if continuous:
                while True:
                    await collect_once(db, session)
                    await asyncio.sleep(5)
            else:
                await collect_once(db, session)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("Monitoring stopped by user.")
    finally:
        await db.disconnect()
        logger.info("Database connection closed cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
