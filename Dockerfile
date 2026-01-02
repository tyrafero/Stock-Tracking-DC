# Railway Deployment Dockerfile
# Single-service build: React frontend + Django backend

# ===========================
# Stage 1: Build React Frontend
# ===========================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY src/frontend/package*.json ./
RUN npm ci

COPY src/frontend ./
ENV DOCKER_BUILD=true
RUN npm run build

# ===========================
# Stage 2: Python Backend with Frontend
# ===========================
FROM python:3.11-slim-bookworm AS production

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN python -m pip install --upgrade pip setuptools wheel

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY src/backend/requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY src/backend ./

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend_build

# Create directories
RUN mkdir -p staticfiles media

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Start command (Railway will set $PORT)
CMD python manage.py migrate && \
    gunicorn stockmgtr.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
