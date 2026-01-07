# K6 Performance Testing Demo

A complete performance testing setup with a REST API service and K6 load testing tools.

## Overview

This project consists of four main components:

1. **Notes Server** (`notes-server/`): A Flask-based REST API with MongoDB backend
   - RESTful API with CRUD operations for notes
   - Basic authentication
   - MongoDB integration with automatic collection handling
   - Dockerized for easy deployment

2. **MongoDB**: Database service (you'll handle this separately)

3. **Performance Tests** (`performance-tests/`): K6 load testing scripts
   - Comprehensive test scenarios covering all CRUD operations
   - Configurable load patterns
   - Detailed reporting and metrics
   - Results saved to shared volume

4. **Results Viewer** (`results-viewer/`): Web interface to view test results
   - Beautiful web UI to browse test results
   - View detailed JSON data
   - Download results files
   - Shows key metrics at a glance

## Quick Start

### 1. Setup MongoDB

Set up your MongoDB instance (local or remote) and note the connection URL.

### 2. Run the Notes Server

#### Using Docker:

```bash
cd notes-server
docker build -t notes-server .
docker run -d -p 5000:5000 \
  -e MONGO_URL=mongodb://localhost:27017/ \
  -e API_USER=admin \
  -e API_PASSWORD=password \
  notes-server
```

#### Using Python directly:

```bash
cd notes-server
pip install -r requirements.txt
export MONGO_URL=mongodb://localhost:27017/
export API_USER=admin
export API_PASSWORD=password
python app.py
```

### 3. Run Performance Tests

```bash
cd performance-tests
k6 run script.js
```

Or with custom configuration:

```bash
BASE_URL=http://localhost:5000 API_USER=admin API_PASSWORD=password k6 run script.js
```

## Configuration

### Notes Server Environment Variables

- `MONGO_URL`: MongoDB connection string (default: `mongodb://localhost:27017/`)
- `DB_NAME`: Database name (default: `notes_db`)
- `API_USER`: Basic auth username (default: `admin`)
- `API_PASSWORD`: Basic auth password (default: `password`)

### Performance Tests Environment Variables

- `BASE_URL`: API base URL (default: `http://localhost:5000`)
- `API_USER`: Basic auth username (default: `admin`)
- `API_PASSWORD`: Basic auth password (default: `password`)

## API Endpoints

All endpoints require Basic Authentication.

- `GET /health` - Health check (no auth required)
- `GET /notes` - List all notes
- `GET /notes/<id>` - Get a specific note
- `POST /notes` - Create a new note (requires `title` in JSON body)
- `PUT /notes/<id>` - Update a note
- `DELETE /notes/<id>` - Delete a note
- `POST /test-results` - Save K6 test result (no auth required)
- `GET /test-results` - Get all test results (no auth required)
- `GET /test-results/<id>` - Get specific test result (no auth required)

## Analyzing Performance Test Results

See `performance-tests/README.md` for detailed instructions on:
- Generating reports (console, JSON, K6 Cloud)
- Analyzing metrics
- Setting up real-time monitoring with InfluxDB/Grafana
- Understanding performance thresholds

## Project Structure

```
k6-demo/
├── notes-server/          # Flask REST API
│   ├── app.py            # Main application
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Docker configuration
├── performance-tests/     # K6 load tests
│   ├── script.js        # Test script
│   ├── Dockerfile        # Docker configuration
│   └── README.md        # Detailed test documentation
├── results-viewer/        # Results web viewer
│   ├── app.py           # Flask web app
│   ├── requirements.txt  # Python dependencies
│   └── Dockerfile        # Docker configuration
├── ENV_VARIABLES.md      # Environment variables guide
├── RAILWAY_SETUP.md      # Railway deployment guide
└── README.md            # This file
```

## Deployment on Railway

See `RAILWAY_SETUP.md` for detailed instructions on deploying all services to Railway cloud, including:
- Configuring MongoDB for results storage
- Setting environment variables
- Running tests and viewing results
- Container auto-shutdown after test completion

## Environment Variables

See `ENV_VARIABLES.md` for a complete list of environment variables needed for each service.

## Notes

- The notes server automatically handles missing MongoDB collections
- Basic auth credentials can be configured via environment variables
- K6 tests include staged load patterns and performance thresholds
- **Test results are stored in MongoDB** (no volumes needed!)
- K6 container automatically shuts down after test completion (saves costs on Railway)
- Results viewer reads directly from MongoDB for real-time viewing
- All components are designed to be simple and maintainable
