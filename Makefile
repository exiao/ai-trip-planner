.PHONY: test test-verbose test-coverage test-watch install run lint help

# Default target
help:
	@echo "Available commands:"
	@echo "  make test          - Run all tests"
	@echo "  make test-verbose  - Run tests with verbose output"
	@echo "  make test-coverage - Run tests with coverage report"
	@echo "  make install       - Install dependencies"
	@echo "  make run           - Start the backend server"
	@echo "  make lint          - Run linter on backend code"

# Run all tests
test:
	cd backend && source .env && uv run pytest tests/ -v

# Run tests with verbose output
test-verbose:
	cd backend && source .env && uv run pytest tests/ -vv

# Run tests with coverage report
test-coverage:
	cd backend && source .env && uv run pytest tests/ --cov=main --cov-report=html --cov-report=term

# Install dependencies
install:
	cd backend && uv pip install -r requirements.txt

# Start the backend server
run:
	cd backend && source .env && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Run linter
lint:
	cd backend && uv run ruff check .

