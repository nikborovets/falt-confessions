"""
Основной файл приложения FastAPI.
"""
import os
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.frameworks_and_drivers.rest_api.routers import confession_router, poll_router


def create_app() -> FastAPI:
    """Создает и настраивает приложение FastAPI."""
    # Создаем приложение
    app = FastAPI(
        title="ФАЛТ.конф API",
        description="API для системы анонимных признаний ФАЛТ.конф",
        version="0.1.0",
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
    app.include_router(confession_router)
    app.include_router(poll_router)
    
    # Добавляем обработчик для проверки работоспособности
    @app.get("/health")
    async def health_check() -> Dict[str, Any]:
        """Проверка работоспособности сервиса."""
        return {
            "status": "ok",
            "version": app.version,
        }
    
    # Обработчики событий жизненного цикла приложения
    @app.on_event("startup")
    async def startup_event() -> None:
        """Обработчик запуска приложения."""
        logger.info("Starting ФАЛТ.конф API")
    
    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Обработчик остановки приложения."""
        logger.info("Shutting down ФАЛТ.конф API")
    
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