import json

# 1. Visualization 1: Anomaly Severity Over Time (TSVB metric visualization)
vis_state_anomalies = {
    "title": "API Anomalies Severity",
    "type": "metrics",
    "params": {
        "id": "anomalies-severity-metric",
        "type": "timeseries",
        "series": [
            {
                "id": "severity-series",
                "color": "#E7664C",
                "split_mode": "terms",
                "terms_field": "api_id",
                "metrics": [{"id": "1", "type": "max", "field": "severity"}],
                "seperate_axis": 0,
                "axis_position": "right",
                "formatter": "number",
                "chart_type": "line",
                "line_width": 2,
                "point_size": 2,
                "fill": 0.3,
                "stacked": "none",
                "label": "Max Severity"
            }
        ],
        "time_field": "timestamp",
        "index_pattern": "anomalies*",
        "interval": "auto",
        "axis_position": "left",
        "axis_formatter": "number",
        "show_legend": 1,
        "show_grid": 1
    },
    "aggs": []
}

obj_vis1 = {
    "id": "local-api-anomalies-viz",
    "type": "visualization",
    "attributes": {
        "title": "API Anomalies Severity Over Time",
        "description": "Shows anomaly severity from the anomalies index",
        "version": 1,
        "visState": json.dumps(vis_state_anomalies),
        "uiStateJSON": "{}",
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": json.dumps({"query": {"query": "", "language": "kuery"}, "filter": []})
        }
    }
}

# 2. Visualization 2: Multi-Cloud Response Times (TSVB metric visualization)
vis_state_latency = {
    "title": "Multi-Cloud API Latency",
    "type": "metrics",
    "params": {
        "id": "api-latency-metric",
        "type": "timeseries",
        "series": [
            {
                "id": "latency-series",
                "color": "#54B399",
                "split_mode": "terms",
                "terms_field": "environment",
                "metrics": [{"id": "1", "type": "avg", "field": "response_time"}],
                "seperate_axis": 0,
                "axis_position": "left",
                "formatter": "number",
                "chart_type": "line",
                "line_width": 2,
                "point_size": 1,
                "fill": 0.2,
                "stacked": "none",
                "label": "Avg Response Time (ms)"
            }
        ],
        "time_field": "timestamp",
        "index_pattern": "api_metrics*",
        "interval": "auto",
        "axis_position": "left",
        "axis_formatter": "number",
        "show_legend": 1,
        "show_grid": 1
    },
    "aggs": []
}

obj_vis2 = {
    "id": "local-api-latency-viz",
    "type": "visualization",
    "attributes": {
        "title": "Multi-Cloud API Response Time",
        "description": "Shows average response time by cloud environment (AWS, Azure, GCP)",
        "version": 1,
        "visState": json.dumps(vis_state_latency),
        "uiStateJSON": "{}",
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": json.dumps({"query": {"query": "", "language": "kuery"}, "filter": []})
        }
    }
}

# 3. Dashboard combining both panels
panels = [
    {
        "panelIndex": "1",
        "gridData": {"x": 0, "y": 0, "w": 24, "h": 15, "i": "1"},
        "id": "local-api-latency-viz",
        "type": "visualization",
        "version": "7.10.0"
    },
    {
        "panelIndex": "2",
        "gridData": {"x": 24, "y": 0, "w": 24, "h": 15, "i": "2"},
        "id": "local-api-anomalies-viz",
        "type": "visualization",
        "version": "7.10.0"
    }
]

obj_dash = {
    "id": "local-api-monitoring-dashboard",
    "type": "dashboard",
    "attributes": {
        "title": "Multi-Cloud API Monitoring & Anomalies",
        "description": "Live dashboard for Multi-Cloud latency and AI detected anomalies",
        "hits": 0,
        "version": 1,
        "timeRestore": True,
        "timeFrom": "now-7d",
        "timeTo": "now",
        "refreshInterval": {"pause": False, "value": 10000},
        "optionsJSON": json.dumps({"hidePanelTitles": False, "useMargins": True}),
        "panelsJSON": json.dumps(panels),
        "kibanaSavedObjectMeta": {
            "searchSourceJSON": json.dumps({"query": {"query": "", "language": "kuery"}, "filter": []})
        }
    }
}

out_path = "kibana_imports/local_api_monitoring_dashboard.ndjson"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(json.dumps(obj_vis1) + "\n")
    f.write(json.dumps(obj_vis2) + "\n")
    f.write(json.dumps(obj_dash) + "\n")

print(f"Generated {out_path} successfully.")
