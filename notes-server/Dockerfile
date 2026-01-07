FROM python:3.11-slim

WORKDIR /app

# Copy from subdirectory since Railway builds from repo root
COPY notes-server/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY notes-server/app.py app.py

EXPOSE 5000

CMD ["python", "app.py"]



