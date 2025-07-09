# Базовый образ с Python
FROM python:3.11-slim as base

# Установка Poetry
RUN pip install poetry

# Настройка рабочей директории
WORKDIR /app

# Копирование файлов Poetry
COPY pyproject.toml ./

# Настройка Poetry
RUN poetry config virtualenvs.create false

# Этап разработки
FROM base as development

# Установка зависимостей разработки
RUN poetry install --with dev

# Копирование исходного кода
COPY . .

# Запуск приложения
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Этап продакшн
FROM base as production

# Установка только основных зависимостей
RUN poetry install --only main

# Копирование исходного кода
COPY . .

# Запуск приложения в продакшн режиме
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"] 