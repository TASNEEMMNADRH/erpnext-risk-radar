.PHONY: help install test coverage lint format clean run

help:
	@echo "ERPNext Risk Radar - Development Commands"
	@echo ""
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run all tests"
	@echo "  make coverage   - Run tests with coverage report"
	@echo "  make lint       - Run linters (flake8)"
	@echo "  make format     - Auto-format code (black, isort)"
	@echo "  make clean      - Remove cache and temp files"
	@echo "  make run        - Start the FastAPI server"
	@echo ""

install:
	pip install --upgrade pip
	pip install -r requirements.txt

test:
	python -m unittest backend.test.test_api -v

coverage:
	coverage run -m unittest backend.test.test_api
	coverage report --include="app.py,services/*.py" -m
	coverage html --include="app.py,services/*.py"
	@echo "\nCoverage report generated in htmlcov/index.html"

lint:
	flake8 app.py services/ backend/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 app.py services/ backend/ --count --max-complexity=10 --max-line-length=127 --statistics

format:
	black app.py services/ backend/
	isort app.py services/ backend/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/ .pytest_cache/

run:
	uvicorn app:app --reload --host 0.0.0.0 --port 8000
