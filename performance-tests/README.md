# Performance Tests with K6

This directory contains K6 performance tests for the notes API.

## Prerequisites

- Install K6: https://k6.io/docs/getting-started/installation/

## Running Tests

### Basic Run

```bash
k6 run script.js
```

### With Custom Configuration

```bash
BASE_URL=http://localhost:5000 API_USER=admin API_PASSWORD=password k6 run script.js
```

### With Output to File

```bash
k6 run --out json=results.json script.js
```

### Load Test Configuration

The test script includes a staged load test that:
- Ramps up to 10 virtual users over 30 seconds
- Maintains 10 users for 1 minute
- Ramps up to 20 users over 30 seconds
- Maintains 20 users for 1 minute
- Ramps down to 0 users over 30 seconds

You can modify the `options.stages` in `script.js` to customize the load pattern.

## Getting and Analyzing Reports

### 1. Console Output

K6 displays a real-time summary in the console showing:
- Request duration (min, max, avg, p95, p99)
- Request rate
- Error rate
- Number of iterations
- Custom metrics

### 2. JSON Output

Generate a JSON report:

```bash
k6 run --out json=results.json script.js
```

Then analyze the JSON file programmatically or use tools like:
- `jq` for command-line JSON processing
- Python scripts to parse and visualize data
- Excel/Google Sheets for manual analysis

### 3. Cloud Results (K6 Cloud)

For detailed analytics and visualization, push results to K6 Cloud:

```bash
# First, get a K6 Cloud API token from https://app.k6.io
export K6_CLOUD_TOKEN=your-token-here
k6 cloud script.js
```

Access detailed reports at: https://app.k6.io

### 4. InfluxDB + Grafana

For real-time monitoring and historical analysis:

```bash
# Run K6 and send metrics to InfluxDB
k6 run --out influxdb=http://localhost:8086/k6 script.js
```

Then visualize in Grafana using K6 dashboard templates.

### 5. Custom Analysis Script

Example Python script to analyze JSON results:

```python
import json

with open('results.json', 'r') as f:
    data = json.load(f)

# Analyze metrics
metrics = data['metrics']
print(f"Total requests: {metrics['http_reqs']['values']['count']}")
print(f"Avg duration: {metrics['http_req_duration']['values']['avg']:.2f}ms")
print(f"Error rate: {metrics['http_req_failed']['values']['rate']*100:.2f}%")
```

## Key Metrics Explained

- **http_req_duration**: Time taken for each HTTP request
- **http_req_failed**: Rate of failed requests (status >= 400)
- **iterations**: Number of complete test iterations
- **vus**: Virtual users (concurrent users)
- **http_reqs**: Total number of HTTP requests

## Thresholds

The test defines performance thresholds:
- 95% of requests should complete in under 500ms
- 99% of requests should complete in under 1000ms
- Error rate should be less than 1%

If thresholds are not met, the test will be marked as failed.



