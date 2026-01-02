# Stock Tracking DC - Docker Management Makefile
# Based on InvenTree's Makefile pattern

.PHONY: help install start stop restart dev dev-build logs logs-backend logs-frontend logs-worker shell dbshell test migrate superuser backup clean rebuild update

# Default target
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Show this help message
	@echo "$(BLUE)Stock Tracking DC - Docker Management$(NC)"
	@echo ""
	@echo "$(GREEN)Available commands:$(NC)"
	@awk 'BEGIN {FS = ":.*##"; printf "\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  $(YELLOW)%-20s$(NC) %s\n", $$1, $$2 }' $(MAKEFILE_LIST)
	@echo ""

# ============================================================================
# Installation & Setup
# ============================================================================

install: ## First-time installation (creates .env, builds, starts, migrates)
	@echo "$(BLUE)Installing Stock Tracking DC...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file from .env.example...$(NC)"; \
		cp .env.example .env; \
		echo "$(RED)WARNING: Please edit .env and set SECRET_KEY, MYSQL_PASSWORD, and MYSQL_ROOT_PASSWORD$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)Building Docker containers...$(NC)"
	docker compose build
	@echo "$(GREEN)Starting services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Waiting for database to be ready...$(NC)"
	sleep 10
	@echo "$(GREEN)Running migrations...$(NC)"
	docker compose exec -T backend python manage.py migrate
	@echo "$(GREEN)Installation complete!$(NC)"
	@echo "$(YELLOW)Next steps:$(NC)"
	@echo "  1. Create a superuser: make superuser"
	@echo "  2. Access frontend: http://localhost:3000"
	@echo "  3. Access backend: http://localhost:8000"

# ============================================================================
# Service Management
# ============================================================================

start: ## Start all services
	@echo "$(GREEN)Starting all services...$(NC)"
	docker compose up -d
	@echo "$(GREEN)Services started!$(NC)"
	@docker compose ps

stop: ## Stop all services
	@echo "$(YELLOW)Stopping all services...$(NC)"
	docker compose down
	@echo "$(GREEN)Services stopped!$(NC)"

restart: ## Restart all services
	@echo "$(YELLOW)Restarting all services...$(NC)"
	docker compose restart
	@echo "$(GREEN)Services restarted!$(NC)"

restart-backend: ## Restart only backend service
	@echo "$(YELLOW)Restarting backend...$(NC)"
	docker compose restart backend
	@echo "$(GREEN)Backend restarted!$(NC)"

restart-frontend: ## Restart only frontend service
	@echo "$(YELLOW)Restarting frontend...$(NC)"
	docker compose restart frontend
	@echo "$(GREEN)Frontend restarted!$(NC)"

restart-worker: ## Restart only worker service
	@echo "$(YELLOW)Restarting worker...$(NC)"
	docker compose restart worker
	@echo "$(GREEN)Worker restarted!$(NC)"

# ============================================================================
# Development
# ============================================================================

dev: ## Start development environment (hot reload enabled)
	@echo "$(BLUE)Starting development environment...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(RED)ERROR: .env file not found. Run 'make install' first.$(NC)"; \
		exit 1; \
	fi
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

dev-build: ## Rebuild and start development environment
	@echo "$(BLUE)Rebuilding development environment...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up --build

dev-bg: ## Start development environment in background
	@echo "$(BLUE)Starting development environment in background...$(NC)"
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
	@echo "$(GREEN)Development environment started!$(NC)"
	@echo "Frontend: http://localhost:5173"
	@echo "Backend: http://localhost:8000"

# ============================================================================
# Logs
# ============================================================================

logs: ## Show logs from all services
	docker compose logs -f

logs-backend: ## Show backend logs
	docker compose logs -f backend

logs-frontend: ## Show frontend logs
	docker compose logs -f frontend

logs-worker: ## Show worker logs
	docker compose logs -f worker

logs-db: ## Show database logs
	docker compose logs -f db

logs-redis: ## Show redis logs
	docker compose logs -f redis

# ============================================================================
# Shell Access
# ============================================================================

shell: ## Access backend shell (bash)
	docker compose exec backend bash

shell-django: ## Access Django shell
	docker compose exec backend python manage.py shell

shell-frontend: ## Access frontend shell
	docker compose exec frontend sh

dbshell: ## Access database shell (MySQL)
	docker compose exec db mysql -u stock_user -p stock_tracking_db

redis-cli: ## Access Redis CLI
	docker compose exec redis redis-cli

# ============================================================================
# Django Commands
# ============================================================================

migrate: ## Run database migrations
	@echo "$(GREEN)Running migrations...$(NC)"
	docker compose exec backend python manage.py migrate

makemigrations: ## Create new migrations
	@echo "$(GREEN)Creating migrations...$(NC)"
	docker compose exec backend python manage.py makemigrations

superuser: ## Create Django superuser
	@echo "$(GREEN)Creating superuser...$(NC)"
	docker compose exec backend python manage.py createsuperuser

collectstatic: ## Collect static files
	@echo "$(GREEN)Collecting static files...$(NC)"
	docker compose exec backend python manage.py collectstatic --noinput

test: ## Run backend tests
	@echo "$(GREEN)Running tests...$(NC)"
	docker compose exec backend python manage.py test

test-coverage: ## Run tests with coverage
	@echo "$(GREEN)Running tests with coverage...$(NC)"
	docker compose exec backend coverage run --source='.' manage.py test
	docker compose exec backend coverage report
	docker compose exec backend coverage html

# ============================================================================
# Database Operations
# ============================================================================

