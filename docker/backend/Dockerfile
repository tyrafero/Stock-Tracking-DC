# Stock Tracking DC - Backend Dockerfile
# Multi-stage build based on InvenTree pattern
# Supports both development and production targets

# ===========================
# Base Stage - Common dependencies
# ===========================
FROM python:3.11-slim-bookworm AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies required for mysqlclient and other packages
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip to latest version
RUN python -m pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy requirements file
COPY src/backend/requirements.txt .

# Install Python dependencies
RUN python -m pip install --no-cache-dir -r requirements.txt

# ===========================
# Development Target
# ===========================
FROM base AS development

# Install development tools
RUN pip install --no-cache-dir \
    ipython \
    django-debug-toolbar \
    django-extensions

# Copy application code (will be mounted as volume in dev)
COPY src/backend /app

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# ===========================
# Production Target
# ===========================
FROM base AS production

# Copy application code
COPY src/backend /app

# Copy gunicorn configuration
COPY docker/backend/gunicorn.conf.py /app/gunicorn.conf.py

# Create directories for static and media files
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Create non-root user for security
RUN useradd -m -u 1000 stockdc && \
    chown -R stockdc:stockdc /app
USER stockdc

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/ || exit 1

# Default command
CMD ["gunicorn", "stockmgtr.wsgi:application", \
     "--config", "gunicorn.conf.py", \
     "--bind", "0.0.0.0:8000"]
