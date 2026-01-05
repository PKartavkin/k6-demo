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

3. **Add Volume (for persistent storage):**
   - Go to "Volumes" tab
   - Click "Add Volume"
   - Set mount path: `/app/results`
   - This ensures results persist across deployments

4. **Set Environment Variables (optional):**
   ```
   PORT=8080
   RESULTS_DIR=/app/results
   ```

5. **Get the Service URL:**
   - Go to "Settings" → "Networking"
   - Copy the generated URL

### 4. Deploy K6 Performance Tests

1. **Add Service:**
   - Click "New" → "Empty Service"
   - Name it `performance-tests`

2. **Configure:**
   - Set root directory to `performance-tests/`
   - Railway will auto-detect the Dockerfile

3. **Add Volume (shared with results-viewer):**
   - Go to "Volumes" tab
   - Click "Add Volume"
   - **Important:** Use the SAME volume as results-viewer
   - Set mount path: `/app/results`
   - This allows K6 to write results that results-viewer can read

4. **Set Environment Variables:**
   ```
   BASE_URL=https://notes-server-production.up.railway.app
   API_USER=admin
   API_PASSWORD=your_secure_password
   RESULTS_DIR=/app/results
   ```

5. **Configure Service:**
   - Set service to run "on deploy" or manually trigger
   - K6 tests are typically run on-demand, not continuously

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
   - Test filename and timestamp
   - Key metrics (requests, duration, error rate)
   - Links to view full JSON or download

### 7. Volume Sharing (Important!)

**For Railway:**
- Railway volumes are service-specific by default
- To share results between K6 and results-viewer, you have two options:

**Option 1: Use Railway's Shared Volumes (if available)**
- Create a volume in one service
- Mount it in both services

**Option 2: Use External Storage (Recommended)**
- Use Railway's built-in storage or external service (S3, etc.)
- Or use a database to store results
- Or use Railway's file system (results persist in service)

**Option 3: Simple Approach (Easiest)**
- Mount volumes separately in each service
- Use a shared database or external storage
- Or: results-viewer can poll/read from K6 service's volume via API

### Alternative: Results via API

If volumes don't work well, you can modify the setup to:
1. K6 saves results to a database (MongoDB)
2. Results viewer reads from the same database
3. Or: K6 uploads results to an S3-compatible storage

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
RESULTS_DIR=/app/results (optional)
```

### Results Viewer
```
PORT=8080 (optional, Railway auto-assigns)
RESULTS_DIR=/app/results (optional)
```

## Troubleshooting

### Results Not Appearing

1. **Check Volume Mounts:**
   - Ensure both services have volumes mounted at `/app/results`
   - Verify they're using the same volume (if shared volumes supported)

2. **Check K6 Output:**
   - Look at K6 service logs
   - Verify `RESULTS_DIR` is set correctly
   - Check if files are being written

3. **Check File Permissions:**
   - Ensure results directory is writable
   - Check Railway volume permissions

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

