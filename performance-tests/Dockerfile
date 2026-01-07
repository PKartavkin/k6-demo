FROM grafana/k6:latest

WORKDIR /app

# Copy test script
COPY script.js .

# Run test and exit (prevents continuous restart on Railway)
# This ensures the container shuts down after test completion
CMD ["sh", "-c", "k6 run script.js && exit 0"]



