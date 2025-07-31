FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory and ensure proper permissions
RUN mkdir -p /data/jobs && chmod 755 /data/jobs

# Set environment variables for production
ENV PYTHONPATH=/app
ENV MAST_STORAGE_PATH=/data/jobs
ENV MAST_FAKE_MODE=0
ENV MAST_API_URL=http://localhost:3000
ENV MAST_ALLOWED_ORIGINS=*

# Expose ports
EXPOSE 3000 9000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Copy and set up startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Default command
CMD ["/app/start.sh"]