"""
Протоколы гейтвеев для работы с внешними системами.
"""
from typing import Optional, Protocol

from src.entities.confession import Confession, Poll
from src.entities.enums import ConfessionStatus


class TelegramGatewayProtocol(Protocol):
    """Интерфейс для отправки сообщений в Telegram."""
    
    async def send_confession(self, confession: Confession) -> str:
        """
        Отправляет признание в Telegram канал.
        
        Returns:
            str: ID сообщения в Telegram
        """
        ...
    
    async def send_poll(self, poll: Poll) -> str:
        """
        Отправляет опрос в Telegram канал.
        
        Returns:
            str: ID сообщения с опросом в Telegram
        """
        ...


class ModerationGatewayProtocol(Protocol):
    """Интерфейс для работы с системой модерации."""
    
    async def moderate(self, confession: Confession) -> ConfessionStatus:
        """
        Проводит модерацию признания с помощью LLM или другой системы.
        
        Returns:
            ConfessionStatus: Статус после модерации (APPROVED/REJECTED)
        """
        ...
    
    async def get_moderation_reason(self, confession: Confession) -> Optional[str]:
        """
        Получает причину отклонения признания при модерации.
        
        Returns:
            Optional[str]: Причина отклонения или None, если признание одобрено
        """
        ... 