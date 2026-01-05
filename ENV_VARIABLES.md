# Environment Variables Guide

This document lists all environment variables needed for each container/service in the setup.

## 1. Notes Server Container

**Required:**
- `MONGO_URL` - MongoDB connection string (default: `mongodb://localhost:27017/`)
  - Example: `mongodb://user:password@host:27017/`
  - Example (MongoDB Atlas): `mongodb+srv://user:password@cluster.mongodb.net/`

**Optional:**
- `DB_NAME` - Database name (default: `notes_db`)
- `API_USER` - Basic auth username (default: `admin`)
- `API_PASSWORD` - Basic auth password (default: `password`)

**Example for Railway:**
```
MONGO_URL=mongodb+srv://user:pass@cluster.mongodb.net/
DB_NAME=notes_db
API_USER=admin
API_PASSWORD=your_secure_password
```

## 2. K6 Performance Test Container

**Required:**
- `BASE_URL` - URL of the notes server API
  - Example: `http://notes-server:5000` (if in same network)
  - Example: `https://your-notes-server.railway.app` (if external)

**Optional:**
- `API_USER` - Basic auth username (default: `admin`)
  - Should match the `API_USER` set in notes-server
- `API_PASSWORD` - Basic auth password (default: `password`)
  - Should match the `API_PASSWORD` set in notes-server

**Example for Railway:**
```
BASE_URL=https://your-notes-server.railway.app
API_USER=admin
API_PASSWORD=your_secure_password
```

## 3. Results Viewer Container

**Optional:**
- `PORT` - Port to run the web server on (default: `8080`)
- `RESULTS_DIR` - Directory where results are stored (default: `/app/results`)

**Example for Railway:**
```
PORT=8080
RESULTS_DIR=/app/results
```

## Railway Setup Instructions

### Setting Environment Variables in Railway:

1. **For Notes Server:**
   - Go to your notes-server service
   - Navigate to "Variables" tab
   - Add:
     - `MONGO_URL` (required)
     - `DB_NAME` (optional)
     - `API_USER` (optional, but recommended to change from default)
     - `API_PASSWORD` (optional, but recommended to change from default)

2. **For K6 Tests:**
   - Go to your performance-tests service
   - Navigate to "Variables" tab
   - Add:
     - `BASE_URL` (required - use your notes-server URL)
     - `API_USER` (should match notes-server)
     - `API_PASSWORD` (should match notes-server)

3. **For Results Viewer:**
   - Go to your results-viewer service
   - Navigate to "Variables" tab
   - Add:
     - `PORT` (optional, Railway will auto-assign if not set)
     - `RESULTS_DIR` (optional, defaults to `/app/results`)

### Getting Service URLs in Railway:

- Railway automatically provides a public URL for each service
- You can find it in the service's "Settings" → "Networking"
- Use this URL for `BASE_URL` in the K6 container

### MongoDB Connection:

If using MongoDB Atlas or external MongoDB:
- Set `MONGO_URL` with the full connection string
- Make sure your MongoDB allows connections from Railway's IP ranges (or use 0.0.0.0/0 for testing)

If using Railway's MongoDB service:
- Railway provides a connection string automatically
- Use that as your `MONGO_URL`

