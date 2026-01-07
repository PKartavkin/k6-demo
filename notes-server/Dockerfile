FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py app.py

EXPOSE 5000

CMD ["python", "app.py"]



