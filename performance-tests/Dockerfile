FROM grafana/k6:latest

WORKDIR /app

# Copy from subdirectory since Railway builds from repo root
COPY performance-tests/script.js script.js
COPY performance-tests/notes-api-client.js notes-api-client.js
COPY performance-tests/utils.js utils.js

# InfluxDB configuration (optional - if not set, K6 runs normally)
# These will be set as environment variables in Railway
ENV INFLUXDB_URL=""
ENV INFLUXDB_TOKEN=""
ENV INFLUXDB_ORG=""
ENV INFLUXDB_BUCKET=""

# Override entrypoint to use sh for conditional logic
ENTRYPOINT ["/bin/sh", "-c"]

# Run test with optional InfluxDB output
# K6's built-in InfluxDB output supports v1 format
# For InfluxDB v2, we use the v1-compatible endpoint with token in URL
# Format: influxdb=http://host:port/database?token=xxx
# If INFLUXDB_URL and INFLUXDB_TOKEN are set, output to InfluxDB; otherwise run normally
CMD ["if [ -n \"$INFLUXDB_URL\" ] && [ -n \"$INFLUXDB_TOKEN\" ]; then k6 run --out \"influxdb=$INFLUXDB_URL?token=$INFLUXDB_TOKEN\" script.js; else k6 run script.js; fi"]



