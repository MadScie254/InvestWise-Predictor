.PHONY: build up down test lint format install-dev data-samples

# Development workflow
install-dev:
	pip install pre-commit
	pre-commit install
	cd backend && pip install -r requirements.txt
	cd ml_service && pip install -r requirements.txt
	cd frontend && npm ci

# Docker operations
build:
	docker-compose build

up:
	docker-compose up --build -d

down:
	docker-compose down

logs:
	docker-compose logs -f

# Testing
test:
	docker-compose run --rm backend pytest backend/tests/ -v
	docker-compose run --rm frontend npm test

test-backend:
	cd backend && pytest tests/ -v

test-frontend:
	cd frontend && npm test

# Code quality
lint:
	black backend/ ml_service/ ml/
	isort backend/ ml_service/ ml/
	flake8 backend/ ml_service/ ml/
	cd frontend && npm run lint

format:
	black backend/ ml_service/ ml/
	isort backend/ ml_service/ ml/

# ML operations
train:
	cd ml && python training/train.py

# Data operations
data-samples:
	python scripts/generate_sample_data.py

# Cleanup
clean:
	docker-compose down -v
	docker system prune -f