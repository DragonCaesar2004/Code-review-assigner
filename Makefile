.PHONY: help build up down restart logs test test-cov clean migrate lint format

# Цвета для вывода
GREEN  := \033[0;32m
YELLOW := \033[0;33m
NC     := \033[0m # No Color

help: ## Показать эту справку
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Собрать Docker образы
	@echo "$(GREEN)Сборка Docker образов...$(NC)"
	docker-compose build

up: ## Запустить сервис (docker-compose up)
	@echo "$(GREEN)Запуск сервиса...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)Сервис запущен на http://localhost:8080$(NC)"
	@echo "$(GREEN)Swagger UI доступен по адресу http://localhost:8080/docs$(NC)"

down: ## Остановить сервис
	@echo "$(YELLOW)Остановка сервиса...$(NC)"
	docker-compose down

restart: down up ## Перезапустить сервис

logs: ## Показать логи сервиса
	docker-compose logs -f app

logs-db: ## Показать логи базы данных
	docker-compose logs -f db

ps: ## Показать статус контейнеров
	docker-compose ps

clean: ## Удалить контейнеры и volumes
	@echo "$(YELLOW)Удаление контейнеров и volumes...$(NC)"
	docker-compose down -v
	rm -rf htmlcov/
	rm -f .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true

test: ## Запустить все тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	uv run pytest tests/ -v

test-cov: ## Запустить тесты с покрытием кода
	@echo "$(GREEN)Запуск тестов с измерением покрытия...$(NC)"
	uv run pytest tests/ -v --cov=src --cov-report=term-missing:skip-covered --cov-report=html
	@echo "$(GREEN)HTML отчёт сохранён в htmlcov/index.html$(NC)"

test-e2e: ## Запустить только E2E тесты
	@echo "$(GREEN)Запуск E2E тестов...$(NC)"
	uv run pytest tests/test_e2e.py -v

test-services: ## Запустить только unit-тесты сервисов
	@echo "$(GREEN)Запуск unit-тестов сервисов...$(NC)"
	uv run pytest tests/test_services.py -v

migrate: ## Применить миграции базы данных
	@echo "$(GREEN)Применение миграций...$(NC)"
	docker-compose exec app alembic upgrade head

migrate-create: ## Создать новую миграцию (использование: make migrate-create MSG="описание")
	@echo "$(GREEN)Создание новой миграции...$(NC)"
	docker-compose exec app alembic revision --autogenerate -m "$(MSG)"

lint: ## Проверить код линтером (ruff)
	@echo "$(GREEN)Проверка кода...$(NC)"
	uv run ruff check src/ tests/

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	uv run ruff format src/ tests/

install: ## Установить зависимости
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	uv sync

shell: ## Открыть shell в контейнере приложения
	docker-compose exec app /bin/bash

db-shell: ## Подключиться к PostgreSQL
	docker-compose exec db psql -U postgres -d code_review_assigner_db

# Полный цикл разработки
dev-setup: install up ## Первичная настройка окружения разработки
	@echo "$(GREEN)Окружение разработки готово!$(NC)"
	@echo "$(GREEN)API: http://localhost:8080$(NC)"
	@echo "$(GREEN)Docs: http://localhost:8080/docs$(NC)"

dev-reset: clean install up ## Полный сброс и перезапуск окружения
	@echo "$(GREEN)Окружение сброшено и перезапущено!$(NC)"

# Проверка перед коммитом
pre-commit: lint test ## Запустить линтер и тесты перед коммитом
	@echo "$(GREEN)✓ Все проверки пройдены!$(NC)"

# CI/CD команды
ci: lint test-cov ## Запустить все проверки как в CI
	@echo "$(GREEN)✓ CI проверки пройдены!$(NC)"

# Информация о проекте
info: ## Показать информацию о проекте
	@echo "$(GREEN)PR Reviewer Assignment Service$(NC)"
	@echo "Версия: 1.0.0"
	@echo "Python: $$(python --version 2>&1 | cut -d' ' -f2)"
	@echo "Docker: $$(docker --version | cut -d' ' -f3 | cut -d',' -f1)"
	@echo ""
	@echo "Структура проекта:"
	@echo "  src/           - исходный код приложения"
	@echo "  tests/         - тесты"
	@echo "  migrations/    - миграции Alembic"
	@echo "  openapi.yaml   - OpenAPI спецификация"
	@echo ""
	@echo "Полезные команды:"
	@echo "  make up        - запустить сервис"
	@echo "  make test      - запустить тесты"
	@echo "  make logs      - показать логи"
	@echo "  make help      - показать все команды"
