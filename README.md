# Stock Tracking DC

A comprehensive stock management system for Distribution Centers, built with Django REST Framework and React.

## Features

- **Stock Management**: Track stock levels, conditions, locations, and movements
- **Reservations**: Reserve stock for future orders and commitments
- **Transfers**: Move stock between locations with full audit trail
- **Stocktake**: Conduct physical inventory audits with variance tracking
- **Purchase Orders**: Manage incoming stock and supplier orders
- **Role-Based Access Control**: Granular permissions for different user roles
- **Real-time Updates**: Live stock level updates across the system
- **REST API**: Full-featured API for integrations

## Technology Stack

**Backend:**
- Django 4.2+ with Django REST Framework
- MySQL 8.0 database
- Redis for caching and task queue
- Celery for background tasks
- JWT authentication

**Frontend:**
- React 19 with TypeScript
- Mantine UI v7 component library
- React Query for data fetching
- Zustand for state management
- Vite build tool

## Quick Start with Docker (Recommended)

The easiest way to get started is using Docker:

```bash
# 1. Clone the repository
git clone <repository-url>
cd Stock-Tracking-DC

# 2. Create environment file
cp .env.example .env
# Edit .env and set SECRET_KEY, MYSQL_PASSWORD, MYSQL_ROOT_PASSWORD

# 3. Install and start (production)
make install
make superuser

# Or for development (with hot reload)
make dev
```

Access the application:
- **Frontend**: http://localhost:3000 (prod) or http://localhost:5173 (dev)
- **Backend API**: http://localhost:8000/api/v1/
- **API Documentation**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin/

For detailed Docker documentation, see [DOCKER.md](DOCKER.md).

## Manual Setup (Without Docker)

### Prerequisites

- Python 3.11+
- Node.js 20+
- MySQL 8.0
- Redis 7+

### Backend Setup

```bash
# Navigate to backend directory
cd src/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file in project root
cp ../../.env.example ../../.env
# Edit .env and configure database, Redis, etc.

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd src/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Start Background Worker

```bash
# In a separate terminal
cd src/backend
source venv/bin/activate
celery -A stockmgtr worker -l info
```

## Available Make Commands

```bash
make help          # Show all available commands
make install       # First-time installation
make start         # Start all services
make stop          # Stop all services
make restart       # Restart all services
make dev           # Start development environment
make logs          # Show all logs
make shell         # Access backend shell
make migrate       # Run database migrations
make superuser     # Create Django superuser
make test          # Run tests
make backup        # Backup database
make clean         # Remove all containers and volumes
```

## User Roles

The system supports the following roles with different permission levels:

- **Admin**: Full system access
- **Owner**: Business owner access
- **Logistics**: Manage transfers and reservations
- **Warehouse**: Manage stock and locations
- **Stocktake Manager**: Conduct and approve stocktakes
- **Sales**: View stock and create reservations
- **Accountant**: View reports and financial data
- **Warehouse Boy**: Basic stock viewing and updates

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## Project Structure

```
Stock-Tracking-DC/
├── docker/                 # Docker configuration files
│   ├── backend/           # Backend Dockerfile and configs
│   └── frontend/          # Frontend Dockerfile and nginx config
├── src/
│   ├── backend/           # Django backend
│   │   ├── api/          # REST API app
│   │   ├── stock/        # Stock management app
│   │   ├── stockmgtr/    # Project settings
│   │   └── requirements.txt
│   └── frontend/          # React frontend
│       ├── src/
│       │   ├── api/      # API client
│       │   ├── components/ # Reusable components
│       │   ├── pages/    # Page components
│       │   ├── states/   # State management
│       │   └── types/    # TypeScript types
│       └── package.json
├── docker-compose.yml     # Production Docker Compose
├── docker-compose.dev.yml # Development Docker Compose override
├── Makefile              # Docker management commands
├── DOCKER.md             # Detailed Docker documentation
└── .env.example          # Environment variables template
```

## Development

### Running Tests

```bash
# Backend tests
make test

# Or manually:
cd src/backend
python manage.py test

# With coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Code Style

The project follows:
- **Backend**: PEP 8 (Python style guide)
- **Frontend**: ESLint + Prettier for TypeScript/React

### Database Migrations

```bash
# Create new migration
make makemigrations

# Apply migrations
make migrate

# Or manually:
cd src/backend
python manage.py makemigrations
python manage.py migrate
```

## Deployment

### Production Deployment with Docker

```bash
# 1. Configure production environment
cp .env.example .env
# Edit .env with production values

# 2. Deploy
make deploy

# 3. Create superuser
make superuser
```

### Environment Variables

Key environment variables for production:

```bash
DEBUG=False
SECRET_KEY=<generate-secure-key>
ALLOWED_HOSTS=yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com

MYSQL_DATABASE=stock_tracking_db
MYSQL_USER=stock_user
MYSQL_PASSWORD=<secure-password>
MYSQL_ROOT_PASSWORD=<secure-root-password>

GUNICORN_WORKERS=4
GUNICORN_LOG_LEVEL=info

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=<app-password>

# Security (for HTTPS)
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Backup and Restore

### Backup Database

```bash
make backup
# Or manually:
docker-compose exec db mysqldump -u stock_user -p stock_tracking_db > backup.sql
```

### Restore Database

```bash
make restore BACKUP=backups/backup_file.sql
# Or manually:
docker-compose exec -T db mysql -u stock_user -p stock_tracking_db < backup.sql
```

## Troubleshooting

### Database Connection Issues

```bash
# Check database status
make status

# View database logs
make logs-db

# Reset database (WARNING: destroys data)
make db-reset
```

### Container Issues

```bash
# View all logs
make logs

# Restart specific service
make restart-backend
make restart-frontend

# Rebuild containers
make rebuild
```

### Permission Errors

```bash
# Fix volume permissions
docker-compose exec backend chown -R stockdc:stockdc /app/staticfiles
docker-compose exec backend chown -R stockdc:stockdc /app/media
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

For issues or questions:
- Check [DOCKER.md](DOCKER.md) for detailed Docker documentation
- Review logs: `make logs`
- Check service status: `make status`
- Review health: `make health`

## License

[Add your license information here]

## Acknowledgments

- Docker setup inspired by [InvenTree](https://github.com/inventree/InvenTree)
- Built with Django REST Framework and React
