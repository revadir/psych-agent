# Multi-stage build for faster Railway deployment
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

# Copy and install requirements first (for better caching)
COPY backend/requirements-cloud.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --user -r /tmp/requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY backend/ .

# Create directories
RUN mkdir -p data vector_db_hierarchical

# Clean up
RUN find . -type f -name "*.pyc" -delete && \
    find . -type d -name "__pycache__" -delete

# Make sure scripts are in PATH
ENV PATH=/root/.local/bin:$PATH

EXPOSE 8001
CMD ["python", "-m", "app.main"]
