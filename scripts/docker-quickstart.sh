#!/bin/bash
# Stock Tracking DC - Docker Quick Start Script
# This script helps you quickly set up and start the application

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_message() {
    echo -e "${2}${1}${NC}"
}

# Print section header
print_header() {
    echo ""
    echo "========================================"
    echo -e "${BLUE}${1}${NC}"
    echo "========================================"
    echo ""
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main script
main() {
    print_header "Stock Tracking DC - Quick Start"

    # Check prerequisites
    print_message "Checking prerequisites..." "$YELLOW"

    if ! command_exists docker; then
        print_message "ERROR: Docker is not installed. Please install Docker first." "$RED"
        echo "Visit: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command_exists docker-compose; then
        print_message "ERROR: Docker Compose is not installed." "$RED"
        echo "Visit: https://docs.docker.com/compose/install/"
        exit 1
    fi

    print_message "✓ Docker and Docker Compose are installed" "$GREEN"

    # Check if .env exists
    if [ ! -f .env ]; then
        print_message ".env file not found. Creating from .env.example..." "$YELLOW"

        if [ ! -f .env.example ]; then
            print_message "ERROR: .env.example not found!" "$RED"
            exit 1
        fi

        cp .env.example .env
        print_message "✓ Created .env file" "$GREEN"

        # Generate SECRET_KEY
        if command_exists python3; then
            SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "")
            if [ -n "$SECRET_KEY" ]; then
                # Update SECRET_KEY in .env (macOS and Linux compatible)
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
                else
                    sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
                fi
                print_message "✓ Generated SECRET_KEY" "$GREEN"
            fi
        fi

        print_message "" "$YELLOW"
        print_message "IMPORTANT: Please edit .env and set the following:" "$RED"
        print_message "  - MYSQL_PASSWORD" "$YELLOW"
        print_message "  - MYSQL_ROOT_PASSWORD" "$YELLOW"
        print_message "" "$NC"

        read -p "Press Enter after you've updated the .env file, or Ctrl+C to exit..."
    else
        print_message "✓ .env file exists" "$GREEN"
    fi

    # Ask user what to do
    print_header "What would you like to do?"
    echo "1) Production setup (recommended for deployment)"
    echo "2) Development setup (with hot reload)"
    echo "3) Exit"
    echo ""
    read -p "Enter your choice [1-3]: " choice

    case $choice in
        1)
            print_header "Starting Production Setup"
            production_setup
            ;;
        2)
            print_header "Starting Development Setup"
            development_setup
            ;;
        3)
            print_message "Exiting..." "$YELLOW"
            exit 0
            ;;
        *)
            print_message "Invalid choice. Exiting..." "$RED"
            exit 1
            ;;
    esac
}

production_setup() {
    print_message "Building Docker images..." "$BLUE"
    docker-compose build

    print_message "Starting services..." "$BLUE"
    docker-compose up -d

    print_message "Waiting for database to be ready..." "$YELLOW"
    sleep 10

    print_message "Running database migrations..." "$BLUE"
    docker-compose exec -T backend python manage.py migrate

    print_message "Collecting static files..." "$BLUE"
    docker-compose exec -T backend python manage.py collectstatic --noinput

    print_header "Production Setup Complete!"
    print_message "✓ All services are running" "$GREEN"
    echo ""
    echo "Next steps:"
    echo "  1. Create a superuser: docker-compose exec backend python manage.py createsuperuser"
    echo "     Or use: make superuser"
    echo ""
    echo "Access the application:"
    echo "  Frontend:  http://localhost:3000"
    echo "  Backend:   http://localhost:8000"
    echo "  API Docs:  http://localhost:8000/api/docs/"
    echo ""
    echo "Useful commands:"
    echo "  make logs          - View all logs"
    echo "  make stop          - Stop all services"
    echo "  make restart       - Restart all services"
    echo "  make help          - Show all available commands"
    echo ""
}

development_setup() {
    print_message "Building Docker images for development..." "$BLUE"
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml build

    print_message "Starting development services..." "$BLUE"
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

    print_message "Waiting for database to be ready..." "$YELLOW"
    sleep 10

    print_message "Running database migrations..." "$BLUE"
    docker-compose exec -T backend python manage.py migrate

    print_header "Development Setup Complete!"
    print_message "✓ All services are running with hot reload enabled" "$GREEN"
    echo ""
    echo "Next steps:"
    echo "  1. Create a superuser: docker-compose exec backend python manage.py createsuperuser"
    echo "     Or use: make superuser"
    echo ""
    echo "Access the application:"
    echo "  Frontend (Vite):  http://localhost:5173"
    echo "  Backend:          http://localhost:8000"
    echo "  API Docs:         http://localhost:8000/api/docs/"
    echo ""
    echo "View logs:"
    echo "  docker-compose logs -f"
    echo "  Or use: make logs"
    echo ""
    echo "Stop services:"
    echo "  docker-compose down"
    echo "  Or use: make stop"
    echo ""
}

# Run main function
main "$@"
