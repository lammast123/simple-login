# Dockerfile ở root repo
FROM python:3.11-slim

WORKDIR /app

# Copy backend code
COPY backend/ .  

# Cài dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]
