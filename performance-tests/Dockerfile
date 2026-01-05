FROM grafana/k6:latest

WORKDIR /app

# Create results directory
RUN mkdir -p /app/results

# Copy test script
COPY script.js .

# Default command
CMD ["k6", "run", "script.js"]

