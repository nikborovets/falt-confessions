"""
Роутеры FastAPI.
"""

from src.frameworks_and_drivers.rest_api.routers.confession import router as confession_router
from src.frameworks_and_drivers.rest_api.routers.poll import router as poll_router

__all__ = ["confession_router", "poll_router"] 