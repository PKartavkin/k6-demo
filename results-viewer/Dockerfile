FROM python:3.11-slim

WORKDIR /app

# Copy from subdirectory since Railway builds from repo root
COPY results-viewer/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY results-viewer/app.py app.py

EXPOSE 8080

CMD ["python", "app.py"]



