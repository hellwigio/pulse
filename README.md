# Pulse

API вопросов и ответов на Flask, SQLAlchemy и Pydantic. Python 3.14+, uv.

## Запуск

```bash
make install
make env
make db-upgrade
make dev
```

Настройки — в `.env` (пример: `.env.example`). По умолчанию используется SQLite.
Сервер разработки: `http://127.0.0.1:5000`. Другой порт: `make dev PORT=8000`.

## Команды

```bash
make run        # запуск без явного включения debug
make dev        # debug и автоперезагрузка
make check      # тесты и проверка типов
make clean      # удалить сборки и кеши
make help       # все команды
```

## Миграции

```bash
make db-migrate m="Описание" # создать миграцию после изменения моделей
make db-upgrade                    # применить миграции
make db-downgrade                  # откатить одну миграцию
make db-current                    # текущая версия базы
make db-check                      # проверить соответствие базы моделям
```

Перед применением проверьте сгенерированный файл в `migrations/versions/`.
