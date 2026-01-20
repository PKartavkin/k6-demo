# Build k6 with InfluxDB v2 output extension
FROM golang:1.21-alpine AS builder

# Install xk6 and build k6 with InfluxDB v2 extension
RUN apk add --no-cache git
RUN go install go.k6.io/xk6/cmd/xk6@latest
RUN xk6 build --with github.com/grafana/xk6-output-influxdb@latest --output /k6

# Final image
FROM alpine:latest

RUN apk add --no-cache ca-certificates && \
    addgroup -S k6 && \
    adduser -S -G k6 k6

WORKDIR /app

# Copy custom k6 binary from builder
COPY --from=builder /k6 /usr/bin/k6

# Copy from subdirectory since Railway builds from repo root
COPY performance-tests/script.js script.js
COPY performance-tests/notes-api-client.js notes-api-client.js
COPY performance-tests/utils.js utils.js

# InfluxDB v2 configuration (optional - if not set, K6 runs normally)
# These will be set as environment variables in Railway
ENV K6_INFLUXDB_ADDR=""
ENV K6_INFLUXDB_TOKEN=""
ENV K6_INFLUXDB_ORGANIZATION=""
ENV K6_INFLUXDB_BUCKET=""

# Override entrypoint to use sh for conditional logic
ENTRYPOINT ["/bin/sh", "-c"]

# Run test with optional InfluxDB v2 output using xk6-output-influxdb extension
# If InfluxDB env vars are set, output to InfluxDB; otherwise run normally
# Format: xk6-influxdb=<url> with env vars: K6_INFLUXDB_TOKEN, K6_INFLUXDB_ORGANIZATION, K6_INFLUXDB_BUCKET
CMD ["if [ -n \"$K6_INFLUXDB_ADDR\" ] && [ -n \"$K6_INFLUXDB_TOKEN\" ] && [ -n \"$K6_INFLUXDB_ORGANIZATION\" ] && [ -n \"$K6_INFLUXDB_BUCKET\" ]; then k6 run --out xk6-influxdb=$K6_INFLUXDB_ADDR script.js; else k6 run script.js; fi"]
