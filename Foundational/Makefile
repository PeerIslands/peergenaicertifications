# Makefile for Foundational Project

.PHONY: help install test lint format clean docker-build docker-up docker-down deploy

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Installation
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install backend dependencies
	cd backend && python -m pip install -r requirements.txt -r requirements-dev.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm install

# Testing
test: test-backend test-frontend ## Run all tests

test-backend: ## Run backend tests
	cd backend && pytest -v

test-frontend: ## Run frontend tests
	cd frontend && npm test

test-coverage: ## Run tests with coverage
	cd backend && pytest --cov=src --cov-report=html
	cd frontend && npm run test:coverage

test-e2e: ## Run E2E tests
	cd frontend && npm run test:e2e

# Linting and Formatting
lint: lint-backend lint-frontend ## Run linters

lint-backend: ## Run backend linter
	cd backend && flake8 src/
	cd backend && mypy src/ --ignore-missing-imports

lint-frontend: ## Run frontend linter
	cd frontend && npm run lint

format: format-backend format-frontend ## Format code

format-backend: ## Format backend code
	cd backend && black src/
	cd backend && isort src/

format-frontend: ## Format frontend code
	cd frontend && npx prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}"

# Docker
docker-build: ## Build Docker images
	docker-compose build

docker-up: ## Start Docker containers
	docker-compose up -d

docker-down: ## Stop Docker containers
	docker-compose down

docker-logs: ## View Docker logs
	docker-compose logs -f

docker-dev: ## Start development environment
	docker-compose -f docker-compose.dev.yml up

docker-prod: ## Start production environment
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Database
db-backup: ## Backup MongoDB database
	docker-compose exec -T mongodb mongodump --archive > backup-$$(date +%Y%m%d).archive

db-restore: ## Restore MongoDB database (usage: make db-restore FILE=backup.archive)
	docker-compose exec -T mongodb mongorestore --archive < $(FILE)

db-shell: ## Open MongoDB shell
	docker-compose exec mongodb mongosh chatpdf

# Development
dev-backend: ## Start backend development server
	cd backend && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend: ## Start frontend development server
	cd frontend && npm run dev

dev: ## Start both backend and frontend in development mode
	make -j2 dev-backend dev-frontend

# Cleaning
clean: ## Clean build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	rm -rf frontend/coverage backend/htmlcov backend/.coverage

# Health checks
health-check: ## Check health of all services
	@echo "Checking backend..."
	@curl -f http://localhost:8000/health || echo "Backend is down"
	@echo "\nChecking frontend..."
	@curl -f http://localhost:3000 || echo "Frontend is down"

# CI/CD
ci-test: ## Run CI tests (used in GitHub Actions)
	make test
	make lint

# Documentation
docs: ## Generate documentation
	@echo "API documentation available at http://localhost:8000/docs after starting backend"

# Production
deploy: ## Deploy to production
	@echo "Building production images..."
	docker-compose build
	@echo "Pushing images..."
	docker-compose push
	@echo "Deploying..."
	docker-compose -f docker-compose.yml up -d
	@echo "Deployment complete!"

# Version
version: ## Show version information
	@echo "Backend (Python):"
	@cd backend && python --version
	@echo "\nFrontend (Node):"
	@cd frontend && node --version
	@echo "\nDocker:"
	@docker --version
	@echo "\nDocker Compose:"
	@docker-compose --version

