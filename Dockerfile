# Dockerfile for production deployment - optimized for size
FROM python:3.11-slim

WORKDIR /app

# Install only essential system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements and install Python dependencies with optimizations
COPY backend/requirements-cloud.txt ./requirements.txt

# Install dependencies with size optimizations
RUN pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# Copy only the backend application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p data vector_db_hierarchical

# Remove unnecessary files to reduce image size
RUN find . -type f -name "*.pyc" -delete \
    && find . -type d -name "__pycache__" -delete \
    && rm -rf /root/.cache

# Expose port
EXPOSE 8001

# Run the application
CMD ["python", "-m", "app.main"]
