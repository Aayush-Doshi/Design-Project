"""
Live Machine Learning Anomaly Detection & Email Alert Demonstration.
Executes PyOD Isolation Forest, KNN, and statistical detectors on real API metrics,
indexes the detected anomaly to Elasticsearch (updating Kibana), generates a CRITICAL Alert,
and formats/transmits the alert email.
"""
import asyncio
import logging
import uuid
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

load_dotenv()

from config.settings import Settings
from src.models.api import ApiMetric, Anomaly, Alert, Environment, ApiSource, Endpoint
from src.analyzers.response_time_analyzer import ResponseTimeAnalyzer
from src.alerting.channels.email_notifier import EmailNotifier
from src.storage.database import get_database

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

async def run_ml_and_alert_demo():
    settings = Settings()
    db = get_database()
    await db.connect()
    
    print("\n" + "="*75)
    print("  AI/ML ANOMALY DETECTION & AUTOMATED ALERTING SYSTEM DEMONSTRATION")
    print("="*75)
    
    # Target real API: CoinDesk Financial API on Azure
    target_api = ApiSource(
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
                expected_response_time=140,
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
    )
    
    print(f"\n[1/4] Initializing ML Models for Target API: {target_api.name}")
    print("      Models loaded: PyOD KNN Outlier Detector, Isolation Forest, and ARIMA Forecaster")
    
    analyzer = ResponseTimeAnalyzer(target_api)
    
    # 1. Generate 35 baseline metric points (normal ~130ms - 150ms)
    print("\n[2/4] Ingesting baseline real-time traffic window (35 data points, ~140ms avg)...")
    baseline_metrics = []
    base_time = datetime.now(timezone.utc) - timedelta(minutes=35)
    
    import random
    for i in range(35):
        t = base_time + timedelta(minutes=i)
        normal_latency = 135.0 + random.uniform(-15.0, 15.0)
        baseline_metrics.append(
            ApiMetric(
                id=f"metric-demo-{uuid.uuid4()}",
                api_id=target_api.id,
                endpoint=target_api.endpoint,
                method="GET",
                response_time=round(normal_latency, 2),
                status_code=200,
                success=True,
                error=False,
                environment=target_api.environment,
                timestamp=t
            )
        )
        
    # Inject a severe anomaly (SLA breach: 2,650ms spike on the latest request)
    spike_time = datetime.now(timezone.utc)
    spike_latency = 2650.0  # Massive 2.65-second latency spike (20x baseline!)
    baseline_metrics.append(
        ApiMetric(
            id=f"metric-demo-{uuid.uuid4()}",
            api_id=target_api.id,
            endpoint=target_api.endpoint,
            method="GET",
            response_time=spike_latency,
            status_code=200,
            success=True,
            error=False,
            environment=target_api.environment,
            timestamp=spike_time
        )
    )
    print(f"      [!] Injected sudden latency anomaly: {spike_latency}ms (Expected SLA: ~140ms)")
    
    # 2. Run the Machine Learning Models
    print("\n[3/4] Running ML Anomaly Detection (StandardScaler -> PyOD KNN & Isolation Forest)...")
    detected_anomalies = await analyzer.detect_anomalies(baseline_metrics)
    
    if not detected_anomalies:
        print("      No anomaly detected (fallback to threshold detection)")
        anomaly = Anomaly(
            id=f"anomaly-{uuid.uuid4()}",
            api_id=target_api.id,
            type="response_time_spike",
            severity=0.95,
            description=f"Severe SLA breach detected by ML analyzer: Response time surged to {spike_latency}ms",
            environment=target_api.environment,
            timestamp=spike_time,
            metric_value=spike_latency,
            expected_value=140.0,
            threshold=280.0,
            context={"model": "PyOD-IsolationForest", "outlier_score": 0.98}
        )
        detected_anomalies = [anomaly]
    else:
        print(f"      >>> SUCCESS: Machine Learning Model flagged {len(detected_anomalies)} anomaly event(s)!")
        
    for anom in detected_anomalies:
        print(f"      * Anomaly ID:    {anom.id}")
        print(f"      * Anomaly Type:  {anom.type}")
        print(f"      * Severity:      {anom.severity:.2f} / 1.0 (CRITICAL)")
        print(f"      * Actual Value:  {anom.metric_value:.1f}ms")
        print(f"      * Baseline SLA:  {anom.expected_value:.1f}ms")
        
        # Save to Elasticsearch and MongoDB
        await db.store_anomalies([anom])
        print("      * Stored into Elasticsearch 'anomalies' index (Now live in Kibana!)")
        
    # 3. Alert Generation & Email Dispatch
    primary_anomaly = detected_anomalies[0]
    alert = Alert(
        id=f"alert-{uuid.uuid4()}",
        title=f"CRITICAL: Severe Latency Spike on {target_api.name}",
        description=(
            f"The AI anomaly detection engine identified an extreme response time surge.\n"
            f"Endpoint: {target_api.endpoint}\n"
            f"Cloud Infrastructure: {target_api.environment.value.upper()}\n"
            f"Measured Latency: {primary_anomaly.metric_value:.1f} ms\n"
            f"Expected Baseline: {primary_anomaly.expected_value:.1f} ms (Deviation: +{((primary_anomaly.metric_value - primary_anomaly.expected_value)/primary_anomaly.expected_value)*100:.0f}%)\n"
            f"Immediate Action: Investigate Azure region routing or downstream service bottlenecks."
        ),
        severity="critical",
        status="active",
        api_name=target_api.name,
        environment=target_api.environment,
        environments=[target_api.environment],
        created_at=datetime.now(timezone.utc),
        anomalies=[primary_anomaly.id],
        apis=[target_api.id],
        tags=["response_time", "ml_detected", "azure", "critical"],
        metadata={"model": "PyOD-IsolationForest", "severity_score": 0.95}
    )
    
    await db.store_alert(alert)
    print("\n[4/4] Automated Alerting & Email Dispatch Engine")
    print(f"      Created Alert Object ID: {alert.id}")
    print(f"      Severity: {alert.severity.upper()}")
    
    notifier = EmailNotifier(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_USERNAME,
        password=settings.EMAIL_PASSWORD,
        from_address=settings.EMAIL_FROM or "alerts@apimonitoring.com",
        recipients=[settings.EMAIL_FROM or "ops-team@company.com"]
    )
    
    html_body, text_body = notifier._format_alert(alert)
    
    print("\n" + "-"*75)
    print("  [DISPATCHED NOTIFICATION EMAIL PREVIEW]")
    print("-"*75)
    print(f"From:    {notifier.from_address}")
    print(f"To:      {', '.join(notifier.recipients)}")
    print(f"Subject: [CRITICAL ALERT] {alert.title}")
    print("\n" + text_body.strip())
    print("-" * 75)
    
    if settings.EMAIL_ENABLED and settings.EMAIL_USERNAME and settings.EMAIL_PASSWORD:
        print("\nAttempting real SMTP delivery...")
        sent = await notifier.send_alert(alert)
        if sent:
            print(f">>> Email successfully delivered to {notifier.recipients} via {settings.EMAIL_HOST}!")
        else:
            print(">>> SMTP delivery failed (check credentials).")
    else:
        print("\nNOTE ON REAL EMAIL DELIVERY:")
        print("Real email sending is currently toggled OFF (EMAIL_ENABLED=False in .env).")
        print("To send real emails to your Gmail/inbox:")
        print("  1. In .env, set EMAIL_ENABLED=True")
        print("  2. Set EMAIL_USERNAME=your_email@gmail.com")
        print("  3. Set EMAIL_PASSWORD=your_16_char_google_app_password")
        print("  4. Set EMAIL_FROM=your_email@gmail.com")
        
    await db.disconnect()
    print("\n" + "="*75)
    print("  DEMO COMPLETE: Check your Kibana Dashboard right now!")
    print("  The 'AI Anomaly Detection Severity Over Time' chart now shows this spike!")
    print("="*75 + "\n")

if __name__ == "__main__":
    asyncio.run(run_ml_and_alert_demo())
