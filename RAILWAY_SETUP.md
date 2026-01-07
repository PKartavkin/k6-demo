# Railway Cloud Setup Guide

This guide explains how to deploy and configure all services on Railway.

## Architecture Overview

1. **Notes Server** - Flask REST API with MongoDB
2. **K6 Performance Tests** - Load testing service
3. **Results Viewer** - Web interface to view test results

## Setup Steps

### 1. Create a New Railway Project

1. Go to [Railway](https://railway.app)
2. Create a new project
3. Add three services:
   - `notes-server`
   - `performance-tests`
   - `results-viewer`

### 2. Deploy Notes Server

1. **Add Service:**
   - Click "New" → "GitHub Repo" or "Empty Service"
   - Name it `notes-server`

2. **Configure:**
   - Set root directory to `notes-server/`
   - Railway will auto-detect the Dockerfile

3. **Set Environment Variables:**
   - Go to "Variables" tab
   - Add:
     ```
     MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
     DB_NAME=notes_db
     API_USER=admin
     API_PASSWORD=your_secure_password
     ```

4. **Get the Service URL:**
   - Go to "Settings" → "Networking"
   - Copy the generated URL (e.g., `https://notes-server-production.up.railway.app`)

### 3. Deploy Results Viewer

1. **Add Service:**
   - Click "New" → "Empty Service"
   - Name it `results-viewer`

2. **Configure:**
   - Set root directory to `results-viewer/`
   - Railway will auto-detect the Dockerfile

3. **Set Environment Variables:**
   ```
   MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
   DB_NAME=notes_db
   PORT=8080
   ```
   - **Important:** Use the same `MONGO_URL` and `DB_NAME` as notes-server

4. **Get the Service URL:**
   - Go to "Settings" → "Networking"
   - Copy the generated URL

**Note:** No volumes needed! Results are stored in MongoDB.

### 4. Deploy K6 Performance Tests

1. **Add Service:**
   - Click "New" → "Empty Service"
   - Name it `performance-tests`

2. **Configure:**
   - Set root directory to `performance-tests/`
   - Railway will auto-detect the Dockerfile

3. **Set Environment Variables:**
   ```
   BASE_URL=https://notes-server-production.up.railway.app
   API_USER=admin
   API_PASSWORD=your_secure_password
   MONGO_URL=https://notes-server-production.up.railway.app
   ```
   - `BASE_URL`: Your notes-server URL (for running tests)
   - `MONGO_URL`: Same as BASE_URL (results saved via API)
   - `API_USER` and `API_PASSWORD`: Should match notes-server

4. **Configure Service:**
   - The container will automatically shut down after test completion
   - To run tests again, simply redeploy the service
   - No need to configure restart policies

**Note:** No volumes needed! Results are automatically saved to MongoDB via the notes-server API.

### 5. Running Tests

#### Option A: Manual Trigger (Recommended)

1. Go to `performance-tests` service
2. Click "Deploy" or "Redeploy" to run tests
3. View logs to see test progress
4. After completion, go to `results-viewer` URL to see results

#### Option B: Scheduled Runs

1. Use Railway's Cron Jobs (if available) or external scheduler
2. Or set up a webhook trigger

#### Option C: Continuous Testing

1. Set `performance-tests` to run continuously (not recommended for load tests)
2. Tests will run in a loop

### 6. Viewing Results

1. After K6 tests complete, open the `results-viewer` URL in your browser
2. You'll see a list of all test results with:
   - Test ID and timestamp
   - Key metrics (requests, duration, error rate)
   - Links to view full JSON or download

**How it works:**
- K6 tests save results to MongoDB via notes-server API (`/test-results` endpoint)
- Results viewer reads directly from MongoDB
- All results are stored in the `k6_results` collection
- No file system or volumes needed!

## Environment Variables Summary

### Notes Server
```
MONGO_URL=*required*
DB_NAME=notes_db (optional)
API_USER=admin (optional)
API_PASSWORD=password (optional, but recommended to change)
```

### K6 Performance Tests
```
BASE_URL=*required* (your notes-server URL)
API_USER=admin (should match notes-server)
API_PASSWORD=password (should match notes-server)
MONGO_URL=*optional* (defaults to BASE_URL, used for saving results)
```

### Results Viewer
```
MONGO_URL=*required* (same MongoDB as notes-server)
DB_NAME=notes_db (optional, should match notes-server)
PORT=8080 (optional, Railway auto-assigns)
```

## Troubleshooting

### Results Not Appearing

1. **Check MongoDB Connection:**
   - Verify `MONGO_URL` is correct in results-viewer
   - Ensure it's the same MongoDB instance as notes-server
   - Check MongoDB allows connections from Railway IPs

2. **Check K6 Output:**
   - Look at K6 service logs
   - Verify it says "✓ Test results saved to MongoDB"
   - Check if API call to `/test-results` succeeded

3. **Check Notes Server:**
   - Verify notes-server is running
   - Test the `/test-results` endpoint manually
   - Check notes-server logs for errors

### Connection Issues

1. **K6 can't reach Notes Server:**
   - Use the full Railway URL (https://...)
   - Check if services are in the same network
   - Verify `BASE_URL` is correct

2. **MongoDB Connection:**
   - Verify `MONGO_URL` is correct
   - Check MongoDB allows connections from Railway IPs
   - For MongoDB Atlas, whitelist 0.0.0.0/0 (or Railway IPs)

## Quick Start Commands

After setting up on Railway:

1. **Run a test:**
   - Trigger deployment of `performance-tests` service

2. **View results:**
   - Open `results-viewer` URL in browser

3. **Check logs:**
   - View logs in Railway dashboard for each service

## Cost Considerations

- Railway charges based on usage
- K6 tests should run on-demand, not continuously
- Results viewer can run continuously (low resource usage)
- Notes server runs continuously (main service)



