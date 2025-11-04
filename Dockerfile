# Dockerfile for Clarity Sync Service
# This is a MINIMAL sync service - NO AI processing
# All AI operations happen locally on the user's machine

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy sync service requirements
COPY sync_service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy sync service code
COPY sync_service /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run the sync service (NOT the full backend)
CMD ["python", "main.py"]
