from flask import Flask, render_template_string, jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import os
import json
from datetime import datetime
from bson import ObjectId
from bson.errors import InvalidId

app = Flask(__name__)

# MongoDB connection for test results
MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
DB_NAME = os.getenv('DB_NAME', 'notes_db')
RESULTS_COLLECTION_NAME = 'k6_results'
PORT = int(os.getenv('PORT', 8080))

# Connect to MongoDB
try:
    client = MongoClient(MONGO_URL)
    db = client[DB_NAME]
    results_collection = db[RESULTS_COLLECTION_NAME]
    # Create index if it doesn't exist
    results_collection.create_index('timestamp', background=True)
except PyMongoError as e:
    print(f"Warning: Could not connect to MongoDB: {e}")
    results_collection = None

def get_results_collection():
    """Get or create the results collection"""
    global results_collection
    if results_collection is None:
        try:
            client = MongoClient(MONGO_URL)
            db = client[DB_NAME]
            results_collection = db[RESULTS_COLLECTION_NAME]
            results_collection.create_index('timestamp', background=True)
        except PyMongoError as e:
            raise Exception(f"Database connection failed: {e}")
    return results_collection

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>K6 Performance Test Results</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }
        .file-list {
            list-style: none;
        }
        .file-item {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            margin-bottom: 15px;
            transition: all 0.3s;
        }
        .file-item:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }
        .file-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .file-name {
            font-weight: 600;
            color: #2c3e50;
            font-size: 18px;
        }
        .file-date {
            color: #6c757d;
            font-size: 14px;
        }
        .file-actions {
            display: flex;
            gap: 10px;
        }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            font-size: 14px;
            transition: all 0.2s;
        }
        .btn-primary {
            background: #3498db;
            color: white;
        }
        .btn-primary:hover {
            background: #2980b9;
        }
        .btn-success {
            background: #27ae60;
            color: white;
        }
        .btn-success:hover {
            background: #229954;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .metric {
            background: white;
            padding: 12px;
            border-radius: 6px;
            border-left: 4px solid #3498db;
        }
        .metric-label {
            font-size: 12px;
            color: #6c757d;
            text-transform: uppercase;
            margin-bottom: 5px;
        }
        .metric-value {
            font-size: 24px;
            font-weight: 600;
            color: #2c3e50;
        }
        .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        .no-results-icon {
            font-size: 64px;
            margin-bottom: 20px;
        }
        .refresh-btn {
            margin-bottom: 20px;
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="refresh-btn">
            <a href="/" class="btn btn-primary">🔄 Refresh</a>
        </div>
        <h1>📊 K6 Performance Test Results</h1>
        {% if results %}
        <ul class="file-list">
            {% for result in results %}
            <li class="file-item">
                <div class="file-header">
                    <div>
                        <div class="file-name">{{ result.filename }}</div>
                        <div class="file-date">{{ result.date }}</div>
                    </div>
                    <div class="file-actions">
                        <a href="/view/{{ result.id }}" class="btn btn-primary">View Details</a>
                        <a href="/download/{{ result.id }}" class="btn btn-success">Download JSON</a>
                    </div>
                </div>
                {% if result.metrics %}
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">Total Requests</div>
                        <div class="metric-value">{{ result.metrics.http_reqs or 'N/A' }}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Avg Duration</div>
                        <div class="metric-value">{{ result.metrics.avg_duration or 'N/A' }}ms</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Error Rate</div>
                        <div class="metric-value">{{ result.metrics.error_rate or 'N/A' }}%</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">P95 Duration</div>
                        <div class="metric-value">{{ result.metrics.p95_duration or 'N/A' }}ms</div>
                    </div>
                </div>
                {% endif %}
            </li>
            {% endfor %}
        </ul>
        {% else %}
        <div class="no-results">
            <div class="no-results-icon">📭</div>
            <h2>No test results found</h2>
            <p>Run your K6 tests to generate results. Results will appear here automatically.</p>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Results - {{ filename }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #3498db;
            padding-bottom: 15px;
        }
        h1 { color: #2c3e50; }
        .back-btn {
            padding: 10px 20px;
            background: #3498db;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 6px;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.6;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📄 {{ filename }}</h1>
            <a href="/" class="back-btn">← Back to List</a>
        </div>
        <pre id="json-content">{{ json_data }}</pre>
    </div>
    <script>
        // Pretty print JSON
        try {
            const data = JSON.parse(document.getElementById('json-content').textContent);
            document.getElementById('json-content').textContent = JSON.stringify(data, null, 2);
        } catch (e) {
            // Already formatted or invalid JSON
        }
    </script>
</body>
</html>
"""

def extract_metrics(result_doc):
    """Extract key metrics from test result document"""
    metrics = {}
    
    # Try to get from summary first (pre-computed)
    if 'summary' in result_doc:
        summary = result_doc['summary']
        metrics['http_reqs'] = summary.get('http_reqs', 0)
        metrics['avg_duration'] = int(summary.get('avg_duration', 0))
        metrics['p95_duration'] = int(summary.get('p95_duration', 0))
        metrics['error_rate'] = f"{summary.get('error_rate', 0):.2f}"
    # Fallback to extracting from metrics
    elif 'metrics' in result_doc:
        m = result_doc['metrics']
        if 'http_reqs' in m and 'values' in m['http_reqs']:
            metrics['http_reqs'] = int(m['http_reqs']['values'].get('count', 0))
        if 'http_req_duration' in m and 'values' in m['http_req_duration']:
            values = m['http_req_duration']['values']
            metrics['avg_duration'] = int(values.get('avg', 0))
            metrics['p95_duration'] = int(values.get('p(95)', 0))
        if 'http_req_failed' in m and 'values' in m['http_req_failed']:
            rate = m['http_req_failed']['values'].get('rate', 0) * 100
            metrics['error_rate'] = f"{rate:.2f}"
    
    return metrics

@app.route('/')
def index():
    """List all test results from MongoDB"""
    try:
        collection = get_results_collection()
        # Get latest 100 results, sorted by timestamp
        db_results = list(collection.find().sort('timestamp', -1).limit(100))
        
        results = []
        for result in db_results:
            result_id = str(result['_id'])
            test_id = result.get('test_id', result_id)
            timestamp = result.get('timestamp', datetime.utcnow())
            
            # Format date
            if isinstance(timestamp, datetime):
                date_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_str = str(timestamp)
            
            # Extract metrics
            metrics = extract_metrics(result)
            
            results.append({
                'id': result_id,
                'filename': test_id,
                'date': date_str,
                'metrics': metrics if metrics else None
            })
        
        return render_template_string(HTML_TEMPLATE, results=results)
    except Exception as e:
        return f"Error loading results: {str(e)}", 500

@app.route('/view/<result_id>')
def view_result(result_id):
    """View detailed JSON result from MongoDB"""
    try:
        collection = get_results_collection()
        try:
            result = collection.find_one({'_id': ObjectId(result_id)})
        except InvalidId:
            return "Invalid result ID", 400
        
        if not result:
            return "Result not found", 404
        
        # Convert ObjectId to string for JSON serialization
        result['_id'] = str(result['_id'])
        
        # Get test_id or use _id as filename
        filename = result.get('test_id', result_id)
        
        json_str = json.dumps(result, indent=2, default=str)
        return render_template_string(DETAIL_TEMPLATE, filename=filename, json_data=json_str)
    except Exception as e:
        return f"Error reading result: {str(e)}", 500

@app.route('/download/<result_id>')
def download_result(result_id):
    """Download JSON result from MongoDB"""
    try:
        collection = get_results_collection()
        try:
            result = collection.find_one({'_id': ObjectId(result_id)})
        except InvalidId:
            return "Invalid result ID", 400
        
        if not result:
            return "Result not found", 404
        
        # Convert ObjectId to string
        result['_id'] = str(result['_id'])
        
        # Get test_id for filename
        filename = result.get('test_id', result_id)
        if not filename.endswith('.json'):
            filename += '.json'
        
        from flask import Response
        json_str = json.dumps(result, indent=2, default=str)
        return Response(
            json_str,
            mimetype='application/json',
            headers={'Content-Disposition': f'attachment; filename={filename}.json'}
        )
    except Exception as e:
        return f"Error downloading result: {str(e)}", 500

@app.route('/api/results')
def api_results():
    """API endpoint to get list of results from MongoDB"""
    try:
        collection = get_results_collection()
        db_results = list(collection.find().sort('timestamp', -1).limit(100))
        
        results = []
        for result in db_results:
            result_id = str(result['_id'])
            test_id = result.get('test_id', result_id)
            timestamp = result.get('timestamp', datetime.utcnow())
            
            results.append({
                'id': result_id,
                'filename': test_id,
                'date': timestamp.isoformat() if isinstance(timestamp, datetime) else str(timestamp),
                'size': len(json.dumps(result, default=str))
            })
        
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=False)



