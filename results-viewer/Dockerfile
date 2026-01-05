FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Create results directory
RUN mkdir -p /app/results

EXPOSE 8080

CMD ["python", "app.py"]

