FROM grafana/k6:latest

WORKDIR /app

# Copy from subdirectory since Railway builds from repo root
COPY performance-tests/script.js script.js

# Run test - container will exit after completion (prevents continuous restart on Railway)
CMD ["run", "script.js"]