backup: ## Backup database
	@echo "$(GREEN)Backing up database...$(NC)"
	@mkdir -p backups
	@BACKUP_FILE=backups/backup_$$(date +%Y%m%d_%H%M%S).sql; \
	docker compose exec -T db mysqldump -u stock_user -p$${MYSQL_PASSWORD} stock_tracking_db > $$BACKUP_FILE; \
	echo "$(GREEN)Database backed up to $$BACKUP_FILE$(NC)"

restore: ## Restore database from backup (usage: make restore BACKUP=backups/backup_file.sql)
	@if [ -z "$(BACKUP)" ]; then \
		echo "$(RED)ERROR: Please specify BACKUP file: make restore BACKUP=backups/backup_file.sql$(NC)"; \
		exit 1; \
	fi
	@echo "$(YELLOW)Restoring database from $(BACKUP)...$(NC)"
	docker compose exec -T db mysql -u stock_user -p$${MYSQL_PASSWORD} stock_tracking_db < $(BACKUP)
	@echo "$(GREEN)Database restored!$(NC)"

db-reset: ## Reset database (WARNING: destroys all data)
	@echo "$(RED)WARNING: This will destroy all data!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(YELLOW)Resetting database...$(NC)"; \
		docker compose down -v; \
		docker compose up -d; \
		sleep 10; \
		docker compose exec backend python manage.py migrate; \
		echo "$(GREEN)Database reset complete!$(NC)"; \
	fi

# ============================================================================
# Cleanup & Maintenance
# ============================================================================

clean: ## Remove all containers, volumes, and images
	@echo "$(RED)WARNING: This will remove all containers, volumes, and images!$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "$(YELLOW)Cleaning up...$(NC)"; \
		docker compose down -v --rmi all; \
		echo "$(GREEN)Cleanup complete!$(NC)"; \
	fi

prune: ## Remove unused Docker resources
	@echo "$(YELLOW)Pruning unused Docker resources...$(NC)"
	docker system prune -f
	@echo "$(GREEN)Prune complete!$(NC)"

rebuild: ## Rebuild all containers
	@echo "$(YELLOW)Rebuilding all containers...$(NC)"
	docker compose build --no-cache
	docker compose up -d
	@echo "$(GREEN)Rebuild complete!$(NC)"

rebuild-backend: ## Rebuild only backend container
	@echo "$(YELLOW)Rebuilding backend...$(NC)"
	docker compose build --no-cache backend
	docker compose up -d backend
	@echo "$(GREEN)Backend rebuilt!$(NC)"

rebuild-frontend: ## Rebuild only frontend container
	@echo "$(YELLOW)Rebuilding frontend...$(NC)"
	docker compose build --no-cache frontend
	docker compose up -d frontend
	@echo "$(GREEN)Frontend rebuilt!$(NC)"

# ============================================================================
# Update & Deploy
# ============================================================================

update: ## Pull latest code and rebuild
	@echo "$(BLUE)Updating Stock Tracking DC...$(NC)"
	git pull
	docker compose build
	docker compose up -d
	docker compose exec backend python manage.py migrate
	docker compose exec backend python manage.py collectstatic --noinput
	@echo "$(GREEN)Update complete!$(NC)"

deploy: ## Deploy to production (pull, build, migrate, restart)
	@echo "$(BLUE)Deploying to production...$(NC)"
	git pull
	docker compose build --no-cache
	docker compose down
	docker compose up -d
	@echo "$(YELLOW)Waiting for services to be ready...$(NC)"
	sleep 15
	docker compose exec -T backend python manage.py migrate
	docker compose exec -T backend python manage.py collectstatic --noinput
	@echo "$(GREEN)Deployment complete!$(NC)"

# ============================================================================
# Status & Information
# ============================================================================

status: ## Show status of all services
	@echo "$(BLUE)Service Status:$(NC)"
	@docker compose ps

ps: status ## Alias for status

info: ## Show environment information
	@echo "$(BLUE)Stock Tracking DC - Environment Information$(NC)"
	@echo ""
	@echo "$(GREEN)Docker Version:$(NC)"
	@docker --version
	@echo ""
	@echo "$(GREEN)Docker Compose Version:$(NC)"
	@docker compose version
	@echo ""
	@echo "$(GREEN)Services:$(NC)"
	@docker compose ps
	@echo ""
	@echo "$(GREEN)Volumes:$(NC)"
	@docker volume ls | grep stockdc || true
	@echo ""
	@echo "$(GREEN)Networks:$(NC)"
	@docker network ls | grep stockdc || true

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	@echo ""
	@echo "$(GREEN)Database:$(NC)"
	@docker compose exec -T db mysqladmin ping -h localhost -u root -p$${MYSQL_ROOT_PASSWORD} 2>/dev/null && echo "✓ MySQL is healthy" || echo "✗ MySQL is unhealthy"
	@echo ""
	@echo "$(GREEN)Redis:$(NC)"
	@docker compose exec -T redis redis-cli ping 2>/dev/null && echo "✓ Redis is healthy" || echo "✗ Redis is unhealthy"
	@echo ""
	@echo "$(GREEN)Backend:$(NC)"
	@curl -sf http://localhost:8000/api/v1/health/ > /dev/null && echo "✓ Backend is healthy" || echo "✗ Backend is unhealthy"
	@echo ""
	@echo "$(GREEN)Frontend:$(NC)"
	@curl -sf http://localhost:3000 > /dev/null && echo "✓ Frontend is healthy" || echo "✗ Frontend is unhealthy"

# ============================================================================
# Quick Commands
# ============================================================================

up: start ## Alias for start

down: stop ## Alias for stop

build: ## Build all containers
	docker compose build

pull: ## Pull latest images
	docker compose pull
