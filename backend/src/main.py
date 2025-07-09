"""
Основной файл приложения FastAPI.
"""
import os
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.frameworks_and_drivers.rest_api.routers import confession_router, poll_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Обработчик жизненного цикла приложения."""
    # Код, выполняемый при запуске приложения
    logger.info("Starting ФАЛТ.конф API")
    
    yield  # Здесь приложение работает
    
    # Код, выполняемый при остановке приложения
    logger.info("Shutting down ФАЛТ.конф API")


def create_app() -> FastAPI:
    """Создает и настраивает приложение FastAPI."""
    # Создаем приложение
    app = FastAPI(
        title="ФАЛТ.конф API",
        description="API для системы анонимных признаний ФАЛТ.конф",
        version="0.1.0",
        lifespan=lifespan,
    )
    
    # Настраиваем CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # В продакшене заменить на конкретные домены
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Регистрируем роутеры
    app.include_router(confession_router, prefix="/api")
    app.include_router(poll_router, prefix="/api")
    
    # Добавляем обработчик для проверки работоспособности
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Проверка работоспособности сервиса."""
        return {
            "status": "ok",
            "version": app.version,
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    # Получаем настройки из переменных окружения
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    # Запускаем сервер
    uvicorn.run(
        "src.main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true",
    )