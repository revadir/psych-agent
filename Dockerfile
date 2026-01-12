# Dockerfile for production deployment
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the backend application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p data vector_db_hierarchical

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "-m", "app.main"]
