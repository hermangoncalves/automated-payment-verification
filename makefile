.PHONY: run clean install format lint test

run:
	@echo "Running the application..."
	@python3 main.py

install:
	@echo "Installing dependencies..."
	@pip install -r requirements.txt

format:
	@echo "Formatting code with Black..."
	@black .

lint:
	@echo "Checking code style with Flake8..."
	@flake8 .

test:
	@echo "Running tests..."
	@pytest

clean:
	@echo "Cleaning up..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
