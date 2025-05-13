# ФАЛТ.конф

**Анонимная платформа для студентов, выпускников и сотрудников ФАЛТ (МФТИ).**

Предоставляет безопасное пространство для анонимных признаний, автоматической (LLM-based) и ручной модерации, публикации в Telegram, поддержки вложений и реакций. Основано на принципах Чистой Архитектуры:

- **Entities:** доменные сущности (`src/entities`, диаграмма в `docs/CA_c4_class.puml`)  
- **Use Cases:** бизнес-логика (`src/use_cases`)  
- **Interface Adapters:** Protocol-интерфейсы, DTO, контроллеры (`src/interface_adapters`)  
- **Frameworks and Drivers (infrastructure):** FastAPI, SQLAlchemy/Alembic, Telegram-бот (`src/frameworks_and_drivers`)

---

## 🚀 Быстрый старт

```bash
git clone https://github.com/your-org/falt-conf.git
cd falt-conf
poetry install --with dev
cp .env.example .env   # и заполнить переменные
docker-compose up -d
````

После этого API будет доступно на `http://localhost:8000`, админ-миграции Alembic можно запускать через `poetry run alembic upgrade head`.

---

## Прогресс выполнения

### 1) Настройка проекта

* [ ] Инициализация Git-репозитория и `.gitignore`
* [ ] Создание `pyproject.toml` и `poetry.lock` (Poetry)
* [ ] Создание каталогов:

  * `src/entities`
  * `src/use_cases`
  * `src/interface_adapters`
  * `src/frameworks_and_drivers`
  * `tests`, `scripts`, `docs`
* [ ] Настройка `Dockerfile` и `docker-compose.yml`

### 2) Entities (`src/entities`)

* [ ] Определить классы:

  * `Confession`, `Poll`, `Attachment`, `Reaction`, `Tag`, `Comment`, `ModerationLog`, `PublishedRecord`
* [ ] Добавить `Enum`-ы:

  * `ConfessionStatus`, `AttachmentType`
* [ ] Написать базовые unit-тесты для валидации полей и конструкторов

### 3) Use Cases (`src/use_cases`)

* [ ] Реализовать:

  * `CreateConfessionUseCase`
  * `ModerateConfessionUseCase`
  * `PublishConfessionUseCase`
  * `UpdateReactionsUseCase`
* [ ] Написать unit-тесты для каждого интерактора (AAA, мок-объекты)

### 4) Interface Adapters (`src/interface_adapters`)

* [ ] Определить Protocol-интерфейсы:

  * `ConfessionRepository`, `ModerationGateway`, `TelegramGateway`, `ReactionRepository`
* [ ] Создать DTO-классы (`Pydantic` или `dataclasses`):

  * `ConfessionDTO`, `PollDTO`, `AttachmentDTO`, `ReactionDTO` и т.д.
* [ ] Определить Controller-классы (методы без реализации)

### 5) Frameworks and Drivers (`src/frameworks_and_drivers`)

* [ ] Настроить SQLAlchemy и Alembic:

  * Базовые модели и миграции
* [ ] Реализация репозиториев на SQLAlchemy:

  * `ConfessionRepository`, `ReactionRepository` и пр.
* [ ] Telegram-шлюз (aiogram или python-telegram-bot):

  * Методы для отправки сообщений и опросов
* [ ] FastAPI:

  * Pydantic-схемы запросов/ответов
  * Роутеры, middleware, dependency-injection контроллеров

### Тестирование

* [ ] Настроить `pytest` и `pytest-asyncio`
* [ ] Написать unit-тесты для:

  * Entities
  * Use Cases
  * Interface Adapters (мок-репозитории)
* [ ] Написать integration-тесты для:

  * Репозиториев (база + миграции)
  * Полного сценария (создание → модерация → публикация)
* [ ] Достичь coverage ≥ 75% и добавить отчёт Cobertura/XML

### CI/CD

* [ ] GitHub Actions:

  1. `actions/setup-python@v4`
  2. `poetry install --with dev`
  3. Lint: `ruff`, `flake8`
  4. Type-check: `mypy`
  5. Tests: `pytest --cov`
  6. Docker: `docker build`, `docker push`
* [ ] Pre-commit hooks: `black`, `isort`, `ruff`
* [ ] Добавить бейджи Build/Tests/Coverage в README

### Дополнительно

* [ ] Реализовать ручную модерацию через CLI или админ-панель
* [ ] Поддержка хранения вложений (S3/minio)
* [ ] Фоновые задачи для обновления реакций в Telegram
* [ ] Настройка CORS и rate-limiting middleware
