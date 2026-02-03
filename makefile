.PHONY: install dev sync test lint format clean run help

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies with uv"
	@echo "  make sync       - Sync dependencies with uv"
	@echo "  make test       - Run tests with uv (requires pytest)"
	@echo "  make lint       - Run linter with uv (requires ruff)"
	@echo "  make format     - Format code with uv (requires ruff)"
	@echo "  make clean      - Remove Python cache files and directories"
	@echo "  make run        - Run the application with uv"
	@echo "  make dev        - Install dev dependencies (ruff, pytest)"

install:
	uv pip install -r requirements.txt

dev:
	uv pip install ruff pytest

sync:
	uv sync

test:
	@command -v pytest >/dev/null 2>&1 || { echo "pytest not found. Run 'make dev' to install it."; exit 1; }
	uv run pytest

lint:
	@command -v ruff >/dev/null 2>&1 || { echo "ruff not found. Run 'make dev' to install it."; exit 1; }
	uv run ruff check .

format:
	@command -v ruff >/dev/null 2>&1 || { echo "ruff not found. Run 'make dev' to install it."; exit 1; }
	uv run ruff format .

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaned up cache files and directories"

run:
	uv run python main.py