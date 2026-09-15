.DEFAULT_GOAL := help

UV ?= uv
HOST ?= 127.0.0.1
PORT ?= 5000
RUN_ARGS ?=
TEST_ARGS ?=
MESSAGE ?=
export MESSAGE REVISION

.PHONY: help install env run dev routes shell test typecheck check lock build clean db-migrate db-upgrade db-downgrade db-current db-history db-check

help: ## Показать доступные команды
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "  make %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Установить зависимости из uv.lock
	$(UV) sync --locked

env: ## Создать .env из примера, если файл отсутствует
	@test -e .env || cp .env.example .env

run: ## Запустить сервер разработки (HOST, PORT, RUN_ARGS="--debug")
	$(UV) run pulse run --host "$(HOST)" --port "$(PORT)" $(RUN_ARGS)

dev: ## Запустить с debug и автоперезагрузкой (HOST, PORT, RUN_ARGS)
	$(UV) run pulse run --debug --host "$(HOST)" --port "$(PORT)" $(RUN_ARGS)

routes: ## Показать маршруты API
	$(UV) run pulse routes

shell: ## Открыть Python-консоль в контексте Flask
	$(UV) run pulse shell

db-migrate: ## Создать миграцию по моделям (MESSAGE="Описание")
	@test -n "$$MESSAGE" || { echo 'Укажите описание: make db-migrate MESSAGE="Описание"'; exit 1; }
	$(UV) run pulse db migrate --message "$$MESSAGE"

db-upgrade: REVISION = head
db-upgrade: ## Применить миграции (REVISION=head по умолчанию)
	$(UV) run pulse db upgrade -- "$$REVISION"

db-downgrade: REVISION = -1
db-downgrade: ## Откатить одну миграцию (или до REVISION)
	$(UV) run pulse db downgrade -- "$$REVISION"

db-current: ## Показать текущую версию базы
	$(UV) run pulse db current

db-history: ## Показать историю миграций
	$(UV) run pulse db history

db-check: ## Проверить, что схема базы соответствует моделям
	$(UV) run pulse db check

test: ## Запустить тесты (дополнительные параметры: TEST_ARGS)
	$(UV) run pytest tests $(TEST_ARGS)

typecheck: ## Проверить типы через Pyright
	$(UV) run pyright src tests

check: test typecheck ## Запустить тесты и проверку типов

lock: ## Обновить uv.lock согласно pyproject.toml
	$(UV) lock

build: ## Собрать wheel и sdist в dist/
	$(UV) build

clean: ## Удалить сборки и кеши проекта, сохранив .venv и .env
	rm -rf build dist wheels .pytest_cache .pyright .coverage htmlcov
	find src tests -type d \( -name __pycache__ -o -name '*.egg-info' \) -prune -exec rm -rf {} +
	find src tests -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
