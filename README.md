# Pulse

Flask-приложение на Python 3.14+, управляемое через uv.
Код прототипа перенесён в устанавливаемый пакет `src/pulse`.

## Запуск

```bash
uv sync
cp .env.example .env
uv run pulse run
```

Единая точка входа — `pulse`, зарегистрированная в `pyproject.toml`.
Она использует стандартный Flask CLI: `run`, `routes`, `shell`, `--help`.
`make run` вызывает `uv run pulse run`.

```bash
make run                              # обычный запуск
make dev PORT=8000                    # debug и автоперезагрузка
uv run pulse run --debug --port 8000   # то же напрямую
```

Список маршрутов: `make routes` или `uv run pulse routes`.

Настройки читаются из переменных окружения и `.env`:

- `APP_ENV`: `development` (по умолчанию), `testing`, `production`.
- `SECRET_KEY`: секрет приложения; для production задайте собственное значение.
- `DATABASE_URL`: по умолчанию `sqlite:///db.sqlite3`.

`APP_ENV` выбирает конфигурацию приложения и не включает debug автоматически.
Debug включается явно через `--debug` или `FLASK_DEBUG=1`; `--no-debug`
отключает его даже при заданной переменной окружения.
Команды запуска выше используют встроенный сервер Flask для разработки.
Для production WSGI-сервер должен загружать фабрику `pulse:create_app()`;
переключение `APP_ENV=production` само по себе не меняет сервер.

CLI построен на [FlaskGroup](https://flask.palletsprojects.com/en/stable/cli/#custom-scripts),
чтобы не дублировать обработку параметров и автоперезагрузку в коде проекта.

## Структура

```text
src/pulse/
├── __init__.py       # create_app: конфигурация и регистрация blueprint
├── main.py           # консольная команда pulse
├── config.py         # конфигурации окружений
├── extensions.py     # SQLAlchemy и Flask-Migrate
├── routers/
│   ├── __init__.py   # регистрация маршрутов
│   ├── questions.py
│   └── answers.py
├── models/          # место для моделей хранения
└── schemas/         # место для схем Pydantic
```

Сохранены маршруты прототипа: `GET/POST /questions` и
`GET/PUT/PATCH/DELETE /questions/<int:id>`. Их обработчики в исходнике
содержали только `pass`; теперь они возвращают JSON с кодом `501 Not Implemented`.
Маршруты ответов и Pydantic-схемы остаются заготовками.
Модели SQLAlchemy `Question` и `Answer` описывают таблицы вопросов и ответов.

## Миграции базы данных

Flask-Migrate подключён к фабрике приложения; модели загружаются автоматически.
Начальная миграция в `migrations/versions/` создаёт таблицы `questions` и
`answers` со связью через `question_id`.

Из корня проекта:

```bash
make db-upgrade                       # применить существующие миграции
make db-current                       # посмотреть текущую версию базы
make db-migrate MESSAGE="Description" # создать миграцию после изменения моделей
```

Перед применением новой миграции проверьте сгенерированный файл.
`db migrate` создаёт файл, а `db upgrade` изменяет схему базы данных.
База выбирается через `DATABASE_URL`; относительный SQLite-путь отсчитывается
от instance-каталога Flask (при текущем запуске из исходников — `src/instance/`).
Тестовая конфигурация использует отдельную SQLite-базу в памяти.

`make db-downgrade` откатывает одну миграцию; `REVISION=<id>` задаёт целевую
ревизию для upgrade или downgrade. Откат может удалить таблицы и их данные.
После применения миграций `make db-check` проверяет соответствие базы моделям.

## Проверки

```bash
make check
```

## Команды Makefile

`make` или `make help` выводит справку по всем командам.

| Команда | Назначение |
| --- | --- |
| `make install` | Установить зависимости из `uv.lock` |
| `make env` | Создать `.env`, сохранив существующий файл |
| `make run` | Запустить сервер разработки через `pulse run` |
| `make dev` | Запустить через `pulse run --debug` с автоперезагрузкой |
| `make routes` | Показать маршруты API |
| `make shell` | Открыть консоль Flask |
| `make db-migrate MESSAGE="Описание"` | Создать миграцию по изменениям моделей |
| `make db-upgrade` | Применить миграции до `head` или указанной `REVISION` |
| `make db-downgrade` | Откатить одну миграцию или до указанной `REVISION` |
| `make db-current` | Показать текущую ревизию базы |
| `make db-history` | Показать историю миграций |
| `make db-check` | Проверить соответствие базы моделям |
| `make test` | Запустить тесты через pytest |
| `make typecheck` | Проверить типы через Pyright |
| `make check` | Запустить тесты и проверку типов |
| `make lock` | Обновить lock-файл согласно зависимостям проекта |
| `make build` | Собрать пакет в `dist/` |
| `make clean` | Удалить сборки, кеши и отчёты покрытия; сохранить `.venv` и `.env` |

Примеры: `make dev PORT=8000`, `make test TEST_ARGS="-v -k question"`.
