# --- Step 1: Chọn base image ---
FROM node:20-alpine

# --- Step 2: Tạo working directory ---
WORKDIR /app

# --- Step 3: Copy package.json và install ---
COPY package*.json ./
RUN npm install

# --- Step 4: Copy toàn bộ source code ---
COPY . .

# --- Step 5: Expose port ---
EXPOSE 3000

# --- Step 6: Chạy app ---
CMD ["node", "server.js"]
