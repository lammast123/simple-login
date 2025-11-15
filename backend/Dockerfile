# --- Step 1: Chọn base image ---
FROM python:3.11-slim

# --- Step 2: Tạo working directory ---
WORKDIR /app

# --- Step 3: Copy files và requirements ---
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# --- Step 4: Expose port ---
EXPOSE 5000

# --- Step 5: Chạy app ---
CMD ["python", "app.py"]
