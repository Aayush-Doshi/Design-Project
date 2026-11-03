# API Monitoring System

This is a student project for monitoring APIs. It collects information about API response times and errors, looks for unusual changes, and can send alerts.

The project uses Python, MongoDB, Elasticsearch, and Kibana.

## What it does

- Collects API data
- Tracks response times and errors
- Finds unusual activity
- Shows results in Kibana dashboards
- Can send alerts by email or Slack

## What you need

- Python 3.8 or newer
- MongoDB
- Elasticsearch
- Kibana (optional, for dashboards)

## Setup

1. Clone this repository and open its folder.
2. Make a virtual environment and install the packages:

   ```bash
   python -m venv venv
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and add your own database and service settings. Keep the `.env` file private.

## Run it

On Windows, run:

```bat
start_cloud.bat
```

On Linux or macOS, run:

```bash
./start_cloud.sh
```

The app checks the database connection, starts the monitoring service, and collects demo data. The API docs are available at [http://localhost:8000/docs](http://localhost:8000/docs).

## Dashboards

Kibana usually opens at [http://localhost:5601](http://localhost:5601). The dashboards show API health, errors, and unusual activity.

![System architecture](system%20architecture.jpeg)

## Useful API links

- `/api/v1/apis` — list APIs
- `/api/v1/metrics` — view metrics
- `/api/v1/anomalies` — view unusual activity
- `/api/v1/predictions` — view predictions
- `/api/v1/alerts` — view alerts

## If something goes wrong

- Check that MongoDB and Elasticsearch are running and that your `.env` settings are correct.
- If there is no data, try running `python -m src.scripts.generate_test_data`.
- Check the messages printed in the terminal for errors.
