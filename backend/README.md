# fastapi-backend-template

Пустой шаблон для приложений Fast API с Postgres и Kafka.
В качестве веб-сервиса используется Nginx. Все сервисы обернуты в Docker контейнеры,
которые можно запустить с помощью Docker Compose.

## Конфигурация

- Сервисы можно настраивать через переменные окружения.
- Пример конфигурации находится в файле `.env.example`.
- Для разработки и отладки рекомендуется создать файл `.env-dev`.

## Разработка, отладка, тестовый запуск

1. Установить `pyenv`
2. Установить `pipx`
3. Установить `poetry` через `pipx` (`pipx install poetry`)
4. `make dev-docker-run-postgres`
5. `make dev-docker-run-kafka`
6. `make dev-init` - создаст окружение и установит все нужные пакеты.
7. `make dev-run-server` - запуск Fast API сервера в контейнере.

На http://0.0.0.0:8000/ доступен dev-сервер Fast API.

### Полезные команды:
- Запуск тестов и проверки покрытия тестами - `make test`
- Запуск линтеров в режиме исправления возможных проблем - `make lint`
- Запуск тестов и линтеров - `make check`
- Создание миграции - `cd src && alembic revision --autogenerate -m "<migration name>"`
- Прогон миграций - `cd src && alembic upgrade head`

Изменения в коде необходимо покрывать тестами, перед отправкой изменений
в свою рабочую ветку (git push) необходимо прогонять тесты локально, чтобы обнаружить
ошибки до этапа CI в репозитории.

### Gitlab CI:
Далее приведен пример файла конфигурации CI `.gitlab-ci.yml`, связанного с репозиторием
[fastapi-gitlab-ci-template](https://gitlab.inst.falt.ru/backend_utils/fastapi-gitlab-ci-template):
```
image:
  docker:24.0.6

stages:
  - build
  - lint
  - test

include:
  - project: 'backend_utils/fastapi-gitlab-ci-template'
    file: '/jobs/build.yml'
  - project: 'backend_utils/fastapi-gitlab-ci-template'
    file: '/jobs/lint.yml'
  - project: 'backend_utils/fastapi-gitlab-ci-template'
    file: '/jobs/test.yml'

```
Gitlab автоматически попробует выполнить описанные шаги при наличии данного
файла в корне репозитория, чтобы pipeline мог пройти, необходимо,
чтобы в настройках проекта был указан Runner (подробнее к команде DevOps).
Помимо Runner в Gitlab проекте (репозитории) в Settings -> CI/CD -> Variables
также необходимо будет добавить следующие переменные:
`CI_REGISTRY`, `CI_REGISTRY_IMAGE`, `CI_COMMIT_REF_SLUG`, `CI_PROJECT_DIR`.

**Во время создания CI файла не было доступных раннеров, так что при использовании
примера может понадобиться отладка!**

### Опционально:
- Локально установить расширение `poetry-sort` с помощью команды
`poetry self add poetry-sort` для автоматической сортировки зависимостей
по алфавиту в `pyproject.toml` при прогоне `poetry add ...` или с помощью
команды `poetry sort`.
