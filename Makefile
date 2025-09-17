.PHONY: help setup test clean lint format install

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Set up development environment
	python setup.py

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	python test_litellm_fallback.py
	python test_bedrock_converse_fallback.py

lint: ## Run linting
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format: ## Format code
	black . --line-length 127
	isort .

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -name "*.egg-info" -exec rm -rf {} +
	find . -name ".pytest_cache" -exec rm -rf {} +

security: ## Run security checks
	bandit -r . --severity-level medium
	safety check

examples: ## Run example scripts
	@echo "Running examples..."
	python litellm_multi_model.py || true
	python anthropic_to_bedrock_fallback.py || true