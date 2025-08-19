.PHONY: install run lint test patch-bin docker-build docker-up clean

install:
	pip install -r requirements.txt

run:
	python -m app.main

lint:
	@echo "Linting com ruff..."
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check .; \
	else \
		echo "ruff não encontrado. Instale com: pip install ruff"; \
	fi

test:
	pytest -q

patch-bin:
	@echo "Verificando binário patch..."
	@if command -v patch >/dev/null 2>&1; then \
		echo "✓ patch encontrado: $(shell which patch)"; \
		patch --version | head -1; \
	else \
		echo "✗ patch não encontrado. Instale o pacote patch"; \
		exit 1; \
	fi

docker-build:
	docker build -t dev-trooper .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf /tmp/dev_trooper

setup: install patch-bin
	@echo "Setup completo! Copie env.example para .env e configure as variáveis"
