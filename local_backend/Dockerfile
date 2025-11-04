FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy model (optional, for better chunking)
# RUN python -m spacy download en_core_web_sm

# Copy application code
COPY app/ ./app/

# Create data directories
RUN mkdir -p /root/.clarity/chroma /root/.clarity/logs

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CLARITY_BASE_DIR=/root/.clarity

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
