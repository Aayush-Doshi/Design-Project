import asyncio
from dotenv import load_dotenv
load_dotenv()

from src.storage.database import get_database

async def sync():
    db = get_database()
    await db.connect()
    
    if not db.mongo_available:
        print("MongoDB is not available!")
        return
    if not db.es_available:
        print("Elasticsearch is not available!")
        return

    # Fetch all anomalies from MongoDB
    cursor = db.mongo_db.anomalies.find({})
    anomalies = await cursor.to_list(length=5000)
    print(f"Found {len(anomalies)} anomalies in MongoDB.")
    
    if not anomalies:
        print("No anomalies to sync.")
        return
        
    bulk_ops = []
    for a in anomalies:
        a_id = str(a.get("id", a.get("_id")))
        ts = a.get("timestamp")
        if hasattr(ts, "isoformat"):
            ts_str = ts.isoformat()
        else:
            ts_str = str(ts)
            
        env = a.get("environment", "")
        if hasattr(env, "value"):
            env = env.value
            
        bulk_ops.append({"index": {"_index": "anomalies", "_id": a_id}})
        bulk_ops.append({
            "id": a_id,
            "timestamp": ts_str,
            "api_id": a.get("api_id", ""),
            "type": a.get("type", ""),
            "severity": float(a.get("severity", 0.0)),
            "description": a.get("description", ""),
            "environment": str(env),
            "context": a.get("context", {})
        })
        
    if bulk_ops:
        res = await db.es_client.bulk(operations=bulk_ops)
        print(f"Successfully synced {len(anomalies)} anomalies to Elasticsearch index 'anomalies'!")
        
    await db.disconnect()

if __name__ == "__main__":
    asyncio.run(sync())
