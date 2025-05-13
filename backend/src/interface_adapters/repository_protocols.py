"""
Протоколы репозиториев для работы с данными.
"""
from typing import List, Optional, Protocol

from src.entities.confession import Confession, Poll, Tag
from src.entities.enums import ConfessionStatus


class ConfessionRepositoryProtocol(Protocol):
    """Интерфейс для работы с репозиторием признаний."""

    async def save(self, confession: Confession) -> Confession:
        """Сохраняет признание в репозитории."""
        ...

    async def get_by_id(self, id: int) -> Optional[Confession]:
        """Получает признание по ID."""
        ...

    async def list_by_status(self, status: ConfessionStatus) -> List[Confession]:
        """Получает список признаний по статусу."""
        ...

    async def update_status(self, id: int, status: ConfessionStatus) -> None:
        """Обновляет статус признания."""
        ...


class PollRepositoryProtocol(Protocol):
    """Интерфейс для работы с репозиторием опросов."""

    async def save(self, poll: Poll) -> Poll:
        """Сохраняет опрос в репозитории."""
        ...

    async def get_by_id(self, id: int) -> Optional[Poll]:
        """Получает опрос по ID."""
        ...


class TagRepositoryProtocol(Protocol):
    """Интерфейс для работы с репозиторием тегов."""

    async def get_or_create(self, name: str) -> Tag:
        """Получает существующий тег или создает новый."""
        ...

    async def get_by_names(self, names: List[str]) -> List[Tag]:
        """Получает список тегов по их именам."""
        ... 