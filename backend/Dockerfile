# Base image Python 3.11 slim
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy chỉ backend
COPY backend/ .  

# Cài dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Mở port Flask
EXPOSE 5000

# Chạy app.py
CMD ["python", "app.py"]
