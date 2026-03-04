# Network Backup Orchestrator - Containerized
FROM python:3.11-slim

LABEL maintainer="Gabriele Saronni"
LABEL description="Multi-vendor network backup automation tool"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first (Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY network-backup-orchestrator.py .
COPY credential_manager_gui.py .

# Create directories for backups
RUN mkdir -p /backups/todayBackup /backups/backupArchive /backups/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV BACKUP_PATH=/backups

# Default command (can be overridden)
CMD ["python", "network-backup-orchestrator.py"]
