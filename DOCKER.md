# Docker Setup Guide for Stock Tracking DC

This guide provides comprehensive instructions for running Stock Tracking DC using Docker, similar to InvenTree's Docker setup.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Docker Services](#docker-services)
- [Environment Configuration](#environment-configuration)
- [Common Commands](#common-commands)
- [Troubleshooting](#troubleshooting)
- [Advanced Configuration](#advanced-configuration)

---

## Overview

Stock Tracking DC uses a multi-container Docker setup with the following services:

- **db**: MySQL 8.0 database
- **redis**: Redis cache and Celery broker
- **backend**: Django REST API (Gunicorn in production, runserver in dev)
- **worker**: Celery background task worker
- **frontend**: React SPA (nginx in production, Vite dev server in dev)

## Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ (included with Docker Desktop)
- At least 4GB RAM available for Docker
- 10GB free disk space

## Quick Start

### Production (Quick Deploy)

```bash
# 1. Clone the repository
git clone <repository-url>
cd Stock-Tracking-DC

# 2. Create environment file
cp .env.example .env

# 3. Edit .env and set required variables (at minimum):
#    - SECRET_KEY (generate a secure random key)
#    - MYSQL_PASSWORD
#    - MYSQL_ROOT_PASSWORD

# 4. Start all services
docker-compose up -d

# 5. Create a superuser
docker-compose exec backend python manage.py createsuperuser

# 6. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Admin: http://localhost:8000/admin
```

### Development (Hot Reload)

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and set DEBUG=True

# 2. Start development stack
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# 3. Access development servers
# Frontend (Vite): http://localhost:5173
# Backend: http://localhost:8000
```

Or use the Makefile:

```bash
make dev        # Start development stack
make dev-build  # Rebuild and start development stack
```

## Development Setup

### Starting Development Environment

The development setup provides:
- Hot reload for both frontend (Vite HMR) and backend (Django runserver)
- Volume mounts for live code changes
- Debug logging enabled
- Development dependencies included

```bash
# Start with logs
make dev

# Start in background
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop services
docker-compose down
```

### Running Django Commands

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run tests
docker-compose exec backend python manage.py test

# Django shell
docker-compose exec backend python manage.py shell

# Collect static files
docker-compose exec backend python manage.py collectstatic
```

### Accessing Container Shells

```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh

# Database shell
docker-compose exec db mysql -u stock_user -p stock_tracking_db

# Redis CLI
docker-compose exec redis redis-cli
```

### Installing New Dependencies

**Backend (Python):**
```bash
# Add package to src/backend/requirements.txt
# Then rebuild the backend container
docker-compose build backend
docker-compose up -d backend
```

**Frontend (Node.js):**
```bash
# Add package
docker-compose exec frontend npm install <package-name>

# Or rebuild
docker-compose build frontend
docker-compose up -d frontend
```

## Production Deployment

### Production Configuration

1. **Environment Variables** - Set production values in `.env`:

```bash
DEBUG=False
SECRET_KEY=your-very-secure-random-secret-key-here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

MYSQL_DATABASE=stock_tracking_db
MYSQL_USER=stock_user
MYSQL_PASSWORD=secure-database-password
MYSQL_ROOT_PASSWORD=secure-root-password

REDIS_URL=redis://redis:6379/0

GUNICORN_WORKERS=4
GUNICORN_LOG_LEVEL=info

# Email configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security settings (for HTTPS)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

2. **Generate Secret Key**:

```bash
# Generate a secure SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

3. **Start Production Stack**:

```bash
# Build and start all services
docker-compose up -d --build

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

4. **Initial Setup**:

```bash
# Run migrations
docker-compose exec backend python manage.py migrate

# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Collect static files (if needed)
docker-compose exec backend python manage.py collectstatic --noinput
```

### Using Makefile for Production

```bash
make install    # Install and start production stack
make start      # Start all services
make stop       # Stop all services
make restart    # Restart all services
make update     # Pull latest code and rebuild
make backup     # Backup database
```

## Docker Services

### Database (MySQL)

- **Container**: stockdc-db
- **Image**: mysql:8.0
- **Port**: 3306
- **Data**: Persisted in `db_data` volume
- **Backup**:
  ```bash
  docker-compose exec db mysqldump -u stock_user -p stock_tracking_db > backup.sql
  ```

### Redis

- **Container**: stockdc-redis
- **Image**: redis:7-alpine
- **Port**: 6379
- **Purpose**: Cache and Celery message broker

### Backend (Django)

- **Container**: stockdc-backend
- **Production**: Gunicorn WSGI server (4 workers)
- **Development**: Django runserver with auto-reload
- **Port**: 8000
- **Volumes**:
  - `static_data`: Collected static files
  - `media_data`: User-uploaded files

### Worker (Celery)

- **Container**: stockdc-worker
- **Production**: 2 concurrent workers
- **Development**: 1 worker with debug logging
- **Purpose**: Background tasks (emails, reports, etc.)

### Frontend (React)

- **Container**: stockdc-frontend
- **Production**: nginx serving built static files
- **Development**: Vite dev server with HMR
- **Ports**: 3000 (prod), 5173 (dev)

## Environment Configuration

### Required Variables

These must be set in `.env`:

```bash
SECRET_KEY=<generate-secure-key>
MYSQL_PASSWORD=<database-password>
MYSQL_ROOT_PASSWORD=<root-password>
```

### Optional Variables

```bash
# Application
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Database
MYSQL_DATABASE=stock_tracking_db
MYSQL_USER=stock_user
MYSQL_HOST=db
MYSQL_PORT=3306

# Redis
REDIS_URL=redis://redis:6379/0

# Gunicorn
GUNICORN_WORKERS=4
GUNICORN_LOG_LEVEL=info

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
NODE_ENV=production
```

## Common Commands

### Using Makefile

```bash
make help          # Show all available commands
make install       # First-time installation
make start         # Start all services
make stop          # Stop all services
make restart       # Restart all services
make dev           # Start development environment
make logs          # Show all logs
make logs-backend  # Show backend logs
make logs-frontend # Show frontend logs
make shell         # Access backend shell
make dbshell       # Access database shell
make test          # Run backend tests
make migrate       # Run database migrations
make superuser     # Create Django superuser
make backup        # Backup database
make clean         # Remove all containers and volumes
make rebuild       # Rebuild all containers
```

### Using Docker Compose Directly

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service-name]

# Restart a service
docker-compose restart [service-name]

# Rebuild and restart
docker-compose up -d --build

# Remove everything (including volumes)
docker-compose down -v

# Scale workers
docker-compose up -d --scale worker=4
```

## Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
docker-compose ps db

# View database logs
docker-compose logs db

# Test connection
docker-compose exec backend python manage.py dbshell

# Reset database (WARNING: destroys all data)
docker-compose down -v
docker-compose up -d
docker-compose exec backend python manage.py migrate
```

### Backend Not Starting

```bash
# Check backend logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait for db health check
# 2. Missing migrations - run: make migrate
# 3. Wrong SECRET_KEY - check .env file

# Restart backend
docker-compose restart backend
```

### Frontend Build Issues

```bash
# View frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Check nginx config
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf
```

### Permission Errors

```bash
# Fix volume permissions
docker-compose exec backend chown -R stockdc:stockdc /app/staticfiles
docker-compose exec backend chown -R stockdc:stockdc /app/media
```

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8000  # or :3000, :5173, etc.

# Kill process
sudo kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Map container port 8000 to host port 8001
```

### Viewing Service Health

```bash
# Check health status
docker-compose ps

# All services should show "healthy" or "running"
# If not, check logs:
docker-compose logs [unhealthy-service]
```

## Advanced Configuration

### Scaling Services

```bash
# Scale Celery workers
docker-compose up -d --scale worker=4

# Scale in production with multiple worker containers
# Edit docker-compose.yml to add worker2, worker3, etc.
```

### Using External Database

Edit `.env`:
```bash
DATABASE_URL=mysql://user:password@external-host:3306/dbname
```

Comment out the `db` service in `docker-compose.yml` and remove `depends_on: db` from backend and worker.

### Custom nginx Configuration

Edit `docker/frontend/nginx.conf` for custom routing, SSL, etc.

### Adding SSL/HTTPS

Use a reverse proxy like Traefik or nginx-proxy:

```yaml
# Add to docker-compose.yml
services:
  traefik:
    image: traefik:v2.9
    command:
      - "--providers.docker=true"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--certificatesresolvers.myresolver.acme.httpchallenge=true"
      - "--certificatesresolvers.myresolver.acme.httpchallenge.entrypoint=web"
      - "--certificatesresolvers.myresolver.acme.email=your@email.com"
      - "--certificatesresolvers.myresolver.acme.storage=/letsencrypt/acme.json"
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock:ro"
      - "./letsencrypt:/letsencrypt"
```

### Performance Tuning

**Gunicorn Workers**:
```bash
# Set in .env
GUNICORN_WORKERS=8  # Formula: (2 x CPU cores) + 1
```

**Database Connection Pool**:
Edit `src/backend/stockmgtr/settings.py`:
```python
DATABASES = {
    'default': {
        # ...
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
        'CONN_MAX_AGE': 600,  # Connection pooling
    }
}
```

### Monitoring

Add monitoring services:

```yaml
# Prometheus metrics
services:
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  # Grafana dashboards
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

---

## Support

For issues or questions:
- Check logs: `docker-compose logs -f`
- Review this documentation
- Check Docker status: `docker-compose ps`
- Verify environment: `cat .env`

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [InvenTree Docker Setup](https://docs.inventree.org/en/latest/start/docker/)
